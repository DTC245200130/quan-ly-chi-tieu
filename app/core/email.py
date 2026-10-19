import os
from html import escape

import requests
from dotenv import load_dotenv


load_dotenv()

RESEND_API_KEY = os.getenv("RESEND_API_KEY")
RENDER_EXTERNAL_HOSTNAME = os.getenv("RENDER_EXTERNAL_HOSTNAME", "").strip()
FRONTEND_URL = os.getenv("FRONTEND_URL") or (
    f"https://{RENDER_EXTERNAL_HOSTNAME}"
    if RENDER_EXTERNAL_HOSTNAME
    else "http://127.0.0.1:8000"
)
RESEND_FROM_EMAIL = os.getenv(
    "RESEND_FROM_EMAIL",
    "Expense Management AI <onboarding@resend.dev>",
).strip()
RESEND_API_URL = "https://api.resend.com/emails"


def send_reset_password_email(to_email: str, reset_token: str) -> bool:
    """Gửi email chứa link đặt lại mật khẩu. Trả về True nếu gửi thành công."""
    reset_link = f"{FRONTEND_URL}/reset-password?token={reset_token}"
    safe_reset_link = escape(reset_link, quote=True)

    plain_text = (
        "Đặt lại mật khẩu Sổ Chi Tiêu\n\n"
        "Chúng tôi nhận được yêu cầu đặt lại mật khẩu cho tài khoản của bạn.\n"
        "Liên kết này có hiệu lực trong 15 phút và chỉ sử dụng được một lần:\n\n"
        f"{reset_link}\n\n"
        "Nếu bạn không gửi yêu cầu này, bạn không cần làm gì thêm. "
        "Tài khoản và mật khẩu hiện tại của bạn vẫn an toàn.\n\n"
        "Sổ Chi Tiêu"
    )

    payload = {
        "from": RESEND_FROM_EMAIL,
        "to": [to_email],
        "subject": "Đặt lại mật khẩu tài khoản Sổ Chi Tiêu",
        "text": plain_text,
        "html": f"""
            <!doctype html>
            <html lang="vi">
              <body style="margin:0;padding:0;background:#f3f7f6;font-family:Arial,sans-serif;color:#172126">
                <div style="display:none;max-height:0;overflow:hidden;opacity:0">
                  Liên kết đặt lại mật khẩu có hiệu lực trong 15 phút.
                </div>
                <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background:#f3f7f6;padding:32px 12px">
                  <tr>
                    <td align="center">
                      <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="max-width:560px;background:#ffffff;border:1px solid #e2e8e6;border-radius:12px">
                        <tr>
                          <td style="padding:28px 32px 18px;font-size:20px;font-weight:700;color:#087f5b">Sổ Chi Tiêu</td>
                        </tr>
                        <tr>
                          <td style="padding:0 32px 32px;line-height:1.6">
                            <h1 style="margin:0 0 16px;font-size:24px;line-height:1.3;color:#172126">Đặt lại mật khẩu</h1>
                            <p style="margin:0 0 16px">Chúng tôi nhận được yêu cầu đặt lại mật khẩu cho tài khoản của bạn.</p>
                            <p style="margin:0 0 24px">Nhấn nút bên dưới trong vòng <strong>15 phút</strong>. Liên kết chỉ sử dụng được một lần.</p>
                            <table role="presentation" cellspacing="0" cellpadding="0">
                              <tr>
                                <td style="border-radius:8px;background:#087f5b">
                                  <a href="{safe_reset_link}" style="display:inline-block;padding:12px 20px;color:#ffffff;text-decoration:none;font-weight:700">Đặt lại mật khẩu</a>
                                </td>
                              </tr>
                            </table>
                            <p style="margin:24px 0 0;color:#53636c;font-size:14px">Nếu bạn không gửi yêu cầu này, bạn không cần làm gì thêm. Tài khoản và mật khẩu hiện tại của bạn vẫn an toàn.</p>
                          </td>
                        </tr>
                        <tr>
                          <td style="padding:18px 32px;border-top:1px solid #e8edeb;color:#718078;font-size:12px;line-height:1.5">
                            Đây là email bảo mật tự động từ Sổ Chi Tiêu. Vui lòng không trả lời email này.
                          </td>
                        </tr>
                      </table>
                    </td>
                  </tr>
                </table>
              </body>
            </html>
        """,
    }
    headers = {
        "Authorization": f"Bearer {RESEND_API_KEY}",
        "Content-Type": "application/json",
    }

    try:
        response = requests.post(RESEND_API_URL, json=payload, headers=headers, timeout=10)
        return response.status_code == 200
    except requests.RequestException:
        return False
