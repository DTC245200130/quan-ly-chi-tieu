# CI/CD và vận hành

## CI/CD và cấu hình

Xác định nền tảng pipeline hiện có, trigger, artifact/version và môi trường. Dùng pipeline build/test/package rõ đầu vào; không nhúng secret. Phân biệt build artifact với deploy artifact, giảm việc build lại khác phiên bản khi release. Không tạo workflow auto-deploy nếu chỉ được giao CI. Thay cấu hình phải nêu default, biến bắt buộc và tác động, không đưa giá trị secret thật vào tài liệu.

## Backup/restore

Xác định dữ liệu trong phạm vi, lịch/retention đã được duyệt, mã hóa/quyền và nơi lưu. Backup thành công không chứng minh restore thành công: thử restore trong môi trường riêng và kiểm tra consistency, schema, file upload liên quan. Không restore đè production để kiểm tra. RPO/RTO chưa được chốt phải ghi chưa quyết định; không tự đặt SLA.

## Sự cố

Ghi triệu chứng, thời điểm và phiên bản; ưu tiên kiểm tra chỉ đọc để xác định ảnh hưởng. Mitigation/restart/rollback chỉ trong phạm vi đã giao; không suy ra quyền từ yêu cầu “theo dõi”. Giữ bằng chứng trước thay đổi, ghi timeline và kiểm chứng phục hồi. Chẩn đoán sâu dùng debugging. Không gửi thông báo bên ngoài khi chưa được giao.

Kế hoạch vận hành và bằng chứng thực thi phải tách rõ; release-readiness đánh giá đủ điều kiện, deployment thực hiện phát hành.
