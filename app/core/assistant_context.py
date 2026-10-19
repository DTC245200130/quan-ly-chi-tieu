import calendar
from datetime import date, timedelta
from decimal import Decimal

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.finance import compute_available_balance
from app.models.budget import Budget
from app.models.category import Category
from app.models.goal_transaction import GoalTransaction
from app.models.saving_goal import SavingGoal
from app.models.transaction import Transaction


SAFE_CATEGORY_LABELS = {
    "utensils": "Ăn uống",
    "shopping-bag": "Mua sắm",
    "house": "Nhà ở",
    "car": "Di chuyển",
    "bus": "Di chuyển",
    "fuel": "Di chuyển",
    "smartphone": "Liên lạc",
    "receipt": "Hóa đơn",
    "heart-pulse": "Sức khỏe",
    "graduation-cap": "Giáo dục",
    "gamepad-2": "Giải trí",
    "dog": "Thú cưng",
    "baby": "Gia đình",
    "dumbbell": "Sức khỏe",
    "plane": "Du lịch",
    "gift": "Quà tặng",
    "piggy-bank": "Tiết kiệm",
    "banknote": "Thu nhập",
    "briefcase-business": "Thu nhập",
    "trending-up": "Đầu tư",
    "hand-coins": "Thu nhập khác",
    "badge-dollar-sign": "Thu nhập khác",
    "wallet": "Chi tiêu khác",
    "circle-dollar-sign": "Tài chính khác",
}


def month_bounds(year: int, month: int) -> tuple[date, date]:
    start = date(year, month, 1)
    if month == 12:
        return start, date(year + 1, 1, 1)
    return start, date(year, month + 1, 1)


def shift_month(year: int, month: int, offset: int) -> tuple[int, int]:
    absolute_month = year * 12 + month - 1 + offset
    shifted_year, shifted_month = divmod(absolute_month, 12)
    return shifted_year, shifted_month + 1


def change_percentage(current: Decimal, previous: Decimal) -> float | None:
    if previous == 0:
        return 0 if current == 0 else None
    return round(float((current - previous) / previous * Decimal(100)), 1)


def percentage(amount: Decimal, total: Decimal) -> float:
    if total <= 0:
        return 0
    return round(float(amount / total * Decimal(100)), 1)


def _period_totals(
    db: Session,
    user_id: str,
    start: date,
    end: date,
) -> dict[str, Decimal | int]:
    rows = (
        db.query(Transaction.type, func.sum(Transaction.amount), func.count(Transaction.id))
        .filter(
            Transaction.user_id == user_id,
            Transaction.txn_date >= start,
            Transaction.txn_date < end,
        )
        .group_by(Transaction.type)
        .all()
    )
    totals: dict[str, Decimal | int] = {
        "income": Decimal(0),
        "expense": Decimal(0),
        "transaction_count": 0,
    }
    for transaction_type, amount, count in rows:
        if transaction_type in ("income", "expense"):
            totals[transaction_type] = Decimal(amount or 0)
            totals["transaction_count"] = int(totals["transaction_count"]) + int(count or 0)
    return totals


def _category_totals(
    db: Session,
    user_id: str,
    start: date,
    end: date,
) -> dict[str, dict]:
    rows = (
        db.query(
            Category.icon,
            func.sum(Transaction.amount),
            func.count(Transaction.id),
        )
        .join(Transaction, Transaction.category_id == Category.id)
        .filter(
            Category.user_id == user_id,
            Transaction.user_id == user_id,
            Transaction.type == "expense",
            Transaction.txn_date >= start,
            Transaction.txn_date < end,
        )
        .group_by(Category.icon)
        .all()
    )
    return {
        icon or "wallet": {
            "label": SAFE_CATEGORY_LABELS.get(icon or "wallet", "Chi tiêu khác"),
            "icon": icon or "wallet",
            "amount": Decimal(amount or 0),
            "transaction_count": int(count or 0),
        }
        for icon, amount, count in rows
    }


