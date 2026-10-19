import unittest
from datetime import date
from decimal import Decimal

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.models.budget import Budget
from app.models.category import Category
from app.models.goal_transaction import GoalTransaction
from app.models.saving_goal import SavingGoal
from app.models.transaction import Transaction
from app.models.user import User
from app.routers.dashboard import get_dashboard


class DashboardApiTest(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        session = sessionmaker(bind=self.engine)
        self.db = session()

        self.user = User(id="user-1", username="demo", email="demo@example.com", password_hash="test")
        other_user = User(id="user-2", username="other", email="other@example.com", password_hash="test")
        salary = Category(
            id="salary",
            user_id=self.user.id,
            name="Lương",
            type="income",
            color="#2563eb",
            icon="briefcase-business",
        )
        food = Category(
            id="food",
            user_id=self.user.id,
            name="Ăn uống",
            type="expense",
            color="#07845c",
            icon="utensils",
        )
        transport = Category(
            id="transport",
            user_id=self.user.id,
            name="Đi lại",
            type="expense",
            color="#f29b00",
            icon="bus",
        )
        other_category = Category(
            id="other-income",
            user_id=other_user.id,
            name="Dữ liệu người khác",
            type="income",
            color="#000000",
        )
        self.db.add_all([self.user, other_user, salary, food, transport, other_category])
        self.db.add_all(
            [
                Transaction(id="jun-income", user_id=self.user.id, category_id=salary.id, amount=10_000, type="income", txn_date=date(2026, 6, 1)),
                Transaction(id="jun-expense", user_id=self.user.id, category_id=food.id, amount=1_000, type="expense", txn_date=date(2026, 6, 5)),
                Transaction(id="jul-income", user_id=self.user.id, category_id=salary.id, amount=12_000, type="income", txn_date=date(2026, 7, 1)),
                Transaction(id="jul-expense", user_id=self.user.id, category_id=transport.id, amount=2_000, type="expense", txn_date=date(2026, 7, 8)),
                Transaction(id="aug-income", user_id=self.user.id, category_id=salary.id, amount=15_000, type="income", txn_date=date(2026, 8, 1), note="Lương tháng 8"),
                Transaction(id="aug-food", user_id=self.user.id, category_id=food.id, amount=3_000, type="expense", txn_date=date(2026, 8, 10)),
                Transaction(id="aug-transport", user_id=self.user.id, category_id=transport.id, amount=1_000, type="expense", txn_date=date(2026, 8, 15)),
                Transaction(id="future-income", user_id=self.user.id, category_id=salary.id, amount=999_000, type="income", txn_date=date(2026, 9, 1)),
                Transaction(id="other-user-income", user_id=other_user.id, category_id=other_category.id, amount=5_000_000, type="income", txn_date=date(2026, 8, 1)),
            ]
        )
        self.db.add_all(
            [
                Budget(id="food-budget", user_id=self.user.id, category_id=food.id, month=8, year=2026, limit_amount=5_000),
                Budget(id="transport-budget", user_id=self.user.id, category_id=transport.id, month=8, year=2026, limit_amount=1_000),
            ]
        )
        goal = SavingGoal(
            id="goal-1",
            user_id=self.user.id,
            name="Quỹ dự phòng",
            target_amount=10_000,
            deadline=date(2026, 12, 31),
            status="active",
        )
        self.db.add(goal)
        self.db.add_all(
            [
                GoalTransaction(id="goal-deposit", goal_id=goal.id, amount=4_000, type="deposit", txn_date=date(2026, 7, 20)),
                GoalTransaction(id="goal-withdraw", goal_id=goal.id, amount=1_000, type="withdraw", txn_date=date(2026, 8, 20)),
                GoalTransaction(id="future-goal-deposit", goal_id=goal.id, amount=10_000, type="deposit", txn_date=date(2026, 9, 2)),
            ]
        )
        self.db.commit()

    def tearDown(self):
        self.db.close()
        self.engine.dispose()

    def test_dashboard_aggregates_selected_month_and_scopes_user(self):
        result = get_dashboard(month=8, year=2026, db=self.db, current_user=self.user)

        self.assertEqual(result.summary.income, Decimal("15000.00"))
        self.assertEqual(result.summary.expense, Decimal("4000.00"))
        self.assertEqual(result.summary.net, Decimal("11000.00"))
        self.assertEqual(result.summary.available_balance, Decimal("27000.00"))

        self.assertEqual([point.month for point in result.trend], [6, 7, 8])
        self.assertEqual(result.trend[0].income, Decimal("10000.00"))
        self.assertEqual(result.trend[1].expense, Decimal("2000.00"))
        self.assertEqual(result.trend[2].expense, Decimal("4000.00"))

        spending = {item.category_id: item for item in result.spending_by_category}
        self.assertEqual(spending["food"].amount, Decimal("3000.00"))
        self.assertEqual(spending["food"].percentage, 75.0)
        self.assertEqual(spending["food"].icon, "utensils")
        self.assertEqual(spending["transport"].percentage, 25.0)

        budgets = {item.category_id: item for item in result.budgets}
        self.assertEqual(budgets["food"].spent, Decimal("3000.00"))
        self.assertEqual(budgets["food"].status, "safe")
        self.assertEqual(budgets["food"].icon, "utensils")
        self.assertEqual(budgets["transport"].status, "warning")

        self.assertEqual(result.goals[0].current_amount, Decimal("3000.00"))
        self.assertEqual(result.goals[0].progress_percentage, 30.0)
        self.assertEqual(len(result.recent_transactions), 3)
        self.assertEqual(result.recent_transactions[0].category_icon, "bus")
        self.assertNotIn("other-income", {item.category_id for item in result.recent_transactions})

    def test_dashboard_returns_zeroes_for_month_without_data(self):
        result = get_dashboard(month=5, year=2026, db=self.db, current_user=self.user)

        self.assertEqual(result.summary.income, Decimal(0))
        self.assertEqual(result.summary.expense, Decimal(0))
        self.assertEqual(result.summary.net, Decimal(0))
        self.assertEqual(result.spending_by_category, [])
        self.assertEqual(result.budgets, [])
        self.assertEqual(result.recent_transactions, [])
        self.assertEqual(len(result.trend), 3)


if __name__ == "__main__":
    unittest.main()
