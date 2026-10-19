import unittest
from datetime import date
from decimal import Decimal
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import MagicMock, Mock, patch

import requests
from fastapi import HTTPException
from jose import JWTError
from pydantic import ValidationError
from sqlalchemy import create_engine, inspect, text

from app.core import assistant_context, email, gemini
from app.core.deps import get_current_user
from app.core.gemini import (
    GeminiNotConfiguredError,
    GeminiRateLimitError,
    GeminiServiceError,
    GeminiUnavailableError,
)
from app.core.schema_migrations import (
    ensure_category_icon_column,
    ensure_goal_completion_columns,
    ensure_user_profile_columns,
)
from app.database import get_db
from app.schemas.goal import GoalCreate, GoalItemCreate, GoalItemUpdate, GoalUpdate
from app.schemas.category import CategoryCreate, CategoryUpdate
from app.schemas.transaction import TransactionCreate, TransactionUpdate


class DependencyAndDatabaseTests(unittest.TestCase):
    def test_get_current_user_accepts_valid_subject(self):
        user = object()
        db = MagicMock()
        db.query.return_value.filter.return_value.first.return_value = user
        with patch("app.core.deps.decode_access_token", return_value={"sub": "user-1"}):
            self.assertIs(get_current_user("token", db), user)

    def test_get_current_user_rejects_invalid_payload_missing_and_unknown_user(self):
        db = MagicMock()
        for payload in ({}, {"sub": None}):
            with self.subTest(payload=payload), patch("app.core.deps.decode_access_token", return_value=payload):
                with self.assertRaises(HTTPException) as caught:
                    get_current_user("token", db)
                self.assertEqual(caught.exception.status_code, 401)

        with patch("app.core.deps.decode_access_token", side_effect=JWTError("bad")):
            with self.assertRaises(HTTPException):
                get_current_user("token", db)

        db.query.return_value.filter.return_value.first.return_value = None
        with patch("app.core.deps.decode_access_token", return_value={"sub": "missing"}):
            with self.assertRaises(HTTPException):
                get_current_user("token", db)

    def test_get_db_always_closes_session(self):
        session = MagicMock()
        with patch("app.database.SessionLocal", return_value=session):
            generator = get_db()
            self.assertIs(next(generator), session)
            generator.close()
        session.close.assert_called_once_with()


class EmailTests(unittest.TestCase):
    @patch("app.core.email.requests.post")
    def test_email_success_and_non_success_status(self, post):
        post.return_value.status_code = 200
        with patch.object(
            email,
            "RESEND_FROM_EMAIL",
            "Expense Management AI <no-reply@verified.example>",
        ), patch.object(email, "FRONTEND_URL", "https://app.verified.example"):
            self.assertTrue(email.send_reset_password_email("a@example.com", "token"))
        kwargs = post.call_args.kwargs
        self.assertEqual(
            kwargs["json"]["from"],
            "Expense Management AI <no-reply@verified.example>",
        )
        self.assertIn(
            "https://app.verified.example/reset-password?token=token",
            kwargs["json"]["html"],
        )
        self.assertEqual(kwargs["timeout"], 10)

        post.return_value.status_code = 202
        self.assertFalse(email.send_reset_password_email("a@example.com", "token"))

    @patch("app.core.email.requests.post", side_effect=requests.ConnectionError("offline"))
    def test_email_request_failure_is_non_fatal(self, _post):
        self.assertFalse(email.send_reset_password_email("a@example.com", "token"))


