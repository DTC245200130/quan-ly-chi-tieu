# Báo cáo kiểm thử hộp trắng

Ngày thực hiện: 31/08/2026

## Phạm vi

- Backend FastAPI/SQLAlchemy: core services, dependency xác thực, schema, migration, router, phân quyền theo người dùng, tích hợp Gemini/email và phục vụ frontend.
- Frontend React: API client và chuẩn hóa dữ liệu, AuthContext, route guards, component dùng chung, bảy trang nghiệp vụ và bốn luồng xác thực.
- Kỹ thuật: statement/branch coverage, condition/boundary testing, positive/negative paths, rollback, authorization scope, error mapping, retry và rendering states.

## Kết quả tự động

| Phần | Test | Kết quả | Statement | Branch | Function | Line |
|---|---:|---|---:|---:|---:|---:|
| Backend | 66 | Đạt | 99.23% | 93.51% | — | 99.23% |
| Frontend | 50 | Đạt | 63.98% | 47.98% | 59.27% | 69.08% |
| Tổng | 116 | Đạt | — | — | — | — |

Coverage tổng hợp statement + branch của backend là 98.41%. Ngưỡng hồi quy được cấu hình ở mức 95% cho backend và 60% statement / 45% branch / 55% function / 65% line cho frontend.

## Các nhánh chính đã phủ

- Đăng ký/đăng nhập, cập nhật hồ sơ, avatar hợp lệ/không hợp lệ/quá dung lượng, forgot/reset password, rate limit và token hết hạn.
- CRUD danh mục, giao dịch, ngân sách và mục tiêu; duplicate/not-found/in-use; kiểm tra ownership; nạp/rút/hoàn thành mục tiêu theo ba chế độ.
- Tổng hợp Dashboard/Report/Assistant theo kỳ, kỳ rỗng, dữ liệu người khác, ngân sách vượt hạn mức và số dư khả dụng.
- Gemini: thiếu cấu hình, timeout, mất kết nối, retry, rate limit, upstream error, JSON lỗi và phản hồi rỗng.
- Migration cũ/mới/idempotent; static frontend routing, API 404, path traversal và build chưa tồn tại.
- React: success/loading/error/retry cho mọi trang, xác thực và điều hướng, profile, upload validation, request headers, lỗi HTTP và chuẩn hóa số.

## Khiếm khuyết đã khắc phục

1. `TransactionUpdate(txn_date=None)` nay trả lỗi validation có cấu trúc; bỏ qua trường `txn_date` vẫn hỗ trợ cập nhật từng phần như trước.
2. `CategoryCreate.type`, `CategoryUpdate.type` và `CategoryOut.type` nay chỉ chấp nhận `Literal["income", "expense"]`.
3. `listBudgets`, `createBudget` và `updateBudget` nay chuẩn hóa `limit_amount` và `spent` từ Decimal dạng chuỗi sang `number`.

Mỗi lỗi đều có test hồi quy tương ứng trong bộ test backend hoặc frontend.

## Cách chạy lại

```powershell
.\venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\venv\Scripts\python.exe -m coverage erase
.\venv\Scripts\python.exe -m coverage run -m unittest discover -s tests
.\venv\Scripts\python.exe -m coverage report -m

Set-Location frontend
npm.cmd install
npm.cmd run test:coverage
npm.cmd run build
```
