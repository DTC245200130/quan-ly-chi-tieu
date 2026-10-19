# Chọn tầng kiểm thử và dữ liệu

Chọn tầng thấp nhất có thể chứng minh hành vi, bổ sung integration/E2E tại ranh giới thực sự có rủi ro:
- Unit: rule/tính toán/normalization, dependency cô lập; kiểm tra đầu ra và side effect quan trọng.
- Integration/API: route/schema/auth/persistence/transaction cùng hoạt động; success, invalid input, unauthenticated, wrong owner, missing object.
- Frontend component: hành vi người dùng, loading/error/empty, validation; không gắn kỳ vọng vào chi tiết DOM vô nghĩa.
- E2E: luồng chính đi qua browser và backend trên môi trường thử; selector ổn định, trạng thái chờ rõ, không sleep tùy tiện.
- Migration: phối hợp database-migration; SQLite không thay PostgreSQL cho kiểm chứng dialect.

Ca biên lấy từ domain và AC: rỗng/null, ngưỡng min/max, trước/tại/sau thời hạn, timezone và precision khi liên quan. Tránh sao chép mọi ca cho mọi tầng.

Fixture dùng dữ liệu giả, clock cố định khi cần, account A/B để kiểm tra ownership, reset độc lập từng ca và không phụ thuộc thứ tự. Mock dịch vụ ngoài ở ranh giới; test tích hợp dịch vụ thật chỉ khi nằm trong phạm vi và có môi trường thích hợp.

Đọc cấu hình chọn interpreter/command thực tế; chạy ca liên quan trước rồi mở rộng theo tác động. Báo lệnh, phiên bản/phạm vi, pass/fail/skip; test flaky phải ghi nhận, không retry đến pass rồi giấu lần fail. Không đổi expected để khớp bug.
