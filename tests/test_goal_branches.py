import unittest
from datetime import date
from decimal import Decimal

from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.models.category import Category
from app.models.goal_item import GoalItem
from app.models.goal_transaction import GoalTransaction
from app.models.saving_goal import SavingGoal
from app.models.transaction import Transaction
from app.models.user import User
from app.routers.goals import (
    add_item,
    complete_goal,
    create_goal,
    delete_goal,
    delete_item,
    deposit,
    get_owned_goal,
    list_goals,
    update_item,
    withdraw,
)
from app.schemas.goal import (
    GoalCompleteRequest,
    GoalCreate,
    GoalItemCreate,
    GoalItemUpdate,
    GoalTxCreate,
)


class GoalBranchTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        self.db = sessionmaker(bind=self.engine)()
        self.user = User(id="u1", username="owner", email="owner@example.com", password_hash="x")
        self.other = User(id="u2", username="other", email="other@example.com", password_hash="x")
        self.expense = Category(
            id="expense", user_id=self.user.id, name="Chi", type="expense",
            color="#000", icon="wallet",
        )
        self.income = Category(
            id="income", user_id=self.user.id, name="Thu", type="income",
            color="#111", icon="banknote",
        )
        self.other_expense = Category(
            id="other-expense", user_id=self.other.id, name="Khác", type="expense",
            color="#222", icon="wallet",
        )
        self.db.add_all([self.user, self.other, self.expense, self.income, self.other_expense])
        self.db.add(Transaction(
            id="salary", user_id=self.user.id, category_id=self.income.id,
            amount=Decimal("1000"), type="income", txn_date=date.today(),
        ))
        self.db.commit()

    def tearDown(self):
        self.db.close()
        self.engine.dispose()

    def goal(self, goal_id, target=Decimal("100"), status="active", saved=Decimal("0")):
        goal = SavingGoal(
            id=goal_id, user_id=self.user.id, name=goal_id,
            target_amount=target, deadline=None, status=status,
        )
        self.db.add(goal)
        if saved:
            self.db.add(GoalTransaction(
                id=f"{goal_id}-deposit", goal_id=goal_id, amount=saved,
                type="deposit", txn_date=date.today(),
            ))
        self.db.commit()
        return goal

    def assert_error(self, code, fn, *args):
        with self.assertRaises(HTTPException) as caught:
            fn(*args, db=self.db, current_user=self.user)
        self.assertEqual(caught.exception.status_code, code)

    def test_create_list_ownership_and_delete_clean_goal(self):
        other_goal = SavingGoal(
            id="other-goal", user_id=self.other.id, name="Other",
            target_amount=10, status="active",
        )
        self.db.add(other_goal)
        self.db.commit()
        with self.assertRaises(HTTPException):
            get_owned_goal(self.db, other_goal.id, self.user.id)

        created = create_goal(GoalCreate(name="  Quỹ mới ", target_amount=250), self.db, self.user)
        self.assertEqual(created["name"], "Quỹ mới")
        self.assertEqual([goal["id"] for goal in list_goals(self.db, self.user)], [created["id"]])

        self.db.add(GoalItem(id="orphanable", goal_id=created["id"], name="Item", cost=10))
        self.db.commit()
        self.assertEqual(delete_goal(created["id"], self.db, self.user), {"message": "Đã xóa mục tiêu"})
        self.assertIsNone(self.db.query(GoalItem).filter_by(id="orphanable").first())

    def test_item_crud_and_missing_item_branches(self):
        goal = self.goal("items")
        result = add_item(goal.id, GoalItemCreate(name="  Laptop  ", cost=80), self.db, self.user)
        item_id = result["items"][0].id
        result = update_item(
            goal.id, item_id, GoalItemUpdate(cost=90, is_purchased=True), self.db, self.user
        )
        self.assertEqual(result["items"][0].cost, Decimal("90"))
        self.assertTrue(result["items"][0].is_purchased)
        self.assert_error(404, update_item, goal.id, "missing", GoalItemUpdate(cost=1))
        self.assert_error(404, delete_item, goal.id, "missing")
        self.assertEqual(delete_item(goal.id, item_id, self.db, self.user)["items"], [])

    def test_deposit_and_withdraw_boundaries(self):
        inactive = self.goal("inactive", status="completed")
        self.assert_error(400, deposit, inactive.id, GoalTxCreate(amount=1))

        goal = self.goal("money")
        self.assert_error(400, deposit, goal.id, GoalTxCreate(amount=1001))
        deposited = deposit(goal.id, GoalTxCreate(amount=300, note="save"), self.db, self.user)
        self.assertEqual(deposited["current_amount"], Decimal("300"))
        self.assert_error(400, withdraw, goal.id, GoalTxCreate(amount=301))
        withdrawn = withdraw(goal.id, GoalTxCreate(amount=125, note="need"), self.db, self.user)
        self.assertEqual(withdrawn["current_amount"], Decimal("175"))

    def test_complete_rejects_invalid_states_and_spend_categories(self):
        completed = self.goal("completed", status="completed", saved=100)
        self.assert_error(400, complete_goal, completed.id, GoalCompleteRequest())

        incomplete = self.goal("incomplete", target=200, saved=100)
        self.assert_error(400, complete_goal, incomplete.id, GoalCompleteRequest())

        ready = self.goal("ready", saved=100)
        self.assert_error(400, complete_goal, ready.id, GoalCompleteRequest(mode="spend"))
        for category_id, code in (("missing", 404), (self.income.id, 404), (self.other_expense.id, 404)):
            with self.subTest(category_id=category_id):
                self.assert_error(
                    code,
                    complete_goal,
                    ready.id,
                    GoalCompleteRequest(mode="spend", category_id=category_id),
                )


if __name__ == "__main__":
    unittest.main()
