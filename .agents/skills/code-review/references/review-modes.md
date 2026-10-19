# Review theo phạm vi và hồi quy

Diff nhỏ: đọc patch và phần ngữ cảnh quanh đó, caller trực tiếp, test; tìm hành vi bị đổi ngoài ý định. Không chỉ tìm lỗi ở các dòng thêm, cũng xem dòng xóa và điều kiện không còn.

Thay đổi nhiều tầng: lần theo contract UI → API → validation → auth/ownership → persistence → response; kiểm tra tương thích caller và rollback khi lỗi giữa chừng. Đối chiếu migration nếu có, không review schema chỉ từ model mới.

Hồi quy: kiểm tra nhánh cũ còn hoạt động, error handling không che lỗi, cache/session không lẫn account, giá trị mặc định/null có đổi nghĩa không. Ưu tiên bằng chứng tái hiện hoặc lập luận đường đi cụ thể.

Finding cần vị trí, trigger, tác động và cách xác minh. Severity theo hậu quả, không theo sở thích cá nhân. Phân biệt lỗi mới với lỗi có sẵn; không tự sửa khi chỉ review. Nếu không đủ evidence, ghi risk/question thay vì confirmed.