class MigrationTests(unittest.TestCase):
    def test_migrations_return_when_tables_are_absent(self):
        engine = create_engine("sqlite:///:memory:")
        ensure_category_icon_column(engine)
        ensure_goal_completion_columns(engine)
        ensure_user_profile_columns(engine)
        engine.dispose()

    def test_goal_and_user_legacy_tables_are_upgraded_idempotently(self):
        engine = create_engine("sqlite:///:memory:")
        with engine.begin() as connection:
            connection.execute(text(
                "CREATE TABLE saving_goals (id VARCHAR PRIMARY KEY, target_amount NUMERIC, status VARCHAR)"
            ))
            connection.execute(text(
                "INSERT INTO saving_goals VALUES ('done', 750, 'completed'), ('active', 100, 'active')"
            ))
            connection.execute(text(
                "CREATE TABLE users (id VARCHAR PRIMARY KEY, username VARCHAR NOT NULL)"
            ))

        ensure_goal_completion_columns(engine)
        ensure_user_profile_columns(engine)
        ensure_goal_completion_columns(engine)
        ensure_user_profile_columns(engine)

        self.assertIn("completion_amount", {c["name"] for c in inspect(engine).get_columns("saving_goals")})
        self.assertIn("completion_mode", {c["name"] for c in inspect(engine).get_columns("saving_goals")})
        self.assertIn("display_name", {c["name"] for c in inspect(engine).get_columns("users")})
        with engine.connect() as connection:
            amount = connection.execute(text(
                "SELECT completion_amount FROM saving_goals WHERE id='done'"
            )).scalar_one()
        self.assertEqual(Decimal(amount), Decimal("750"))
        engine.dispose()

    def test_category_migration_is_noop_when_icon_exists(self):
        engine = create_engine("sqlite:///:memory:")
        with engine.begin() as connection:
            connection.execute(text(
                "CREATE TABLE categories (id VARCHAR PRIMARY KEY, type VARCHAR, icon VARCHAR)"
            ))
        ensure_category_icon_column(engine)
        self.assertEqual(
            {c["name"] for c in inspect(engine).get_columns("categories")},
            {"id", "type", "icon"},
        )
        engine.dispose()


class GeminiBranchTests(unittest.TestCase):
    def test_prompt_configuration_and_output_fallbacks(self):
        history = [("user", "x" * 2100), ("assistant", "answer")]
        prompt = gemini.build_prompt(" question ", {"when": date(2026, 1, 2)}, history)
        self.assertIn("Người dùng: " + "x" * 2000, prompt)
        self.assertIn("Trợ lý: answer", prompt)
        self.assertIn('"when":"2026-01-02"', prompt)
        self.assertTrue(prompt.endswith("question"))
        self.assertIn("Chưa có hội thoại", gemini.build_prompt("q", {}, []))

        self.assertEqual(gemini.extract_response_text({"outputs": [{"text": " ok "}]}), "ok")
        self.assertEqual(gemini.extract_response_text({"outputs": [None, {"text": 1}]}), "")
        self.assertEqual(gemini.extract_response_text({"steps": [None, {"type": "other"}]}), "")
        with patch.dict("os.environ", {"GEMINI_MODEL": "custom"}):
            self.assertEqual(gemini.configured_model(), "custom")

    @patch("app.core.gemini._api_key", return_value="")
    def test_missing_key(self, _key):
        with self.assertRaises(GeminiNotConfiguredError):
            gemini.generate_financial_advice("q", {}, [])

    def _run_with_response(self, response):
        with patch("app.core.gemini._api_key", return_value="key"), patch(
            "app.core.gemini.requests.post", return_value=response
        ), patch("app.core.gemini.time.sleep"):
            return gemini.generate_financial_advice("q", {}, [])

    def test_http_and_response_error_mapping(self):
        cases = [
            (429, GeminiRateLimitError),
            (503, GeminiUnavailableError),
            (400, GeminiServiceError),
        ]
        for status_code, expected in cases:
            response = Mock(status_code=status_code)
            with self.subTest(status=status_code), self.assertRaises(expected):
                self._run_with_response(response)

        invalid_json = Mock(status_code=200)
        invalid_json.json.side_effect = ValueError("bad json")
        with self.assertRaises(GeminiServiceError):
            self._run_with_response(invalid_json)

        empty = Mock(status_code=200)
        empty.json.return_value = {}
        with self.assertRaises(GeminiServiceError):
            self._run_with_response(empty)

    @patch("app.core.gemini.time.sleep")
    @patch("app.core.gemini.requests.post", side_effect=requests.ConnectionError("offline"))
    @patch("app.core.gemini._api_key", return_value="key")
    def test_connection_retries_then_unavailable(self, _key, post, sleep):
        with self.assertRaises(GeminiUnavailableError):
            gemini.generate_financial_advice("q", {}, [])
        self.assertEqual(post.call_count, 2)
        sleep.assert_called_once_with(1)

    @patch("app.core.gemini.requests.post", side_effect=requests.RequestException("bad"))
    @patch("app.core.gemini._api_key", return_value="key")
    def test_generic_request_error(self, _key, _post):
        with self.assertRaises(GeminiServiceError):
            gemini.generate_financial_advice("q", {}, [])


