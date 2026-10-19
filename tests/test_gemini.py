import unittest
from unittest.mock import Mock, patch

import requests

from app.core.gemini import (
    GeminiTimeoutError,
    extract_response_text,
    generate_financial_advice,
)


class GeminiResponseParsingTests(unittest.TestCase):
    def test_extracts_sdk_output_text(self):
        self.assertEqual(extract_response_text({"output_text": "  Xin chào  "}), "Xin chào")

    def test_extracts_raw_interactions_model_output(self):
        payload = {
            "status": "completed",
            "steps": [
                {
                    "type": "model_output",
                    "content": [
                        {"type": "text", "text": "Kết luận."},
                        {"type": "text", "text": "Bằng chứng."},
                    ],
                }
            ],
        }
        self.assertEqual(extract_response_text(payload), "Kết luận.\nBằng chứng.")

    def test_ignores_non_text_steps(self):
        self.assertEqual(
            extract_response_text({"steps": [{"type": "tool_call", "content": []}]}),
            "",
        )

    @patch("app.core.gemini.time.sleep")
    @patch("app.core.gemini.requests.post")
    @patch("app.core.gemini._api_key", return_value="test-key")
    def test_retries_transient_upstream_failure(self, _key, post, sleep):
        busy = Mock(status_code=503)
        success = Mock(status_code=200)
        success.json.return_value = {"output_text": "Đã phân tích."}
        post.side_effect = [busy, success]

        result = generate_financial_advice("Tóm tắt", {}, [])

        self.assertEqual(result, "Đã phân tích.")
        self.assertEqual(post.call_count, 2)
        sleep.assert_called_once_with(1)
        generation_config = post.call_args.kwargs["json"]["generation_config"]
        self.assertEqual(generation_config["thinking_level"], "low")
        self.assertNotIn("temperature", generation_config)

    @patch("app.core.gemini.requests.post", side_effect=requests.ReadTimeout())
    @patch("app.core.gemini._api_key", return_value="test-key")
    def test_reports_timeout_separately(self, _key, _post):
        with self.assertRaises(GeminiTimeoutError):
            generate_financial_advice("Tóm tắt", {}, [])


if __name__ == "__main__":
    unittest.main()
