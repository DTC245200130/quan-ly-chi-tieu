# Security review report

## Rà soát lại ngày 20/09/2026

Review chỉ đọc xác nhận các query nghiệp vụ chính vẫn scope theo `current_user.id`; Gemini dùng context tổng hợp và request `store: false`. Không sửa app và không chạy SAST/DAST/dependency scan trong đợt này.

- Không phát hiện HIGH/CRITICAL mới qua source review.
- **MEDIUM — SEC-006:** hai invariant AC-018/AC-019 đang chỉ được kỳ vọng ở application và hiện tại còn thiếu; schema/migration cũng chưa có unique normalized category và CHECK năm ngân sách. Đây là integrity gap, có thể tạo dữ liệu không hợp lệ qua API hoặc regression sau này.
- Các finding SEC-001..SEC-005 bên dưới vẫn mở; đặc biệt token 24 giờ không revoke sớm, rate limit reset password in-memory, public avatar storage và thiếu vulnerability scan.

Giới hạn: không kiểm tra production TLS, PostgreSQL, backup retention, malware scan, secret history, container image hay dịch vụ ngoài live. Vì vậy báo cáo này không phải chứng nhận an toàn và Security/Release Gate không được tự động phê duyệt.

Ngày review: 06/09/2026. Phương pháp: source review và test hiện có; **chưa chạy** SAST/DAST/dependency vulnerability scanner nên không được hiểu là chứng nhận an toàn.

## Findings

- **HIGH — SEC-001:** access token 24 giờ không có cơ chế revoke/rotation hay server-side session; token bị lộ còn hiệu lực đến khi hết hạn. Cần human decision cho `RQ-002`.
- **MEDIUM — SEC-002:** reset-password rate limit dùng bộ nhớ một process và theo email; không bền qua restart, không đồng bộ nhiều instance và dễ phân tán theo identifier. Production nên dùng shared store và thêm IP/device controls.
- **MEDIUM — SEC-003:** database thiếu một số constraint ownership/invariant; một regression ở application có thể tạo tham chiếu chéo user. Xem database report.
- **MEDIUM — SEC-004:** avatar lưu trên filesystem public; đã có kiểm tra MIME/magic/size theo code và test, nhưng cần chính sách malware scanning, cleanup, headers và object storage cho production lâu dài.
- **LOW — SEC-005:** dependency versions được pin nhưng chưa có bằng chứng vulnerability scan trong đợt đánh giá này.

## Controls đã quan sát

Bcrypt password hashing; JWT expiry; secret từ environment; SQLAlchemy parameterization; per-user query filters; upload validation; CORS/trusted hosts configurable; API docs tắt mặc định ở production; Gemini key chỉ ở backend, request có timeout và `store: false`; AI context dùng aggregate category labels thay vì identity/note/raw transactions.

## CSRF/XSS

Bearer token không dùng cookie làm giảm CSRF truyền thống; nếu chuyển sang cookie phải bổ sung SameSite/CSRF token. React escaping và việc Gemini cấm HTML giảm XSS, nhưng vẫn cần CSP và kiểm thử render ở deployment thật.