def build_assistant_context(
    db: Session,
    user_id: str,
    month: int,
    year: int,
) -> dict:
    current_start, current_end = month_bounds(year, month)
    previous_year, previous_month = shift_month(year, month, -1)
    previous_start, previous_end = month_bounds(previous_year, previous_month)

    current = _period_totals(db, user_id, current_start, current_end)
    previous = _period_totals(db, user_id, previous_start, previous_end)
    current_income = Decimal(current["income"])
    current_expense = Decimal(current["expense"])
    previous_income = Decimal(previous["income"])
    previous_expense = Decimal(previous["expense"])

    current_categories = _category_totals(db, user_id, current_start, current_end)
    previous_categories = _category_totals(db, user_id, previous_start, previous_end)
    category_keys = set(current_categories) | set(previous_categories)
    categories = []
    for icon in category_keys:
        current_category = current_categories.get(icon)
        previous_category = previous_categories.get(icon)
        category = current_category or previous_category
        current_amount = current_category["amount"] if current_category else Decimal(0)
        previous_amount = previous_category["amount"] if previous_category else Decimal(0)
        categories.append(
            {
                "label": category["label"],
                "icon": category["icon"],
                "current_amount": current_amount,
                "previous_amount": previous_amount,
                "difference": current_amount - previous_amount,
                "current_share": percentage(current_amount, current_expense),
                "current_transaction_count": current_category["transaction_count"] if current_category else 0,
            }
        )
    categories.sort(
        key=lambda item: (item["current_amount"], item["previous_amount"]),
        reverse=True,
    )

    budget_rows = (
        db.query(Budget.category_id, Budget.limit_amount)
        .filter(Budget.user_id == user_id, Budget.month == month, Budget.year == year)
        .all()
    )
    spent_by_category = {
        category_id: Decimal(amount or 0)
        for category_id, amount in (
            db.query(Transaction.category_id, func.sum(Transaction.amount))
            .filter(
                Transaction.user_id == user_id,
                Transaction.type == "expense",
                Transaction.txn_date >= current_start,
                Transaction.txn_date < current_end,
            )
            .group_by(Transaction.category_id)
            .all()
        )
    }
    over_budget_count = sum(
        1
        for category_id, limit_amount in budget_rows
        if spent_by_category.get(category_id, Decimal(0)) > Decimal(limit_amount)
    )

    active_goals = (
        db.query(SavingGoal)
        .filter(SavingGoal.user_id == user_id, SavingGoal.status == "active")
        .all()
    )
    goal_ids = [goal.id for goal in active_goals]
    goal_saved_total = Decimal(0)
    if goal_ids:
        goal_rows = (
            db.query(GoalTransaction.type, func.sum(GoalTransaction.amount))
            .filter(GoalTransaction.goal_id.in_(goal_ids), GoalTransaction.txn_date < current_end)
            .group_by(GoalTransaction.type)
            .all()
        )
        goal_totals = {row_type: Decimal(amount or 0) for row_type, amount in goal_rows}
        goal_saved_total = goal_totals.get("deposit", Decimal(0)) - goal_totals.get("withdraw", Decimal(0))

    today = date.today()
    days_in_month = calendar.monthrange(year, month)[1]
    if (year, month) == (today.year, today.month):
        elapsed_days = today.day
    elif current_end <= today:
        elapsed_days = days_in_month
    else:
        elapsed_days = 1
    average_expense = current_expense / Decimal(max(elapsed_days, 1))
    projected_expense = average_expense * Decimal(days_in_month)
    projected_net = current_income - projected_expense
    through_date = min(current_end - timedelta(days=1), today)

    return {
        "current_period": {"month": month, "year": year},
        "previous_period": {"month": previous_month, "year": previous_year},
        "current": {
            "income": current_income,
            "expense": current_expense,
            "net": current_income - current_expense,
            "transaction_count": int(current["transaction_count"]),
        },
        "previous": {
            "income": previous_income,
            "expense": previous_expense,
            "net": previous_income - previous_expense,
            "transaction_count": int(previous["transaction_count"]),
        },
        "available_balance": compute_available_balance(db, user_id, through_date=through_date),
        "expense_difference": current_expense - previous_expense,
        "expense_change_percentage": change_percentage(current_expense, previous_expense),
        "categories": categories[:7],
        "forecast": {
            "elapsed_days": elapsed_days,
            "days_in_month": days_in_month,
            "average_expense_per_day": average_expense,
            "projected_expense": projected_expense,
            "projected_net": projected_net,
            "confidence": "medium" if int(current["transaction_count"]) >= 7 else "low",
        },
        "active_budget_count": len(budget_rows),
        "over_budget_count": over_budget_count,
        "active_goal_count": len(active_goals),
        "goal_target_total": sum((Decimal(goal.target_amount) for goal in active_goals), Decimal(0)),
        "goal_saved_total": goal_saved_total,
    }
