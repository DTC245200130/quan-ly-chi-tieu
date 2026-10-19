---
name: security-review
description: Thực hiện rà soát bảo mật chỉ đọc cho Sổ Chi Tiêu trên các khía cạnh xác thực, phân quyền, đầu vào, upload, secret, quyền riêng tư AI, dependency và triển khai.
---

# Rà soát bảo mật

## Phạm vi nhiệm vụ

Áp dụng [hợp đồng context](../../../docs/ai-engineering/context.md); prompt tương ứng: [AIP-SEC-001](../../../docs/ai-engineering/prompts.md#aip-sec-001). Các bước ghi file bên dưới chỉ áp dụng khi nhiệm vụ cho phép cập nhật artifact đó. Với yêu cầu tư vấn, phân tích hoặc review không ghi file, trả kết quả trong câu trả lời; không tự chạy toàn quy trình hay chuyển sang triển khai. Quyết định đã được người dùng chốt là đầu vào, không hỏi lại cùng quyết định.

## Quy trình

Khi review sâu auth, upload, API hoặc privacy AI, đọc [Review bảo mật theo ranh giới](references/focused-checks.md). Chỉ nạp phần phù hợp nhiệm vụ.

1. Xác định phạm vi, môi trường và phương pháp review; ghi rõ SAST/DAST/dependency scan nào được chạy hoặc không chạy.
2. Đọc requirements bảo mật/quyền riêng tư, kiến trúc, deployment và luồng dữ liệu AI.
3. Kiểm tra xác thực: đăng ký/đăng nhập, hash mật khẩu, token expiry/validation, reset token, enumeration và rate limit.
4. Kiểm tra phân quyền cấp đối tượng trên từng query/mutation; xác minh dữ liệu tài chính, hội thoại, upload và aggregate đều scope theo owner đã xác thực.
5. Kiểm tra input/output: validation, SQL/command injection, path traversal, upload MIME/magic/size, XSS và khả năng áp dụng CSRF.
6. Kiểm tra secret/config: biến môi trường, log, response, frontend bundle, CORS, trusted host, debug/docs và thông báo lỗi.
7. Kiểm tra AI privacy: chỉ gửi aggregate được lập tài liệu; loại identity, note, raw transaction, internal ID và dữ liệu cấm; kiểm tra timeout, error mapping và `store: false` khi hỗ trợ.
8. Kiểm tra dependency/deployment: version pinning, vulnerability evidence, TLS, public storage, backup/retention và trust boundary.
9. Với mỗi finding, ghi severity, bằng chứng file:dòng hoặc lệnh, kịch bản khai thác/tác động và remediation. Không khẳng định lỗ hổng nếu chỉ có giả thuyết.
10. Cập nhật `docs/software/testing/security-review.md` với controls đã quan sát, finding, giới hạn và rủi ro chưa kiểm chứng.

## Điểm dừng và gate

- Không sửa mã trong skill này.
- Phải phân biệt `không có finding` với `chưa kiểm tra`.
- HIGH/CRITICAL còn mở phải được con người chấp nhận hoặc được khắc phục trước khi Security Gate được phê duyệt; AI không tự phê duyệt gate.
