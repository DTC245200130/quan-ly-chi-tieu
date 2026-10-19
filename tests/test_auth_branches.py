import unittest
from datetime import datetime, timedelta, timezone
from io import BytesIO
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker

from app.core.security import hash_password, verify_password
from app.database import Base
from app.models.user import User
from app.routers import auth
from app.schemas.user import (
    ChangePasswordRequest,
    ForgotPasswordRequest,
    ResetPasswordRequest,
    UserProfileUpdate,
    UserRegister,
)


class AuthBranchTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        self.db = sessionmaker(bind=self.engine)()
        self.user = User(
            id="u1", username="owner", email="owner@example.com",
            password_hash=hash_password("secret1"),
        )
        self.other = User(
            id="u2", username="other", email="other@example.com",
            password_hash=hash_password("secret2"),
        )
        self.db.add_all([self.user, self.other])
        self.db.commit()
        auth._reset_request_log.clear()

    def tearDown(self):
        auth._reset_request_log.clear()
        self.db.close()
        self.engine.dispose()

    def assert_error(self, code, fn, *args, **kwargs):
        with self.assertRaises(HTTPException) as caught:
            fn(*args, **kwargs)
        self.assertEqual(caught.exception.status_code, code)
        return caught.exception

    def test_register_success_short_username_duplicate_username_and_integrity_race(self):
        short = UserRegister.model_construct(username=" x ", email="x@example.com", password="secret")
        self.assert_error(400, auth.register, short, self.db)
        self.assert_error(
            400,
            auth.register,
            UserRegister(username="owner", email="fresh@example.com", password="secret"),
            self.db,
        )
        with patch("app.routers.auth.hash_password", return_value="hashed"):
            created = auth.register(
                UserRegister(username="  fresh  ", email="FRESH@example.com", password="secret"),
                self.db,
            )
        self.assertEqual(created.username, "fresh")
        self.assertEqual(created.email, "fresh@example.com")

        fake_db = MagicMock()
        fake_db.query.return_value.filter.return_value.first.return_value = None
        fake_db.commit.side_effect = IntegrityError("statement", {}, Exception("duplicate"))
        with patch("app.routers.auth.hash_password", return_value="hashed"):
            self.assert_error(
                400,
                auth.register,
                UserRegister(username="racer", email="race@example.com", password="secret"),
                fake_db,
            )
        fake_db.rollback.assert_called_once_with()

    def test_login_failure_me_and_profile_conflicts(self):
        self.assert_error(
            401,
            auth.login,
            SimpleNamespace(username="missing", password="wrong"),
            self.db,
        )
        self.assertIs(auth.me(self.user), self.user)

        short = UserProfileUpdate.model_construct(display_name=None, username="x", email="x@example.com")
        self.assert_error(400, auth.update_profile, short, self.db, self.user)
        self.assert_error(
            400,
            auth.update_profile,
            UserProfileUpdate(display_name=None, username=self.other.username, email=self.user.email),
            self.db,
            self.user,
        )

        self.user.reset_token_hash = "old"
        self.user.reset_token_expiry = datetime.now(timezone.utc) + timedelta(minutes=1)
        result = auth.update_profile(
            UserProfileUpdate(display_name=" ", username="owner-new", email="new@example.com"),
            self.db,
            self.user,
        )
        self.assertIsNone(result.display_name)
        self.assertIsNone(result.reset_token_hash)
        self.assertIsNone(result.reset_token_expiry)

    def test_profile_integrity_race_rolls_back(self):
        with patch.object(self.db, "commit", side_effect=IntegrityError("statement", {}, Exception("race"))):
            self.assert_error(
                400,
                auth.update_profile,
                UserProfileUpdate(display_name="Owner", username="owner", email="owner@example.com"),
                self.db,
                self.user,
            )

    def test_change_password_commit_failure_rolls_back(self):
        with patch.object(self.db, "commit", side_effect=RuntimeError("database unavailable")), patch.object(
            self.db, "rollback"
        ) as rollback:
            error = self.assert_error(
                500,
                auth.change_password,
                ChangePasswordRequest(current_password="secret1", new_password="new-secret"),
                self.db,
                self.user,
            )

        self.assertEqual(error.detail, "Không thể đổi mật khẩu. Vui lòng thử lại.")
        rollback.assert_called_once_with()

    def test_avatar_validation_and_commit_cleanup(self):
        bad_type = SimpleNamespace(content_type="text/plain", file=BytesIO(b"text"))
        self.assert_error(415, auth.upload_avatar, bad_type, self.db, self.user)

        for content, expected in ((b"", 400), (b"x" * (auth.AVATAR_MAX_BYTES + 1), 413), (b"not png", 415)):
            with self.subTest(expected=expected):
                file = SimpleNamespace(content_type="image/png", file=BytesIO(content))
                self.assert_error(expected, auth.upload_avatar, file, self.db, self.user)

        with TemporaryDirectory() as directory, patch.object(auth, "AVATAR_DIRECTORY", Path(directory)):
            file = SimpleNamespace(content_type="image/png", file=BytesIO(b"\x89PNG\r\n\x1a\nvalid"))
            fake_db = MagicMock()
            fake_db.commit.side_effect = RuntimeError("db down")
            with self.assertRaises(RuntimeError):
                auth.upload_avatar(file, fake_db, self.user)
            self.assertEqual(list(Path(directory).iterdir()), [])
            fake_db.rollback.assert_called_once_with()

    def test_avatar_replacement_removes_only_local_previous_file(self):
        with TemporaryDirectory() as directory, patch.object(auth, "AVATAR_DIRECTORY", Path(directory)):
            previous = Path(directory) / "old.png"
            previous.write_bytes(b"old")
            self.user.avatar_url = "/uploads/avatars/old.png"
            self.db.commit()
            result = auth.upload_avatar(
                SimpleNamespace(
                    content_type="image/webp",
                    file=BytesIO(b"RIFF1234WEBPvalid"),
                ),
                self.db,
                self.user,
            )
            self.assertFalse(previous.exists())
            self.assertTrue((Path(directory) / Path(result.avatar_url).name).exists())

            auth._remove_local_avatar("https://example.com/external.png")
            auth._remove_local_avatar(None)

    @patch("app.routers.auth.send_reset_password_email")
    @patch("app.routers.auth.secrets.token_urlsafe", return_value="known-token")
    def test_forgot_password_known_user_and_rate_limit(self, _token, send_email):
        response = auth.forgot_password(ForgotPasswordRequest(email="OWNER@example.com"), self.db)
        self.assertIn("Nếu email tồn tại", response.message)
        send_email.assert_called_once_with("owner@example.com", "known-token")
        self.assertEqual(self.user.reset_token_hash, auth._hash_token("known-token"))

        now = datetime.now(timezone.utc)
        auth._reset_request_log[self.user.email] = [
            now - timedelta(minutes=1), now - timedelta(minutes=2), now - timedelta(minutes=3),
            now - timedelta(hours=2),
        ]
        auth.forgot_password(ForgotPasswordRequest(email=self.user.email), self.db)
        self.assertEqual(send_email.call_count, 1)
        self.assertTrue(auth._is_rate_limited(self.user.email))

    def test_reset_password_missing_expired_and_naive_expiry(self):
        self.assert_error(
            400,
            auth.reset_password,
            ResetPasswordRequest(token="missing", new_password="newpass"),
            self.db,
        )

        self.user.reset_token_hash = auth._hash_token("no-expiry")
        self.user.reset_token_expiry = None
        self.db.commit()
        self.assert_error(
            400,
            auth.reset_password,
            ResetPasswordRequest(token="no-expiry", new_password="newpass"),
            self.db,
        )

        self.user.reset_token_hash = auth._hash_token("expired")
        utc_now_naive = datetime.now(timezone.utc).replace(tzinfo=None)
        self.user.reset_token_expiry = utc_now_naive - timedelta(seconds=1)
        self.db.commit()
        self.assert_error(
            400,
            auth.reset_password,
            ResetPasswordRequest(token="expired", new_password="newpass"),
            self.db,
        )

        self.user.reset_token_hash = auth._hash_token("valid-naive")
        self.user.reset_token_expiry = utc_now_naive + timedelta(minutes=5)
        self.db.commit()
        auth.reset_password(
            ResetPasswordRequest(token="valid-naive", new_password="newpass"),
            self.db,
        )
        self.assertTrue(verify_password("newpass", self.user.password_hash))


if __name__ == "__main__":
    unittest.main()
