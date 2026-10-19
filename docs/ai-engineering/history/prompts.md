# Prompt register

Mục đích: lưu các task/prompt người dùng đã giao cho Codex trong chuỗi AI-Augmented SDLC. Nội dung dưới đây được chép từ cuộc trao đổi ngày 06/09/2026; chỉ chuẩn hóa Markdown/khoảng trắng. Không tái dựng các prompt phát triển trước thời điểm này vì không có bằng chứng hội thoại trong repository.

## P-001 — Đối chiếu hướng dẫn

**Prompt nguyên văn:**

> đọc hướng dẫn trong file và đánh giá xem cách làm việc của tôi và bạn đã bám theo hướng dẫn chưa. nếu chưa hãy chỉ ra, và bổ sung những gì còn thiếu

**Đầu vào:** `1_Thuc_hanh_AI_Augmented_SDLC (1).docx`, repository hiện tại.  
**Skill áp dụng:** `skill-creator`, sau đó các project skill được tạo.  
**Artifacts:** `docs/governance/sdlc-compliance-audit.md`, `.agents/skills/*`, bộ tài liệu SDLC.
**Kết quả:** phát hiện thiếu skills/gates/traceability/prompt evidence; bổ sung tài liệu và sửa test discovery.

## P-002 — Tiếp tục sau khi cấp quyền đọc file

**Prompt nguyên văn:**

> tiếp tục đi

**Mục đích:** cho phép tiếp tục task P-001 sau khi môi trường cho phép đọc DOCX.  
**Artifacts:** dùng chung với P-001.

## P-003 — Yêu cầu hướng dẫn Human Gate

**Prompt nguyên văn:**

> huong dan toi xac nhan

**Kết quả:** Codex hướng dẫn cách review requirements và cách ghi `APPROVED`/`CHANGES_REQUESTED`; chưa tự phê duyệt thay người dùng.

## P-004 — Phê duyệt Requirements Gate

**Prompt nguyên văn:**

> Tôi APPROVE Requirements Gate.
>
> Tên người duyệt: Đào Minh Tâm.
>
> Các quyết định:
>
> - RQ-001: không phân biệt hoa/thường
> - RQ-002: hết hạn access token sẽ đăng xuất/thu hồi token
> - RQ-003: số dư khả dụng chính là số tiền có thể tạo giao dịch chi tiêu hoặc nạp vào mục tiêu tiết kiệm. Số tiền này không bao gồm số tiền đã nằm trong mục tiêu tiết kiệm
> - RQ-004: múi giờ hà nội, đơn vị tiền tệ là việt nam đồng, làm tròn đến 1 chữ số thập phân, ngày chốt kỳ (tháng) là ngày cuối cùng của tháng
> - RQ-005: giữ lại lịch sử hội thoại, giữ liệu cá nhân có thể chủ động xóa
> - RQ-006: hệ thống hầu như uptime 24/7, nếu có sự cố sẽ xử lý trong vòng 24h (vì hệ thống chỉ là ghi chú lại thông tin thu chi, không phản ánh và ảnh hưởng đến quyết định và hành động chi tiêu thực tế); thời gian phản hồi thao tác dưới 10s, các vấn đề còn lại chưa quyết định
> - RQ-007: dựa theo khả năng thực tế của hệ thống
> - RQ-008: offline hầu hết thao tác trên phiên bản app, trừ tính năng ai cần kết nối internet; phiên bản web yêu cầu online 100%

**Skill áp dụng:** `requirements-analysis`.  
**Artifacts:** requirements, stories, acceptance criteria, issues và Human Gate.  
**Human result:** Requirements Gate `APPROVED`; quyết định offline sau đó được P-006 thay thế.

## P-005 — Làm rõ và yêu cầu đánh giá kiến trúc

**Prompt nguyên văn:**

> 1. Bạn đánh giá tính khả thi của offline hầu hết trừ ai
> 2. Bạn đánh giá khả năng đồng bộ từ máy lên máy chủ
> 3. Vẫn cần mã hóa, ít nhất là dữ liệu gửi cho ai
> 4. Xóa tài khoản
> 5. Phản hồi dưới 10s áp dụng khi tải bình thường, hệ thống hiện tại chưa hướng tới lượng người dùng lớn nên không phải vấn đề

**Skill áp dụng:** `architecture-design`.  
**Kết quả:** đánh giá offline khả thi nhưng phức tạp; tạo draft kiến trúc local DB/sync. Draft này bị P-006 rút khỏi scope nhưng được giữ trong process log như lịch sử quyết định.

## P-006 — Human correction về offline

**Prompt nguyên văn:**

> bạn sửa lại giúp mình nhé. quyết định hiện tại là online toàn bộ. phiên bản offline sẽ dựa trên phản hồi sử dụng app của người dùng. nếu có số lượng lớn yêu cầu offline sẽ phát triển sau

**Skill áp dụng:** `requirements-analysis`, `architecture-design`.  
**Artifacts:** baseline requirements v1.1, architecture/ADR, issues, user guide và README.  
**Human correction:** `FR-OFF-001` chuyển thành `WITHDRAWN`; `FR-CONN-001` trở thành yêu cầu hiện hành.

## P-007 — Phê duyệt Architecture Gate

**Prompt nguyên văn:**

> Tôi APPROVE Architecture Gate.
>
> Người duyệt: Đào Minh Tâm
>
> - Web và ứng dụng cài đặt online toàn bộ.
> - Offline không thuộc phạm vi hiện tại.
> - Dùng chung backend FastAPI và database máy chủ.
> - Dữ liệu gửi Gemini được tối thiểu hóa và truyền qua HTTPS.
> - Đồng ý xóa backup của tài khoản đã xóa sau tối đa 30 ngày.

**Skill áp dụng:** `architecture-design`.  
**Human result:** Architecture Gate `APPROVED`; ADR-007..009 `ACCEPTED`.

## P-008 — Chuẩn bị Database Gate, không sửa code

**Prompt nguyên văn:**

> tiếp tục, đảm bảo chưa sửa code

**Skill áp dụng:** `database-design`.  
**Artifact:** `docs/software/design/database-design.md`.
**Kết quả:** chỉ thiết kế constraints/indexes/FK/delete policy; không sửa source, migration hay database.

## P-009 — Phê duyệt Database Gate

**Prompt nguyên văn:**

> Tôi APPROVE Database Gate.
>
> Người duyệt: Đào Minh Tâm
>
> 1. Cấm category trùng tên trong cùng loại của một người dùng, so khớp không phân biệt hoa thường.
> 2. Năm ngân sách hợp lệ từ 2000 đến 2100.
> 3. Nếu migration phát hiện dữ liệu trùng/xung đột: dừng và báo cáo, không tự xóa hoặc tự chọn dữ liệu.
> 4. Xóa tài khoản bằng hard delete đối với dữ liệu active; backup hết retention trong tối đa 30 ngày.

**Skill áp dụng:** `database-design`.  
**Human result:** Database Gate `APPROVED`; chưa triển khai code/migration.

## P-010 — Kiểm tra prompt evidence

**Prompt nguyên văn:**

> về phần promt người dùng thì sao?

**Skill áp dụng:** `documentation`.  
**Kết quả:** tạo prompt register này và liên kết vào audit/process log.
