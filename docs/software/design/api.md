# API overview

Base path: `/api`. Các endpoint nghiệp vụ (trừ register, login, forgot/reset password, health và readiness) yêu cầu `Authorization: Bearer <token>`. OpenAPI có tại `/api/docs` khi `ENABLE_API_DOCS=true`.

| Nhóm | Endpoint chính |
|---|---|
| System | `GET /health`, `GET /ready` |
| Auth | `POST /auth/register`, `POST /auth/login`, `GET/PUT/DELETE /auth/me`, avatar, forgot/reset password |
| Categories | `GET/POST /categories/`, `PUT/DELETE /categories/{id}` |
| Transactions | `GET/POST /transactions/`, `PUT/DELETE /transactions/{id}` |
| Budgets | `GET/POST /budgets/`, `PUT/DELETE /budgets/{id}` |
| Goals | CRUD goal, items, deposit, withdraw, complete và history dưới `/goals` |
| Analytics | `GET /dashboard/`, `GET /reports/` |
| Assistant | context, conversations và `POST /assistant/messages` dưới `/assistant` |

Schema request/response chuẩn được sinh trực tiếp từ Pydantic/OpenAPI. Không dùng bảng này thay cho OpenAPI khi cần chi tiết field và validation.

## Hợp đồng mục tiêu xóa tài khoản

`DELETE /auth/me` yêu cầu Bearer token và body gồm `current_password` cùng `confirmation` có giá trị chính xác `XÓA TÀI KHOẢN`. Server lấy người dùng từ token, không nhận `user_id` từ client. Thành công trả `204` không có body; mật khẩu/xác nhận sai không thay đổi dữ liệu; lỗi trong transaction phải rollback toàn bộ. Đây là hợp đồng mục tiêu theo RQ-011, chưa phải endpoint as-built cho tới khi mã và test tương ứng tồn tại.
