# Code review report

## Rà soát lại ngày 20/09/2026

Phạm vi: review chỉ đọc toàn bộ `app/`, `frontend/src/`, Alembic migration và test; không sửa mã ứng dụng. Kết luận: ownership filtering được áp dụng nhất quán ở các router chính, frontend test/build đạt, nhưng baseline chưa đạt do hai defect đã được test tái hiện.

- **MEDIUM — CR-005 (confirmed defect, AC-018/BR-001):** `app/routers/categories.py:19-24` so sánh `Category.name == payload.name` trực tiếp, nên cùng owner/type vẫn tạo được `Food`, `food` và ` Food `. Hai test tại `tests/test_baseline_requirements.py:25-41` thất bại. Cần normalize trim/casefold ở application và ràng buộc unique tương đương trong database bằng migration đã review.
- **MEDIUM — CR-006 (confirmed defect, AC-019/BR-002):** `app/schemas/budget.py:8` khai báo `year: int` không có biên `ge=2000, le=2100`; năm 1999 và 2101 không bị từ chối. Hai test tại `tests/test_baseline_requirements.py:14-18` thất bại. Cần thêm validation và CHECK constraint qua migration.
- **LOW — CR-007 (environment reproducibility):** `python -m pytest -q` dùng Python hệ thống dừng ở collection vì thiếu FastAPI, trong khi `.\venv\Scripts\python.exe -m pytest -q` chạy đầy đủ. Tài liệu/setup cần quy định interpreter/venv rõ ràng để lệnh test tái lập được.
- **LOW — CR-008 (maintainability):** bảy output schema vẫn dùng class-based `Config`, phát 7 cảnh báo deprecated trên Pydantic 2 và sẽ cần chuyển trước Pydantic 3.

Không phát hiện defect ownership mới trong phạm vi static review; điều này không đồng nghĩa các nhánh chưa có test đã được chứng minh. Release Gate tiếp tục `PENDING`.

Ngày review: 06/09/2026. Phạm vi: as-built structure, API boundaries, tests và release configuration. Đây là review read-only; lỗi test-discovery được sửa ở bước testing riêng.

## Findings

- **MEDIUM — CR-001:** routers chứa nhiều nghiệp vụ và transaction orchestration, làm tăng coupling và khó kiểm thử transaction boundary. Nên tách service cho goal completion/budget aggregation khi tiếp tục mở rộng.
- **MEDIUM — CR-002:** database invariants chủ yếu được giữ ở Pydantic/application, chưa có đủ CHECK/unique/composite constraints; xem `docs/software/design/database-design.md`.
- **LOW — CR-003:** 7 output schema dùng Pydantic class `Config` deprecated, tạo rủi ro khi nâng lên Pydantic 3.
- **LOW — CR-004:** [white-box-test-report-2026-08-31.md](white-box-test-report-2026-08-31.md) chứa số coverage snapshot không còn trùng kết quả chạy hiện tại; nên ghi rõ snapshot hoặc sinh report tự động trong CI.

## Điểm tích cực đã kiểm chứng

Ownership filter xuất hiện xuyên suốt API nghiệp vụ; Gemini được tách khỏi database và có timeout/retry/error mapping; production build chặn API fallback và path traversal; test hiện tại chạy pass sau khi sửa discovery.