class HelperAndSchemaTests(unittest.TestCase):
    def test_assistant_math_and_month_helpers(self):
        self.assertEqual(assistant_context.month_bounds(2026, 12), (date(2026, 12, 1), date(2027, 1, 1)))
        self.assertEqual(assistant_context.shift_month(2026, 1, -1), (2025, 12))
        self.assertEqual(assistant_context.change_percentage(Decimal(0), Decimal(0)), 0)
        self.assertIsNone(assistant_context.change_percentage(Decimal(1), Decimal(0)))
        self.assertEqual(assistant_context.percentage(Decimal(1), Decimal(0)), 0)

    def test_goal_validators_accept_trimmed_and_reject_empty_or_long_names(self):
        self.assertEqual(GoalCreate(name="  Mua xe  ", target_amount=1).name, "Mua xe")
        self.assertEqual(GoalUpdate(name="  Mới  ").name, "Mới")
        self.assertIsNone(GoalUpdate(name=None).name)
        self.assertEqual(GoalItemCreate(name="  Bánh xe  ", cost=1).name, "Bánh xe")
        self.assertEqual(GoalItemUpdate(name="  Khung  ").name, "Khung")
        self.assertIsNone(GoalItemUpdate(name=None).name)
        for factory in (
            lambda: GoalCreate(name=" ", target_amount=1),
            lambda: GoalCreate(name="x" * 101, target_amount=1),
            lambda: GoalUpdate(name=" "),
            lambda: GoalUpdate(name="x" * 101),
            lambda: GoalItemCreate(name=" ", cost=1),
            lambda: GoalItemUpdate(name=" "),
        ):
            with self.subTest(factory=factory), self.assertRaises(ValidationError):
                factory()

    def test_transaction_date_validators(self):
        today = date.today()
        self.assertEqual(TransactionCreate(category_id="c", amount=1, txn_date=today).txn_date, today)
        self.assertEqual(TransactionUpdate(txn_date=today).txn_date, today)
        future = date(today.year + 1, 1, 1)
        for factory in (
            lambda: TransactionCreate(category_id="c", amount=1, txn_date=future),
            lambda: TransactionUpdate(txn_date=future),
            lambda: TransactionUpdate(txn_date=None),
        ):
            with self.assertRaises(ValidationError):
                factory()

    def test_category_type_is_limited_to_income_or_expense(self):
        self.assertEqual(CategoryCreate(name="Lương", type="income").type, "income")
        self.assertEqual(CategoryUpdate(type="expense").type, "expense")
        for factory in (
            lambda: CategoryCreate(name="Sai", type="nonsense"),
            lambda: CategoryUpdate(type="nonsense"),
        ):
            with self.assertRaises(ValidationError):
                factory()


class FrontendServingTests(unittest.TestCase):
    def test_frontend_serving_branches(self):
        from app.main import serve_frontend

        with TemporaryDirectory() as directory:
            root = Path(directory)
            with patch("app.main.FRONTEND_DIST", root):
                with self.assertRaises(HTTPException) as api_error:
                    serve_frontend("api/unknown")
                self.assertEqual(api_error.exception.status_code, 404)

                with self.assertRaises(HTTPException) as missing:
                    serve_frontend("")
                self.assertEqual(missing.exception.status_code, 503)

                (root / "index.html").write_text("index", encoding="utf-8")
                (root / "asset.js").write_text("asset", encoding="utf-8")
                self.assertEqual(Path(serve_frontend("asset.js").path).name, "asset.js")
                fallback = serve_frontend("dashboard")
                self.assertEqual(Path(fallback.path).name, "index.html")
                self.assertEqual(fallback.headers["cache-control"], "no-store")

                with self.assertRaises(HTTPException) as traversal:
                    serve_frontend("../outside.txt")
                self.assertEqual(traversal.exception.status_code, 404)


if __name__ == "__main__":
    unittest.main()
