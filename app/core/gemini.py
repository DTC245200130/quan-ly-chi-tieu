import json
import logging
import os
import time
from typing import Iterable

import requests


DEFAULT_GEMINI_MODEL = "gemini-3.7-flash"
GEMINI_ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/interactions"
GEMINI_CONNECT_TIMEOUT = 10
GEMINI_READ_TIMEOUT = 90
GEMINI_MAX_ATTEMPTS = 2

logger = logging.getLogger(__name__)


class GeminiNotConfiguredError(RuntimeError):
    pass


class GeminiServiceError(RuntimeError):
    pass


class GeminiRateLimitError(GeminiServiceError):
    pass


class GeminiTimeoutError(GeminiServiceError):
    pass


class GeminiUnavailableError(GeminiServiceError):
    pass


SYSTEM_INSTRUCTION = """Bạn là trợ lý tài chính cá nhân của Sổ Chi Tiêu.
Chỉ đưa ra giải thích và đề xuất tham khảo; không nói rằng bạn đã hoặc có thể sửa dữ liệu.
Chỉ sử dụng các số liệu tổng hợp trong CONTEXT. Không suy đoán giao dịch, ghi chú, danh tính hoặc thông tin không có trong CONTEXT.
Trả lời bằng tiếng Việt, mở đầu bằng kết luận ngắn, sau đó nêu bằng chứng và giả định khi có dự báo.
Phân biệt rõ dữ liệu thực tế với ước tính. Nếu dữ liệu ít, nói rõ mức độ không chắc chắn.
Không đưa ra lời khuyên đầu tư, tín dụng, thuế hoặc pháp lý mang tính quyết định.
Không dùng HTML. Không nhắc lại dữ liệu riêng tư vì dữ liệu đó không được cung cấp."""


def configured_model() -> str:
    return os.getenv("GEMINI_MODEL", DEFAULT_GEMINI_MODEL)


def _api_key() -> str:
    return (os.getenv("GEMINI_API_KEY") or os.getenv("AI_API_KEY") or "").strip()


def _json_default(value):
    if hasattr(value, "isoformat"):
        return value.isoformat()
    return str(value)


def build_prompt(question: str, context: dict, history: Iterable[tuple[str, str]]) -> str:
    history_lines = []
    for role, content in list(history)[-10:]:
        safe_role = "Người dùng" if role == "user" else "Trợ lý"
        history_lines.append(f"{safe_role}: {content[:2000]}")
    history_text = "\n".join(history_lines) or "Chưa có hội thoại trước đó."
    context_text = json.dumps(context, ensure_ascii=False, default=_json_default, separators=(",", ":"))
    return (
        "LỊCH SỬ HỘI THOẠI TRONG ỨNG DỤNG:\n"
        f"{history_text}\n\n"
        "CONTEXT DỮ LIỆU TỔNG HỢP ĐÃ ẨN DANH:\n"
        f"{context_text}\n\n"
        "CÂU HỎI MỚI:\n"
        f"{question.strip()}"
    )


def extract_response_text(payload: dict) -> str:
    """Read text from both SDK-shaped and raw REST Interactions responses."""
    output_text = payload.get("output_text")
    if isinstance(output_text, str) and output_text.strip():
        return output_text.strip()

    for step in reversed(payload.get("steps") or []):
        if not isinstance(step, dict) or step.get("type") != "model_output":
            continue
        texts = [
            item.get("text", "").strip()
            for item in step.get("content") or []
            if isinstance(item, dict)
            and item.get("type") == "text"
            and isinstance(item.get("text"), str)
            and item.get("text", "").strip()
        ]
        if texts:
            return "\n".join(texts)

    for output in reversed(payload.get("outputs") or []):
        if not isinstance(output, dict):
            continue
        text = output.get("text")
        if isinstance(text, str) and text.strip():
            return text.strip()
    return ""


def generate_financial_advice(question: str, context: dict, history: Iterable[tuple[str, str]]) -> str:
    api_key = _api_key()
    if not api_key:
        raise GeminiNotConfiguredError("Gemini chưa được cấu hình trên máy chủ.")

    payload = {
        "model": configured_model(),
        "system_instruction": SYSTEM_INSTRUCTION,
        "input": build_prompt(question, context, history),
        "store": False,
        "generation_config": {
            "thinking_level": "low",
            "max_output_tokens": 900,
        },
    }
    response = None
    for attempt in range(1, GEMINI_MAX_ATTEMPTS + 1):
        try:
            response = requests.post(
                GEMINI_ENDPOINT,
                headers={"x-goog-api-key": api_key, "Content-Type": "application/json"},
                json=payload,
                timeout=(GEMINI_CONNECT_TIMEOUT, GEMINI_READ_TIMEOUT),
            )
        except requests.Timeout as exc:
            logger.warning("Gemini timed out after %ss", GEMINI_READ_TIMEOUT)
            raise GeminiTimeoutError(
                "Gemini phản hồi quá thời gian chờ. Vui lòng thử lại sau ít phút."
            ) from exc
        except requests.ConnectionError as exc:
            logger.warning(
                "Gemini connection failed on attempt %s/%s",
                attempt,
                GEMINI_MAX_ATTEMPTS,
            )
            if attempt < GEMINI_MAX_ATTEMPTS:
                time.sleep(1)
                continue
            raise GeminiUnavailableError(
                "Không thể kết nối tới Gemini. Vui lòng thử lại sau ít phút."
            ) from exc
        except requests.RequestException as exc:
            logger.warning("Gemini request failed: %s", type(exc).__name__)
            raise GeminiServiceError("Không thể gửi yêu cầu tới Gemini.") from exc

        if response.status_code not in (408, 429, 500, 502, 503, 504):
            break
        logger.warning(
            "Gemini returned upstream status %s on attempt %s/%s",
            response.status_code,
            attempt,
            GEMINI_MAX_ATTEMPTS,
        )
        if attempt < GEMINI_MAX_ATTEMPTS:
            time.sleep(1)

    if response is None:
        raise GeminiUnavailableError("Không thể kết nối tới Gemini. Vui lòng thử lại sau ít phút.")
    if response.status_code == 429:
        raise GeminiRateLimitError(
            "Gemini đã đạt giới hạn yêu cầu. Vui lòng chờ một lúc rồi thử lại."
        )
    if response.status_code in (408, 500, 502, 503, 504):
        raise GeminiUnavailableError(
            "Gemini đang tạm thời quá tải hoặc bảo trì. Vui lòng thử lại sau ít phút."
        )
    if response.status_code >= 400:
        logger.warning("Gemini rejected request with upstream status %s", response.status_code)
        raise GeminiServiceError("Gemini từ chối yêu cầu. Hãy kiểm tra khóa API và model cấu hình.")

    try:
        answer = extract_response_text(response.json())
    except (ValueError, TypeError) as exc:
        raise GeminiServiceError("Gemini trả về phản hồi không hợp lệ.") from exc
    if not answer:
        raise GeminiServiceError("Gemini chưa tạo được câu trả lời. Vui lòng thử lại.")
    return answer
