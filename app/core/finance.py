from sqlalchemy.orm import Session
from sqlalchemy import func
from decimal import Decimal
from datetime import date
from app.models.transaction import Transaction
from app.models.saving_goal import SavingGoal
from app.models.goal_transaction import GoalTransaction

def compute_available_balance(
    db: Session,
    user_id: str,
    through_date: date | None = None,
) -> Decimal:
    income_query = db.query(func.sum(Transaction.amount)).filter(
        Transaction.user_id == user_id,
        Transaction.type == "income",
    )
    expense_query = db.query(func.sum(Transaction.amount)).filter(
        Transaction.user_id == user_id,
        Transaction.type == "expense",
    )
    if through_date is not None:
        income_query = income_query.filter(Transaction.txn_date <= through_date)
        expense_query = expense_query.filter(Transaction.txn_date <= through_date)

    income = income_query.scalar() or Decimal(0)
    expense = expense_query.scalar() or Decimal(0)
    goal_ids = [g.id for g in db.query(SavingGoal.id).filter(SavingGoal.user_id == user_id).all()]
    deposits = Decimal(0)
    withdrawals = Decimal(0)
    if goal_ids:
        deposits_query = db.query(func.sum(GoalTransaction.amount)).filter(
            GoalTransaction.goal_id.in_(goal_ids),
            GoalTransaction.type == "deposit",
        )
        withdrawals_query = db.query(func.sum(GoalTransaction.amount)).filter(
            GoalTransaction.goal_id.in_(goal_ids),
            GoalTransaction.type == "withdraw",
        )
        if through_date is not None:
            deposits_query = deposits_query.filter(GoalTransaction.txn_date <= through_date)
            withdrawals_query = withdrawals_query.filter(GoalTransaction.txn_date <= through_date)
        deposits = deposits_query.scalar() or Decimal(0)
        withdrawals = withdrawals_query.scalar() or Decimal(0)
    return income - expense - deposits + withdrawals
