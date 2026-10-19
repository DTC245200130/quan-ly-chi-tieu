import hashlib
import secrets
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.ai_conversation import AIConversation, AIMessage
from app.models.budget import Budget
from app.models.category import Category
from app.models.goal_item import GoalItem
from app.models.goal_transaction import GoalTransaction
from app.models.saving_goal import SavingGoal
from app.models.transaction import Transaction
from app.schemas.user import (
    UserRegister,
    UserOut,
    UserProfileUpdate,
    ChangePasswordRequest,
    DeleteAccountRequest,
    Token,
    ForgotPasswordRequest,
    ResetPasswordRequest,
    MessageResponse,
)
from app.core.security import hash_password, verify_password, create_access_token
from app.core.normalization import canonicalize_identity, normalize_identity
from app.core.deps import get_current_user
from app.core.email import send_reset_password_email

router = APIRouter(prefix="/auth", tags=["auth"])

RESET_TOKEN_EXPIRE_MINUTES = 15

# Rate limit đơn giản trong bộ nhớ: tối đa 3 lần yêu cầu / email / giờ.
# Đủ dùng cho quy mô đồ án; nếu deploy thật lâu dài nên thay bằng Redis.
_reset_request_log: dict[str, list[datetime]] = defaultdict(list)
RESET_RATE_LIMIT_MAX = 3
RESET_RATE_LIMIT_WINDOW = timedelta(hours=1)
AVATAR_MAX_BYTES = 2 * 1024 * 1024
AVATAR_DIRECTORY = Path(__file__).resolve().parents[2] / "uploads" / "avatars"
AVATAR_DIRECTORY.mkdir(parents=True, exist_ok=True)
AVATAR_FORMATS = {
    "image/jpeg": ("jpg", lambda data: data.startswith(b"\xff\xd8\xff")),
    "image/png": ("png", lambda data: data.startswith(b"\x89PNG\r\n\x1a\n")),
    "image/webp": ("webp", lambda data: len(data) >= 12 and data[:4] == b"RIFF" and data[8:12] == b"WEBP"),
}


def _hash_token(raw_token: str) -> str:
    return hashlib.sha256(raw_token.encode()).hexdigest()


def _is_rate_limited(email: str) -> bool:
    now = datetime.now(timezone.utc)
    recent = [t for t in _reset_request_log[email] if now - t < RESET_RATE_LIMIT_WINDOW]
    _reset_request_log[email] = recent
    return len(recent) >= RESET_RATE_LIMIT_MAX


def _remove_local_avatar(avatar_url: str | None) -> None:
    if not avatar_url or not avatar_url.startswith("/uploads/avatars/"):
        return
    target = AVATAR_DIRECTORY / Path(avatar_url).name
    target.unlink(missing_ok=True)

@router.post("/register", response_model=UserOut)
def register(payload: UserRegister, db: Session = Depends(get_db)):
    username = canonicalize_identity(payload.username)
    username_normalized = normalize_identity(username)
    email = normalize_identity(str(payload.email))
    email_normalized = email
    if len(username) < 3:
        raise HTTPException(status_code=400, detail="Tên đăng nhập phải có ít nhất 3 ký tự.")

    existing_username = db.query(User).filter(User.username_normalized == username_normalized).first()
    if existing_username:
        raise HTTPException(status_code=400, detail="Tên đăng nhập đã tồn tại.")

    existing_email = db.query(User).filter(User.email_normalized == email_normalized).first()
    if existing_email:
        raise HTTPException(status_code=400, detail="Email đã được sử dụng.")

    user = User(
        username=username,
        email=email,
        password_hash=hash_password(payload.password),
    )
    db.add(user)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=400, detail="Tên đăng nhập hoặc email đã được sử dụng.") from exc
    db.refresh(user)
    return user

@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    identifier = normalize_identity(form_data.username)
    user = db.query(User).filter(
        (User.username_normalized == identifier) | (User.email_normalized == identifier)
    ).first()
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Tên đăng nhập, email hoặc mật khẩu không đúng.",
        )
    token = create_access_token({"sub": user.id})
    return {"access_token": token, "token_type": "bearer"}

@router.get("/me", response_model=UserOut)
def me(current_user: User = Depends(get_current_user)):
    return current_user


@router.put("/me", response_model=UserOut)
def update_profile(
    payload: UserProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    username = canonicalize_identity(payload.username)
    username_normalized = normalize_identity(username)
    email = normalize_identity(str(payload.email))
    email_normalized = email
    display_name = (payload.display_name or "").strip() or None

    if len(username) < 3:
        raise HTTPException(status_code=400, detail="Tên đăng nhập phải có ít nhất 3 ký tự.")

    username_owner = (
        db.query(User)
        .filter(User.username_normalized == username_normalized, User.id != current_user.id)
        .first()
    )
    if username_owner:
        raise HTTPException(status_code=400, detail="Tên đăng nhập đã tồn tại.")

    email_owner = (
        db.query(User)
        .filter(User.email_normalized == email_normalized, User.id != current_user.id)
        .first()
    )
    if email_owner:
        raise HTTPException(status_code=400, detail="Email đã được sử dụng.")

    email_changed = current_user.email_normalized != email_normalized
    current_user.display_name = display_name
    current_user.username = username
    current_user.email = email
    if email_changed:
        current_user.reset_token_hash = None
        current_user.reset_token_expiry = None
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=400, detail="Tên đăng nhập hoặc email đã được sử dụng.") from exc
    db.refresh(current_user)
    return current_user


@router.put("/me/password", response_model=MessageResponse)
def change_password(
    payload: ChangePasswordRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not verify_password(payload.current_password, current_user.password_hash):
        raise HTTPException(status_code=400, detail="Mật khẩu hiện tại không đúng.")

    current_user.password_hash = hash_password(payload.new_password)
    try:
        db.commit()
    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Không thể đổi mật khẩu. Vui lòng thử lại.",
        ) from exc

    return MessageResponse(message="Đổi mật khẩu thành công.")


