from datetime import date
from decimal import Decimal
from typing import List
import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.core.finance import compute_available_balance
from app.database import get_db
from app.models.category import Category
from app.models.goal_item import GoalItem
from app.models.goal_transaction import GoalTransaction
from app.models.saving_goal import SavingGoal
from app.models.transaction import Transaction
from app.models.user import User
from app.schemas.goal import (
    GoalCompleteRequest,
    GoalCreate,
    GoalItemCreate,
    GoalItemUpdate,
    GoalOut,
    GoalTransactionOut,
    GoalTxCreate,
    GoalUpdate,
)

router = APIRouter(prefix="/goals", tags=["goals"])

def compute_current(db: Session, goal_id: str) -> Decimal:
    deposits = db.query(func.sum(GoalTransaction.amount)).filter(GoalTransaction.goal_id == goal_id, GoalTransaction.type == "deposit").scalar() or Decimal(0)
    withdrawals = db.query(func.sum(GoalTransaction.amount)).filter(GoalTransaction.goal_id == goal_id, GoalTransaction.type == "withdraw").scalar() or Decimal(0)
    return deposits - withdrawals


def get_owned_goal(db: Session, goal_id: str, user_id: str) -> SavingGoal:
    goal = db.query(SavingGoal).filter(
        SavingGoal.id == goal_id,
        SavingGoal.user_id == user_id,
    ).first()
    if not goal:
        raise HTTPException(status_code=404, detail="Không tìm thấy mục tiêu")
    return goal

def to_goal_out(db: Session, goal: SavingGoal) -> dict:
    items = db.query(GoalItem).filter(GoalItem.goal_id == goal.id).order_by(GoalItem.id).all()
    return {
        "id": goal.id, "name": goal.name, "target_amount": goal.target_amount,
        "deadline": goal.deadline, "status": goal.status,
        "current_amount": compute_current(db, goal.id),
        "completion_amount": goal.completion_amount,
        "completion_mode": goal.completion_mode,
        "items": items,
    }

