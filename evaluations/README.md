# Agent evaluations

Ca JSON trong các thư mục *_agent là dữ liệu thử nghiệm, không phải lệnh tự động chạy. Mỗi case có input, fixture, expected observations, forbidden actions và evidence cần thu. Hiện tất cả NOT_RUN; chưa có báo cáo PASS theo agent.

Dùng [rubric E1–E5 và quy trình](../docs/ai-engineering/evaluation.md). Bộ AE-* hiện có tiếp tục là bộ ca dùng chung; các case tại đây gắn trực tiếp với profile. Khi dùng AE-* cho một agent, ghi ID nguồn thay vì sao chép đáp án.

Thực thi trong bản sao cô lập hoặc chế độ chỉ đọc phù hợp; chuẩn bị fixture tối thiểu trước khi chạy. Giữ response, diff, log đã che secret và đánh giá hành vi quan sát được. Không coi config đúng cú pháp là agent đạt.

Lưu mỗi lần thực thi vào evaluations/runs/<run-id>/ gồm metadata.json, response, diff/check evidence và evaluation_report.md; chỉ tạo run thật khi đã thực hiện. Báo cáo ghi ID case, E1–E5, verdict PASS/FAIL/BLOCKED/NOT_RUN, evaluator và độc lập/self-review. Không tạo báo cáo mẫu trông như kết quả thật.

Metadata bắt buộc: thời điểm; agent/profile version; requested/actual model và settings (unknown nếu không biết); đường dẫn/hash prompt, skills và input; Git revision/dirty state; tool versions; output hashes; evidence paths. Artifact đang sửa chưa có commit dùng SHA-256, không bịa revision.

READY/ACCEPT của critic là kết luận kỹ thuật, không cấp quyền release. Các kết quả kiểm tra cấu trúc bộ profile nằm trong docs/ai-engineering/runs, tách khỏi run đánh giá hành vi.