@router.delete("/me", response_model=MessageResponse)
def delete_account(
    payload: DeleteAccountRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not verify_password(payload.current_password, current_user.password_hash):
        raise HTTPException(status_code=400, detail="Mật khẩu hiện tại không đúng.")

    user_id = current_user.id
    previous_avatar = current_user.avatar_url
    goal_ids = db.query(SavingGoal.id).filter(SavingGoal.user_id == user_id)
    conversation_ids = db.query(AIConversation.id).filter(AIConversation.user_id == user_id)

    try:
        db.query(AIMessage).filter(AIMessage.conversation_id.in_(conversation_ids)).delete(
            synchronize_session=False
        )
        db.query(AIConversation).filter(AIConversation.user_id == user_id).delete(
            synchronize_session=False
        )
        db.query(GoalItem).filter(GoalItem.goal_id.in_(goal_ids)).delete(synchronize_session=False)
        db.query(GoalTransaction).filter(GoalTransaction.goal_id.in_(goal_ids)).delete(
            synchronize_session=False
        )
        db.query(SavingGoal).filter(SavingGoal.user_id == user_id).delete(synchronize_session=False)
        db.query(Budget).filter(Budget.user_id == user_id).delete(synchronize_session=False)
        db.query(Transaction).filter(Transaction.user_id == user_id).delete(synchronize_session=False)
        db.query(Category).filter(Category.user_id == user_id).delete(synchronize_session=False)
        db.delete(current_user)
        db.commit()
    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Không thể xóa tài khoản. Dữ liệu của bạn chưa bị thay đổi.",
        ) from exc

    try:
        _remove_local_avatar(previous_avatar)
    except OSError:
        pass
    return MessageResponse(message="Tài khoản và dữ liệu cá nhân đã được xóa.")


@router.post("/me/avatar", response_model=UserOut)
def upload_avatar(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    avatar_format = AVATAR_FORMATS.get(file.content_type or "")
    if not avatar_format:
        raise HTTPException(status_code=415, detail="Ảnh đại diện phải là tệp PNG, JPEG hoặc WebP.")

    content = file.file.read(AVATAR_MAX_BYTES + 1)
    file.file.close()
    if not content:
        raise HTTPException(status_code=400, detail="Tệp ảnh đại diện đang trống.")
    if len(content) > AVATAR_MAX_BYTES:
        raise HTTPException(status_code=413, detail="Ảnh đại diện không được vượt quá 2 MB.")

    extension, matches_signature = avatar_format
    if not matches_signature(content):
        raise HTTPException(status_code=415, detail="Nội dung tệp không khớp với định dạng ảnh đã chọn.")

    filename = f"{current_user.id}-{secrets.token_hex(6)}.{extension}"
    destination = AVATAR_DIRECTORY / filename
    destination.write_bytes(content)
    previous_avatar = current_user.avatar_url
    current_user.avatar_url = f"/uploads/avatars/{filename}"
    try:
        db.commit()
    except Exception:
        db.rollback()
        destination.unlink(missing_ok=True)
        raise
    db.refresh(current_user)
    _remove_local_avatar(previous_avatar)
    return current_user


@router.delete("/me/avatar", response_model=UserOut)
def delete_avatar(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    previous_avatar = current_user.avatar_url
    current_user.avatar_url = None
    db.commit()
    db.refresh(current_user)
    _remove_local_avatar(previous_avatar)
    return current_user

@router.post("/forgot-password", response_model=MessageResponse)
def forgot_password(payload: ForgotPasswordRequest, db: Session = Depends(get_db)):
    email = normalize_identity(str(payload.email))
    generic_response = MessageResponse(
        message="Nếu email tồn tại trong hệ thống, một liên kết đặt lại mật khẩu đã được gửi."
    )

    if _is_rate_limited(email):
        # Vẫn trả về thông báo chung, chỉ không gửi email nữa
        return generic_response

    user = db.query(User).filter(User.email_normalized == email).first()
    if not user:
        # Không tiết lộ email có tồn tại hay không (chống user enumeration)
        return generic_response

    raw_token = secrets.token_urlsafe(32)
    user.reset_token_hash = _hash_token(raw_token)
    user.reset_token_expiry = datetime.now(timezone.utc) + timedelta(minutes=RESET_TOKEN_EXPIRE_MINUTES)
    db.commit()

    _reset_request_log[email].append(datetime.now(timezone.utc))
    send_reset_password_email(email, raw_token)

    return generic_response

@router.post("/reset-password", response_model=MessageResponse)
def reset_password(payload: ResetPasswordRequest, db: Session = Depends(get_db)):
    token_hash = _hash_token(payload.token)
    user = db.query(User).filter(User.reset_token_hash == token_hash).first()

    if not user or not user.reset_token_expiry:
        raise HTTPException(status_code=400, detail="Liên kết đặt lại mật khẩu không hợp lệ.")

    expiry = user.reset_token_expiry
    if expiry.tzinfo is None:
        expiry = expiry.replace(tzinfo=timezone.utc)

    if expiry < datetime.now(timezone.utc):
        raise HTTPException(status_code=400, detail="Liên kết đặt lại mật khẩu đã hết hạn.")

    user.password_hash = hash_password(payload.new_password)

    # Vô hiệu hóa token ngay sau khi dùng — đảm bảo chỉ dùng được một lần
    user.reset_token_hash = None
    user.reset_token_expiry = None
    db.commit()

    return MessageResponse(message="Đặt lại mật khẩu thành công. Vui lòng đăng nhập lại.")