@router.get("/", response_model=List[GoalOut])
def list_goals(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    goals = (
        db.query(SavingGoal)
        .filter(SavingGoal.user_id == current_user.id)
        .order_by(
            SavingGoal.status != "active",
            SavingGoal.deadline.is_(None),
            SavingGoal.deadline,
            SavingGoal.name,
        )
        .all()
    )
    return [to_goal_out(db, g) for g in goals]

@router.post("/", response_model=GoalOut)
def create_goal(payload: GoalCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    goal = SavingGoal(id=str(uuid.uuid4()), user_id=current_user.id, status="active", **payload.model_dump())
    db.add(goal)
    db.commit()
    db.refresh(goal)
    return to_goal_out(db, goal)


@router.patch("/{goal_id}", response_model=GoalOut)
def update_goal(
    goal_id: str,
    payload: GoalUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    goal = get_owned_goal(db, goal_id, current_user.id)
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(goal, key, value)
    db.commit()
    db.refresh(goal)
    return to_goal_out(db, goal)

@router.delete("/{goal_id}")
def delete_goal(goal_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    goal = get_owned_goal(db, goal_id, current_user.id)
    transaction_count = db.query(GoalTransaction).filter(GoalTransaction.goal_id == goal_id).count()
    if transaction_count > 0:
        raise HTTPException(
            status_code=409,
            detail="Không thể xóa mục tiêu đã có lịch sử tiền. Hãy giữ mục tiêu để bảo toàn nhật ký tài chính.",
        )
    db.query(GoalItem).filter(GoalItem.goal_id == goal_id).delete()
    db.delete(goal)
    db.commit()
    return {"message": "Đã xóa mục tiêu"}


@router.get("/{goal_id}/transactions", response_model=List[GoalTransactionOut])
def list_goal_transactions(
    goal_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    get_owned_goal(db, goal_id, current_user.id)
    return (
        db.query(GoalTransaction)
        .filter(GoalTransaction.goal_id == goal_id)
        .order_by(GoalTransaction.txn_date.desc(), GoalTransaction.id.desc())
        .all()
    )

@router.post("/{goal_id}/items", response_model=GoalOut)
def add_item(goal_id: str, payload: GoalItemCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    goal = get_owned_goal(db, goal_id, current_user.id)
    item = GoalItem(id=str(uuid.uuid4()), goal_id=goal_id, **payload.model_dump())
    db.add(item)
    db.commit()
    return to_goal_out(db, goal)

@router.post("/{goal_id}/deposit", response_model=GoalOut)
def deposit(goal_id: str, payload: GoalTxCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    goal = get_owned_goal(db, goal_id, current_user.id)
    if goal.status != "active":
        raise HTTPException(status_code=400, detail="Mục tiêu đã hoàn thành, không thể nạp thêm tiền")

    balance = compute_available_balance(db, current_user.id)
    if payload.amount > balance:
        raise HTTPException(status_code=400, detail=f"Không thể nạp quá số dư khả dụng hiện có ({balance})")

    tx = GoalTransaction(id=str(uuid.uuid4()), goal_id=goal_id, amount=payload.amount, type="deposit", txn_date=date.today(), note=payload.note)
    db.add(tx)
    db.commit()
    return to_goal_out(db, goal)

@router.post("/{goal_id}/withdraw", response_model=GoalOut)
def withdraw(goal_id: str, payload: GoalTxCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    goal = get_owned_goal(db, goal_id, current_user.id)
    current = compute_current(db, goal_id)
    if payload.amount > current:
        raise HTTPException(status_code=400, detail=f"Không thể rút quá số đã tiết kiệm ({current})")
    tx = GoalTransaction(id=str(uuid.uuid4()), goal_id=goal_id, amount=payload.amount, type="withdraw", txn_date=date.today(), note=payload.note)
    db.add(tx)
    db.commit()
    return to_goal_out(db, goal)

@router.post("/{goal_id}/complete", response_model=GoalOut)
def complete_goal(
    goal_id: str,
    payload: GoalCompleteRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    goal = get_owned_goal(db, goal_id, current_user.id)
    if goal.status == "completed":
        raise HTTPException(status_code=400, detail="Mục tiêu đã được hoàn thành")

    current = compute_current(db, goal_id)
    if current < goal.target_amount:
        raise HTTPException(status_code=400, detail="Chưa đạt mốc mục tiêu, không thể hoàn thành")

    if payload.mode == "spend":
        if not payload.category_id:
            raise HTTPException(status_code=400, detail="Hãy chọn danh mục chi tiêu")
        category = db.query(Category).filter(
            Category.id == payload.category_id,
            Category.user_id == current_user.id,
            Category.type == "expense",
        ).first()
        if not category:
            raise HTTPException(status_code=404, detail="Danh mục chi tiêu không tồn tại hoặc không thuộc về bạn")
        db.add(Transaction(
            id=str(uuid.uuid4()),
            user_id=current_user.id,
            category_id=category.id,
            amount=current,
            type="expense",
            txn_date=date.today(),
            note=payload.note or f"Sử dụng tiền cho mục tiêu: {goal.name}",
        ))

    goal.completion_amount = current
    goal.completion_mode = payload.mode

    if payload.mode in {"release", "spend"}:
        note = payload.note or (
            "Hoàn thành mục tiêu — chuyển về số dư"
            if payload.mode == "release"
            else "Hoàn thành mục tiêu — ghi nhận đã sử dụng"
        )
        db.add(GoalTransaction(
            id=str(uuid.uuid4()),
            goal_id=goal_id,
            amount=current,
            type="withdraw",
            txn_date=date.today(),
            note=note,
        ))
    goal.status = "completed"
    db.commit()
    db.refresh(goal)
    return to_goal_out(db, goal)

@router.patch("/{goal_id}/items/{item_id}", response_model=GoalOut)
def update_item(goal_id: str, item_id: str, payload: GoalItemUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    goal = get_owned_goal(db, goal_id, current_user.id)
    item = db.query(GoalItem).filter(GoalItem.id == item_id, GoalItem.goal_id == goal_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Không tìm thấy hạng mục")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(item, key, value)
    db.commit()
    return to_goal_out(db, goal)

@router.delete("/{goal_id}/items/{item_id}", response_model=GoalOut)
def delete_item(goal_id: str, item_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    goal = get_owned_goal(db, goal_id, current_user.id)
    item = db.query(GoalItem).filter(GoalItem.id == item_id, GoalItem.goal_id == goal_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Không tìm thấy hạng mục")
    db.delete(item)
    db.commit()
    return to_goal_out(db, goal)
