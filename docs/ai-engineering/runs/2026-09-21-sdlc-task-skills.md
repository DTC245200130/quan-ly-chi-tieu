# Bổ sung skill tác vụ SDLC — 21/09/2026

Yêu cầu: thực hiện phương án bổ sung 6 skill chuyên biệt và references cho bộ hiện có; tiếp tục hoàn tất từ lượt trước. Công việc bắt đầu trong cuộc trao đổi ngày 20/09 và hoàn tất ngày 21/09/2026.

Đã thêm debugging, change-impact-analysis, api-design, database-migration, document-production, release-readiness. Đã bổ sung reference use case/AC, chiến lược test/fixture, vận hành, chế độ code review và kiểm tra bảo mật chuyên sâu. Đã nối chúng vào skill cha, prompt tương ứng, danh mục vai trò và cách phối hợp; giữ implementation là skill coding chung theo nhiệm vụ.

Kiểm chứng self-review bằng PowerShell/Python: quick_validate.py PASS 17/17 skill; 114 liên kết nội bộ và các neo AIP tồn tại; 17 prompt ánh xạ đủ 17 skill; git diff --check PASS. Kiểm tra này chỉ chứng minh cấu trúc và tham chiếu, không chứng minh chất lượng hành vi.

AE-15 đến AE-20 được thêm với trạng thái NOT RUN. Không chạy agent evaluation, renderer Word/UML, migration, test/build sản phẩm hoặc deploy trong đợt xây dựng skill này. Không sửa SRS hoặc mã/database sản phẩm. Các thay đổi working tree từ lượt trước được giữ nguyên.

Skill-creator định hướng giữ entrypoint gọn, đưa hướng dẫn theo chế độ vào reference và tránh skill trùng chức năng. Các prompt mới là TEMPLATE/NOT RUN, không phải bằng chứng tạo ra implementation lịch sử.
