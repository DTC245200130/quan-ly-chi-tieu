import json
import unittest
from datetime import date
from unittest.mock import patch

from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.assistant_context import build_assistant_context
from app.database import Base
from app.models.ai_conversation import AIConversation, AIMessage
from app.models.category import Category
from app.models.transaction import Transaction
from app.models.user import User
from app.routers.assistant import ask_assistant, delete_conversation, get_conversation
from app.schemas.assistant import AssistantAskRequest


class AssistantApiTest(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        self.db = sessionmaker(bind=self.engine)()
        self.user = User(
            id="user-1",
            username="private-user",
            email="private@example.com",
            password_hash="test",
        )
        self.other_user = User(
            id="user-2",
            username="other",
            email="other@example.com",
            password_hash="test",
        )
        food = Category(
            id="food",
            user_id=self.user.id,
            name="Tên tùy chỉnh rất riêng tư",
            type="expense",
            color="#07845c",
            icon="utensils",
        )
        other = Category(
            id="other",
            user_id=self.other_user.id,
            name="Dữ liệu người khác",
            type="expense",
            color="#000000",
            icon="wallet",
        )
        self.db.add_all([self.user, self.other_user, food, other])
        self.db.add_all(
            [
                Transaction(
                    id="aug-food",
                    user_id=self.user.id,
                    category_id=food.id,
                    amount=6000,
                    type="expense",
                    txn_date=date(2026, 8, 8),
                    note="Ghi chú tuyệt mật",
                ),
                Transaction(
                    id="jul-food",
                    user_id=self.user.id,
                    category_id=food.id,
                    amount=3000,
                    type="expense",
                    txn_date=date(2026, 7, 8),
                ),
                Transaction(
                    id="other-user",
                    user_id=self.other_user.id,
                    category_id=other.id,
                    amount=999999,
                    type="expense",
                    txn_date=date(2026, 8, 8),
                ),
            ]
        )
        self.db.commit()

    def tearDown(self):
        self.db.close()
        self.engine.dispose()

    def test_context_contains_only_scoped_aggregates_and_safe_labels(self):
        context = build_assistant_context(self.db, self.user.id, 8, 2026)
        serialized = json.dumps(context, ensure_ascii=False, default=str)

        self.assertEqual(context["current"]["expense"], 6000)
        self.assertEqual(context["previous"]["expense"], 3000)
        self.assertEqual(context["categories"][0]["label"], "Ăn uống")
        self.assertNotIn("Tên tùy chỉnh rất riêng tư", serialized)
        self.assertNotIn("Ghi chú tuyệt mật", serialized)
        self.assertNotIn("private@example.com", serialized)
        self.assertNotIn("Dữ liệu người khác", serialized)
        self.assertNotIn("999999", serialized)

    @patch("app.routers.assistant.generate_financial_advice")
    def test_ask_creates_owned_conversation_and_persists_evidence(self, generate):
        generate.return_value = "Chi tiêu tăng chủ yếu ở nhóm Ăn uống. Đây là đề xuất tham khảo."

        result = ask_assistant(
            AssistantAskRequest(question="Vì sao chi tiêu tăng?", month=8, year=2026),
            db=self.db,
            current_user=self.user,
        )

        self.assertEqual(result.conversation.title, "Vì sao chi tiêu tăng?")
        self.assertEqual(len(result.conversation.messages), 2)
        self.assertEqual(result.conversation.messages[0].role, "user")
        self.assertEqual(result.conversation.messages[1].role, "assistant")
        self.assertEqual(result.conversation.messages[1].evidence.current.expense, 6000)
        self.assertEqual(self.db.query(AIConversation).count(), 1)
        self.assertEqual(self.db.query(AIMessage).count(), 2)

        args = generate.call_args.args
        prompt_context = json.dumps(args[1], ensure_ascii=False, default=str)
        self.assertNotIn("Tên tùy chỉnh rất riêng tư", prompt_context)
        self.assertNotIn("Ghi chú tuyệt mật", prompt_context)

    def test_conversations_are_scoped_and_delete_removes_messages(self):
        conversation = AIConversation(id="owned", user_id=self.user.id, title="Owned")
        other = AIConversation(id="other-thread", user_id=self.other_user.id, title="Other")
        self.db.add_all([conversation, other])
        self.db.add(AIMessage(id="message", conversation_id=conversation.id, role="user", content="Hello"))
        self.db.commit()

        result = get_conversation(conversation.id, db=self.db, current_user=self.user)
        self.assertEqual(result.id, conversation.id)

        with self.assertRaises(HTTPException) as context:
            get_conversation(other.id, db=self.db, current_user=self.user)
        self.assertEqual(context.exception.status_code, 404)

        delete_conversation(conversation.id, db=self.db, current_user=self.user)
        self.assertIsNone(self.db.query(AIConversation).filter_by(id=conversation.id).first())
        self.assertEqual(self.db.query(AIMessage).filter_by(conversation_id=conversation.id).count(), 0)


if __name__ == "__main__":
    unittest.main()
