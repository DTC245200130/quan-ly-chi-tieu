import unittest
from datetime import date
from decimal import Decimal

from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.models.budget import Budget
from app.models.category import Category
from app.models.transaction import Transaction
from app.models.user import User
from app.routers.budgets import (
    create_budget,
    delete_budget,
    list_budgets,
    update_budget,
)
from app.routers.categories import (
    create_category,
    delete_category,
    list_categories,
    update_category,
)
from app.routers.transactions import (
    create_transaction,
    delete_transaction,
    list_transactions,
    update_transaction,
)
from app.schemas.budget import BudgetCreate, BudgetUpdate
from app.schemas.category import CategoryCreate, CategoryUpdate
from app.schemas.transaction import TransactionCreate, TransactionUpdate


class CrudRoutesTest(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        self.db = sessionmaker(bind=self.engine)()
        self.user = User(id="user-1", username="owner", email="owner@example.com", password_hash="x")
        self.other = User(id="user-2", username="other", email="other@example.com", password_hash="x")
        self.food = Category(
            id="food", user_id=self.user.id, name="Ăn uống", type="expense",
            color="#111111", icon="utensils",
        )
        self.salary = Category(
            id="salary", user_id=self.user.id, name="Lương", type="income",
            color="#222222", icon="banknote",
        )
        self.other_category = Category(
            id="other-food", user_id=self.other.id, name="Ăn uống", type="expense",
            color="#333333", icon="wallet",
        )
        self.db.add_all([self.user, self.other, self.food, self.salary, self.other_category])
        self.db.add_all([
            Transaction(
                id="t-old", user_id=self.user.id, category_id=self.food.id,
                amount=Decimal("25"), type="expense", txn_date=date(2026, 7, 31), note="old",
            ),
            Transaction(
                id="t-food", user_id=self.user.id, category_id=self.food.id,
                amount=Decimal("75"), type="expense", txn_date=date(2026, 8, 2), note="Lunch ABC",
            ),
            Transaction(
                id="t-income", user_id=self.user.id, category_id=self.salary.id,
                amount=Decimal("500"), type="income", txn_date=date(2026, 8, 3), note=None,
            ),
            Transaction(
                id="t-other", user_id=self.other.id, category_id=self.other_category.id,
                amount=Decimal("999"), type="expense", txn_date=date(2026, 8, 2), note="ABC",
            ),
        ])
        self.db.commit()

    def tearDown(self):
        self.db.close()
        self.engine.dispose()

    def assert_http_error(self, status_code, callable_, *args, **kwargs):
        with self.assertRaises(HTTPException) as caught:
            callable_(*args, **kwargs)
        self.assertEqual(caught.exception.status_code, status_code)
        return caught.exception

    def test_categories_are_scoped_and_cover_duplicate_update_delete_branches(self):
        self.assertEqual({item.id for item in list_categories(self.db, self.user)}, {"food", "salary"})

        duplicate = CategoryCreate(name="Ăn uống", type="expense", icon="wallet")
        self.assert_http_error(400, create_category, duplicate, self.db, self.user)

        created = create_category(
            CategoryCreate(name="Mua sắm", type="expense", color="#abcdef", icon="shopping-bag"),
            self.db,
            self.user,
        )
        self.assertEqual(created.user_id, self.user.id)

        self.assert_http_error(404, update_category, "missing", CategoryUpdate(name="X"), self.db, self.user)
        self.assert_http_error(
            400,
            update_category,
            created.id,
            CategoryUpdate(name=self.food.name, type=self.food.type),
            self.db,
            self.user,
        )
        updated = update_category(created.id, CategoryUpdate(color="#000000"), self.db, self.user)
        self.assertEqual(updated.color, "#000000")

        self.assert_http_error(404, delete_category, "missing", self.db, self.user)
        self.assert_http_error(400, delete_category, self.food.id, self.db, self.user)
        budget_only = create_category(
            CategoryCreate(name="Dự phòng", type="expense"),
            self.db,
            self.user,
        )
        self.db.add(Budget(
            id="budget-only",
            user_id=self.user.id,
            category_id=budget_only.id,
            month=8,
            year=2026,
            limit_amount=Decimal("100"),
        ))
        self.db.commit()
        error = self.assert_http_error(400, delete_category, budget_only.id, self.db, self.user)
        self.assertIn("ngân sách", error.detail)
        self.assertEqual(delete_category(created.id, self.db, self.user), {"message": "Đã xóa danh mục"})

    def test_transaction_filters_and_all_mutation_branches(self):
        filtered = list_transactions(
            category_id=self.food.id,
            type="expense",
            from_date=date(2026, 8, 1),
            to_date=date(2026, 8, 31),
            keyword="abc",
            db=self.db,
            current_user=self.user,
        )
        self.assertEqual([item.id for item in filtered], ["t-food"])
        self.assertEqual(len(list_transactions(db=self.db, current_user=self.user)), 3)

        invalid_payload = TransactionCreate(
            category_id=self.other_category.id, amount=10, txn_date=date(2026, 8, 1)
        )
        self.assert_http_error(404, create_transaction, invalid_payload, self.db, self.user)

        created = create_transaction(
            TransactionCreate(category_id=self.salary.id, amount=100, txn_date=date(2026, 8, 4), note="bonus"),
            self.db,
            self.user,
        )
        self.assertEqual(created.type, "income")
        self.assert_http_error(404, update_transaction, "missing", TransactionUpdate(amount=1), self.db, self.user)
        self.assert_http_error(
            404,
            update_transaction,
            created.id,
            TransactionUpdate(category_id=self.other_category.id),
            self.db,
            self.user,
        )
        updated = update_transaction(
            created.id,
            TransactionUpdate(category_id=self.food.id, amount=Decimal("120"), note="changed"),
            self.db,
            self.user,
        )
        self.assertEqual(updated.type, "expense")
        self.assertEqual(updated.amount, Decimal("120"))
        self.assert_http_error(404, delete_transaction, "missing", self.db, self.user)
        self.assertEqual(delete_transaction(created.id, self.db, self.user), {"message": "Đã xóa giao dịch"})

    def test_budget_filters_spending_and_all_error_branches(self):
        budget = Budget(
            id="budget-food", user_id=self.user.id, category_id=self.food.id,
            month=8, year=2026, limit_amount=Decimal("50"),
        )
        other_budget = Budget(
            id="budget-other", user_id=self.other.id, category_id=self.other_category.id,
            month=8, year=2026, limit_amount=Decimal("1000"),
        )
        self.db.add_all([budget, other_budget])
        self.db.commit()

        result = list_budgets(month=8, year=2026, db=self.db, current_user=self.user)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["spent"], Decimal("75"))
        self.assertTrue(result[0]["is_over"])
        self.assertEqual(len(list_budgets(db=self.db, current_user=self.user)), 1)

        self.assert_http_error(
            404,
            create_budget,
            BudgetCreate(category_id=self.salary.id, month=8, year=2026, limit_amount=100),
            self.db,
            self.user,
        )
        self.assert_http_error(
            400,
            create_budget,
            BudgetCreate(category_id=self.food.id, month=8, year=2026, limit_amount=100),
            self.db,
            self.user,
        )
        created = create_budget(
            BudgetCreate(category_id=self.food.id, month=9, year=2026, limit_amount=200),
            self.db,
            self.user,
        )
        self.assertEqual(created["spent"], 0)
        self.assert_http_error(404, update_budget, "missing", BudgetUpdate(limit_amount=1), self.db, self.user)
        updated = update_budget(created["id"], BudgetUpdate(limit_amount=300), self.db, self.user)
        self.assertEqual(updated["limit_amount"], Decimal("300"))
        self.assert_http_error(404, delete_budget, "missing", self.db, self.user)
        self.assertEqual(delete_budget(created["id"], self.db, self.user), {"message": "Đã xóa ngân sách"})


if __name__ == "__main__":
    unittest.main()
