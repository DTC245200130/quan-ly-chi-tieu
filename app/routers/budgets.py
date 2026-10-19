from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from decimal import Decimal
from app.database import get_db
from app.models.budget import Budget
from app.models.category import Category
from app.models.transaction import Transaction
from app.models.user import User
from app.schemas.budget import BudgetCreate, BudgetUpdate, BudgetOut
from app.core.deps import get_current_user
import uuid

router = APIRouter(prefix="/budgets", tags=["budgets"])

def compute_spent(db: Session, user_id: str, category_id: str, month: int, year: int) -> Decimal:
    total = db.query(func.sum(Transaction.amount)).filter(
        Transaction.user_id == user_id,
        Transaction.category_id == category_id,
        Transaction.type == "expense",
        func.extract("month", Transaction.txn_date) == month,
        func.extract("year", Transaction.txn_date) == year,
    ).scalar()
    return total or Decimal(0)

def to_budget_out(db: Session, budget: Budget, user_id: str) -> dict:
    spent = compute_spent(db, user_id, budget.category_id, budget.month, budget.year)
    return {
        "id": budget.id, "category_id": budget.category_id, "month": budget.month,
        "year": budget.year, "limit_amount": budget.limit_amount,
        "spent": spent, "is_over": spent > budget.limit_amount,
    }

@router.get("/", response_model=List[BudgetOut])
def list_budgets(month: int = None, year: int = None, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    query = db.query(Budget).filter(Budget.user_id == current_user.id)
    if month: query = query.filter(Budget.month == month)
    if year: query = query.filter(Budget.year == year)
    budgets = query.all()
    return [to_budget_out(db, b, current_user.id) for b in budgets]

@router.post("/", response_model=BudgetOut)
def create_budget(payload: BudgetCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    category = db.query(Category).filter(Category.id == payload.category_id, Category.user_id == current_user.id, Category.type == "expense").first()
    if not category:
        raise HTTPException(status_code=404, detail="Danh mục chi không tồn tại hoặc không thuộc về bạn")

    existing = db.query(Budget).filter(
        Budget.user_id == current_user.id, Budget.category_id == payload.category_id,
        Budget.month == payload.month, Budget.year == payload.year,
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Danh mục này đã có ngân sách cho tháng này")

    budget = Budget(id=str(uuid.uuid4()), user_id=current_user.id, **payload.model_dump())
    db.add(budget)
    db.commit()
    db.refresh(budget)
    return to_budget_out(db, budget, current_user.id)

@router.put("/{budget_id}", response_model=BudgetOut)
def update_budget(budget_id: str, payload: BudgetUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    budget = db.query(Budget).filter(Budget.id == budget_id, Budget.user_id == current_user.id).first()
    if not budget:
        raise HTTPException(status_code=404, detail="Không tìm thấy ngân sách")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(budget, key, value)
    db.commit()
    db.refresh(budget)
    return to_budget_out(db, budget, current_user.id)

@router.delete("/{budget_id}")
def delete_budget(budget_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    budget = db.query(Budget).filter(Budget.id == budget_id, Budget.user_id == current_user.id).first()
    if not budget:
        raise HTTPException(status_code=404, detail="Không tìm thấy ngân sách")
    db.delete(budget)
    db.commit()
    return {"message": "Đã xóa ngân sách"}
