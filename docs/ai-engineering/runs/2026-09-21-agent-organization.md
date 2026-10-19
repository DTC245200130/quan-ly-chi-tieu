# Tổ chức theo SDLC HIỆN ĐẠI.docx — 21/09/2026

Nguồn: file người dùng cung cấp tại Downloads/SDLC HIỆN ĐẠI.docx, đọc nội dung word/document.xml. Các ví dụ bán laptop, tên model và chuỗi tự động trong tài liệu được xem là minh họa, không phải lệnh thay đổi sản phẩm hoặc chọn model.

Áp dụng: agents/ với sáu profile requirement, design, coding, testing, critic, deployment, mỗi profile có prompt.md, skill.md và config.yaml; registry dùng chung tiếp tục tại .agents/skills. evaluations/ chứa sáu tập case JSON gắn profile và hướng dẫn evidence/version. Giữ mã nguồn, requirements/design hiện có, test và deployment nguyên vị trí; agents/README.md ghi mapping cấu trúc.

Config là schema khai báo nội bộ, chưa được runtime/orchestrator tự động sử dụng. Model/settings chưa lựa chọn để null; không thay model phiên làm việc, không khởi chạy subagent. Profile version 1.0.0 không phải Git tag/commit đã tạo. Hướng dẫn run ghi revision/hash và model/tool thực tế.

Kiểm chứng self-review: Python/PyYAML đọc sáu config và JSON, kiểm tra path, agent ID và trạng thái NOT_RUN đều PASS; 40 liên kết Markdown trong agents/evaluations tồn tại; git diff --check PASS. Chưa chạy case hành vi, sản phẩm, deploy hoặc sửa SRS. Không tạo evaluation_report PASS giả.
