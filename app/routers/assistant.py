import json
from datetime import date, datetime, timedelta, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.assistant_context import build_assistant_context
from app.core.deps import get_current_user
from app.core.gemini import (
    GeminiNotConfiguredError,
    GeminiRateLimitError,
    GeminiServiceError,
    GeminiTimeoutError,
    GeminiUnavailableError,
    configured_model,
    generate_financial_advice,
)
from app.database import get_db
from app.models.ai_conversation import AIConversation, AIMessage
from app.models.user import User
from app.schemas.assistant import (
    AssistantAskRequest,
    AssistantContextOut,
    AssistantConversationOut,
    AssistantConversationSummary,
    AssistantMessageOut,
    AssistantReplyOut,
)


router = APIRouter(prefix="/assistant", tags=["assistant"])

PRIVACY_NOTES = [
    "Chỉ gửi dữ liệu tổng hợp đã ẩn danh",
    "Không gửi ghi chú hoặc mô tả giao dịch",
    "Không gửi username, email hoặc tên mục tiêu",
    "Gemini không thể thay đổi dữ liệu",
]


def _owned_conversation(db: Session, user_id: str, conversation_id: str) -> AIConversation:
    conversation = (
        db.query(AIConversation)
        .filter(AIConversation.id == conversation_id, AIConversation.user_id == user_id)
        .first()
    )
    if not conversation:
        raise HTTPException(status_code=404, detail="Không tìm thấy cuộc trò chuyện.")
    return conversation


def _message_out(message: AIMessage) -> AssistantMessageOut:
    evidence = json.loads(message.evidence_json) if message.evidence_json else None
    return AssistantMessageOut(
        id=message.id,
        role=message.role,
        content=message.content,
        context_month=message.context_month,
        context_year=message.context_year,
        evidence=evidence,
        created_at=message.created_at,
    )


def _conversation_out(db: Session, conversation: AIConversation) -> AssistantConversationOut:
    messages = (
        db.query(AIMessage)
        .filter(AIMessage.conversation_id == conversation.id)
        .order_by(AIMessage.created_at, AIMessage.id)
        .all()
    )
    return AssistantConversationOut(
        id=conversation.id,
        title=conversation.title,
        preview=messages[-1].content[:120] if messages else "",
        message_count=len(messages),
        created_at=conversation.created_at,
        updated_at=conversation.updated_at,
        messages=[_message_out(message) for message in messages],
    )


@router.get("/context", response_model=AssistantContextOut)
def get_assistant_context(
    month: Optional[int] = Query(default=None, ge=1, le=12),
    year: Optional[int] = Query(default=None, ge=2000, le=2100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    today = date.today()
    selected_month = month or today.month
    selected_year = year or today.year
    evidence = build_assistant_context(db, current_user.id, selected_month, selected_year)
    return AssistantContextOut(
        evidence=evidence,
        has_data=(
            evidence["current"]["transaction_count"] > 0
            or evidence["previous"]["transaction_count"] > 0
        ),
        privacy_notes=PRIVACY_NOTES,
        model=configured_model(),
    )


@router.get("/conversations", response_model=list[AssistantConversationSummary])
def list_conversations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    conversations = (
        db.query(AIConversation)
        .filter(AIConversation.user_id == current_user.id)
        .order_by(AIConversation.updated_at.desc(), AIConversation.created_at.desc())
        .all()
    )
    results = []
    for conversation in conversations:
        message_count = (
            db.query(func.count(AIMessage.id))
            .filter(AIMessage.conversation_id == conversation.id)
            .scalar()
            or 0
        )
        latest = (
            db.query(AIMessage.content)
            .filter(AIMessage.conversation_id == conversation.id)
            .order_by(AIMessage.created_at.desc(), AIMessage.id.desc())
            .first()
        )
        results.append(
            AssistantConversationSummary(
                id=conversation.id,
                title=conversation.title,
                preview=(latest[0][:120] if latest else ""),
                message_count=int(message_count),
                created_at=conversation.created_at,
                updated_at=conversation.updated_at,
            )
        )
    return results


@router.get("/conversations/{conversation_id}", response_model=AssistantConversationOut)
def get_conversation(
    conversation_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return _conversation_out(db, _owned_conversation(db, current_user.id, conversation_id))


@router.delete("/conversations/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_conversation(
    conversation_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    conversation = _owned_conversation(db, current_user.id, conversation_id)
    db.query(AIMessage).filter(AIMessage.conversation_id == conversation.id).delete()
    db.delete(conversation)
    db.commit()


@router.post("/messages", response_model=AssistantReplyOut, status_code=status.HTTP_201_CREATED)
def ask_assistant(
    payload: AssistantAskRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    question = payload.question.strip()
    if not question:
        raise HTTPException(status_code=422, detail="Câu hỏi không được để trống.")

    today = date.today()
    selected_month = payload.month or today.month
    selected_year = payload.year or today.year
    if payload.conversation_id:
        conversation = _owned_conversation(db, current_user.id, payload.conversation_id)
    else:
        title = question[:72] + ("…" if len(question) > 72 else "")
        conversation = AIConversation(user_id=current_user.id, title=title)
        db.add(conversation)
        db.flush()

    prior_messages = (
        db.query(AIMessage)
        .filter(AIMessage.conversation_id == conversation.id)
        .order_by(AIMessage.created_at, AIMessage.id)
        .all()
    )
    evidence = build_assistant_context(db, current_user.id, selected_month, selected_year)
    try:
        answer = generate_financial_advice(
            question,
            evidence,
            ((message.role, message.content) for message in prior_messages),
        )
    except GeminiNotConfiguredError as exc:
        db.rollback()
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except GeminiRateLimitError as exc:
        db.rollback()
        raise HTTPException(status_code=429, detail=str(exc)) from exc
    except GeminiTimeoutError as exc:
        db.rollback()
        raise HTTPException(status_code=504, detail=str(exc)) from exc
    except GeminiUnavailableError as exc:
        db.rollback()
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except GeminiServiceError as exc:
        db.rollback()
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    question_time = datetime.now(timezone.utc)
    db.add_all(
        [
            AIMessage(conversation_id=conversation.id, role="user", content=question, created_at=question_time),
            AIMessage(
                conversation_id=conversation.id,
                role="assistant",
                content=answer,
                context_month=selected_month,
                context_year=selected_year,
                evidence_json=json.dumps(evidence, ensure_ascii=False, default=str),
                created_at=question_time + timedelta(microseconds=1),
            ),
        ]
    )
    conversation.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(conversation)
    return AssistantReplyOut(
        conversation=_conversation_out(db, conversation),
        model=configured_model(),
    )
