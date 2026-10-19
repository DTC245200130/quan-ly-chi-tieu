import unittest
from datetime import date
from decimal import Decimal

from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.models.category import Category
from app.models.goal_transaction import GoalTransaction
from app.models.saving_goal import SavingGoal
from app.models.transaction import Transaction
from app.models.user import User
from app.routers.goals import complete_goal, delete_goal, list_goal_transactions, update_goal
from app.schemas.goal import GoalCompleteRequest, GoalUpdate


class GoalsApiTest(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        self.db = sessionmaker(bind=self.engine)()
        self.user = User(id="user-1", username="demo", email="demo@example.com", password_hash="test")
        self.expense_category = Category(
            id="travel",
            user_id=self.user.id,
            name="Du lịch",
            type="expense",
            color="#07845c",
            icon="plane",
        )
        self.db.add_all([self.user, self.expense_category])
        self.db.commit()

    def tearDown(self):
        self.db.close()
        self.engine.dispose()

    def add_goal(self, goal_id: str, amount: Decimal = Decimal("1000")) -> SavingGoal:
        goal = SavingGoal(
            id=goal_id,
            user_id=self.user.id,
            name="Mục tiêu thử nghiệm",
            target_amount=amount,
            deadline=date(2026, 12, 31),
            status="active",
        )
        self.db.add(goal)
        self.db.add(GoalTransaction(
            id=f"{goal_id}-deposit",
            goal_id=goal_id,
            amount=amount,
            type="deposit",
            txn_date=date(2026, 8, 30),
            note="Nạp đủ mục tiêu",
        ))
        self.db.commit()
        return goal

    def test_update_goal_supports_editing_core_fields(self):
        goal = self.add_goal("edit-goal")

        result = update_goal(
            goal.id,
            GoalUpdate(name="Laptop mới", target_amount=Decimal("2500"), deadline=None),
            db=self.db,
            current_user=self.user,
        )

        self.assertEqual(result["name"], "Laptop mới")
        self.assertEqual(result["target_amount"], Decimal("2500"))
        self.assertIsNone(result["deadline"])
        self.assertEqual(result["current_amount"], Decimal("1000"))

    def test_complete_keep_preserves_earmarked_money(self):
        goal = self.add_goal("keep-goal")

        result = complete_goal(
            goal.id,
            GoalCompleteRequest(mode="keep"),
            db=self.db,
            current_user=self.user,
        )

        self.assertEqual(result["status"], "completed")
        self.assertEqual(result["current_amount"], Decimal("1000"))
        self.assertEqual(result["completion_amount"], Decimal("1000"))
        self.assertEqual(result["completion_mode"], "keep")
        self.assertEqual(
            self.db.query(GoalTransaction).filter(GoalTransaction.goal_id == goal.id).count(),
            1,
        )

    def test_complete_release_returns_money_to_available_balance(self):
        goal = self.add_goal("release-goal")

        result = complete_goal(
            goal.id,
            GoalCompleteRequest(mode="release"),
            db=self.db,
            current_user=self.user,
        )

        self.assertEqual(result["status"], "completed")
        self.assertEqual(result["current_amount"], Decimal("0"))
        self.assertEqual(result["completion_amount"], Decimal("1000"))
        self.assertEqual(result["completion_mode"], "release")
        withdrawal = self.db.query(GoalTransaction).filter(
            GoalTransaction.goal_id == goal.id,
            GoalTransaction.type == "withdraw",
        ).one()
        self.assertEqual(withdrawal.amount, Decimal("1000"))

    def test_complete_spend_creates_expense_and_balancing_withdrawal(self):
        goal = self.add_goal("spend-goal")

        result = complete_goal(
            goal.id,
            GoalCompleteRequest(mode="spend", category_id=self.expense_category.id),
            db=self.db,
            current_user=self.user,
        )

        self.assertEqual(result["status"], "completed")
        self.assertEqual(result["current_amount"], Decimal("0"))
        self.assertEqual(result["completion_amount"], Decimal("1000"))
        self.assertEqual(result["completion_mode"], "spend")
        expense = self.db.query(Transaction).filter(Transaction.user_id == self.user.id).one()
        self.assertEqual(expense.type, "expense")
        self.assertEqual(expense.category_id, self.expense_category.id)
        self.assertEqual(expense.amount, Decimal("1000"))

    def test_transaction_history_is_scoped_to_owned_goal(self):
        goal = self.add_goal("history-goal")

        result = list_goal_transactions(goal.id, db=self.db, current_user=self.user)

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].note, "Nạp đủ mục tiêu")

    def test_goal_with_money_history_cannot_be_deleted(self):
        goal = self.add_goal("protected-goal")

        with self.assertRaises(HTTPException) as context:
            delete_goal(goal.id, db=self.db, current_user=self.user)

        self.assertEqual(context.exception.status_code, 409)
        self.assertIsNotNone(self.db.query(SavingGoal).filter(SavingGoal.id == goal.id).first())


if __name__ == "__main__":
    unittest.main()
