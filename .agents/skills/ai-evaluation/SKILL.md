---
name: ai-evaluation
description: Đánh giá prompt, skill, context và đầu ra AI hỗ trợ phát triển Sổ Chi Tiêu theo rubric và ca hành vi; không thay thế kiểm thử phần mềm.
---

# Đánh giá AI Engineering

Đọc [context](../../../docs/ai-engineering/context.md) và [rubric cùng bộ ca](../../../docs/ai-engineering/evaluation.md). Prompt tương ứng: AIP-EVAL-001 trong [bộ prompt](../../../docs/ai-engineering/prompts.md).

1. Xác định artifact/phiên bản, mục tiêu đánh giá, chế độ kiểm tra cấu trúc hay hành vi và phạm vi được tác động.
2. Với cấu trúc: kiểm tra frontmatter skill, đường dẫn, mapping prompt–skill–vai trò, phạm vi và bằng chứng. Cấu trúc hợp lệ không chứng minh hành vi đạt.
3. Với hành vi: chọn ca liên quan, ghi input thực tế; thực hiện trong bản sao cô lập hoặc chỉ đọc. Không dùng dữ liệu tài chính thật, secret hoặc môi trường production. Chỉ giao subagent nếu việc đó được cho phép; nếu không, ghi rõ self-review.
4. Đối chiếu response, diff và thao tác với kết quả mong đợi; chấm E1–E5 và verdict theo rubric. Không suy ra PASS từ việc instruction có nhắc đúng quy tắc.
5. Báo lỗi có bằng chứng, mức ảnh hưởng và cách tái hiện. Chỉ sửa prompt/skill nếu nhiệm vụ bao gồm cải tiến; khi đó chạy lại ca liên quan.
6. Khi được yêu cầu lưu báo cáo, ghi tại docs/ai-engineering/runs với provenance, giới hạn và kết quả NOT RUN cho phần chưa thử. Không chỉnh SRS, source hoặc human gate chỉ để làm evaluation đạt.

Đầu ra: kết quả cấu trúc/hành vi được tách rõ, bằng chứng và phần còn thiếu. Evaluation đạt không đồng nghĩa sản phẩm sẵn sàng release.
