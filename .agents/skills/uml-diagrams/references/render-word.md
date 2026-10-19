# Render, kích thước Word và lưu artifact

## Hợp đồng đầu ra

Ưu tiên đường dẫn/khổ trang do người dùng cung cấp. Nếu chưa có, mặc định A4 dọc, lề 2.5 cm, vùng nội dung rộng 16 cm; trừ chiều cao caption/header/footer trước khi bố trí. Khổ ngang chỉ dùng khi phù hợp tài liệu. Đây là quy ước thực hành, không phải tiêu chuẩn UML.

Mỗi sơ đồ có slug ổn định:
- `docs/diagrams/uml/<slug>/<slug>.puml`: mã nguồn.
- `docs/diagrams/uml/<slug>/<slug>.png`: ảnh tương thích Word.
- `docs/diagrams/uml/<slug>/<slug>.svg`: bản vector nếu công cụ hỗ trợ.
- `docs/diagrams/uml/<slug>/render-notes.md`: nguồn, loại/trạng thái mô hình, renderer/version, lệnh, kích thước, kết quả kiểm tra.

Giữ artifact hiện hữu; kiểm tra nguồn và phạm vi trước khi cập nhật cùng slug. Hình phân rã dùng suffix overview/detail-01… và ghi mapping. Không ghi vào docs/outputs hoặc chỉnh DOCX nếu chưa có nhiệm vụ xuất/chỉnh Word.

## Chữ sau khi chèn quan trọng hơn số pixel

Mục tiêu chữ nhỏ nhất 10–11 pt tại kích thước chèn, tiêu đề 12–14 pt; đường nối vẫn rõ khi in xám. Đây là tiêu chí nội bộ, có thể đổi theo mẫu Word.

PNG dùng khoảng 300 DPI tại kích thước chèn: rộng 16 cm tương đương khoảng 1890 pixel. Chiều cao giữ tỉ lệ và phải vừa vùng trang. DPI cao giúp sắc nét, không tăng kích thước vật lý của chữ.

Ước lượng: `cỡ chữ pt = chiều cao em chữ theo pixel × 72 × chiều rộng chèn inch / chiều rộng ảnh pixel`. Ví dụ ảnh rộng 1890 px chèn 16 cm cần em chữ khoảng 42 px để tương đương 10 pt. Chiều cao nét chữ nhìn thấy không hoàn toàn bằng em; phải kiểm tra trực quan. Nếu ảnh quá cao, Word thu nhỏ thêm để vừa trang thì tính lại theo kích thước thực tế.

Nếu không đạt: bớt chi tiết phụ vào bảng đặc tả, ngắt nhãn hợp lý, tách overview/detail hoặc đổi hướng trang phù hợp. Không xóa quan hệ quan trọng hoặc thu nhỏ chữ để ép vào một hình.

## Công cụ và lệnh render

Mặc định PlantUML local, UTF-8, font có tiếng Việt (ví dụ Arial nếu máy có). Kiểm tra Java, đường dẫn JAR, phiên bản và Graphviz nếu layout cần nó. Có thể dùng renderer PlantUML sẵn có của môi trường; không cài/chỉnh PATH toàn máy chỉ để thử. Nếu thiếu, báo dependency cụ thể và trạng thái NOT RUN; không khẳng định đã tạo ảnh.

Ví dụ PowerShell, thay đường dẫn bằng đường dẫn thực đã kiểm tra:

```powershell
java -version
java -jar 'C:/tools/plantuml.jar' -version
java -jar 'C:/tools/plantuml.jar' -help
java -jar 'C:/tools/plantuml.jar' -charset UTF-8 -failfast2 -tpng 'C:/work/project/docs/diagrams/uml/example/example.puml'
java -jar 'C:/tools/plantuml.jar' -charset UTF-8 -failfast2 -tsvg 'C:/work/project/docs/diagrams/uml/example/example.puml'
```

Kiểm tra option với phiên bản local; không chạy nguyên đường dẫn ví dụ. Lệnh xuất cạnh file nguồn; không thêm tên output trong @startuml nếu muốn giữ basename. Kiểm tra exit code từng lệnh, timestamp và file sinh ra; PlantUML có thể sinh ảnh lỗi. Tài liệu: [PlantUML CLI](https://plantuml.com/command-line).

Khởi đầu nguồn với @startuml / @enduml, font mặc định, nền trắng; `skinparam dpi 300` khi xuất PNG. Không ép scale gây tràn vùng trang. Không dùng include từ URL hoặc gửi nội dung tới server công cộng nếu chưa được cho phép.

## Vòng kiểm tra

1. Render thành công; mở PNG/SVG bằng công cụ xem ảnh phù hợp.
2. Xem toàn hình và các vùng dày chữ: tiếng Việt, cắt nhãn, giao cắt cạnh, hướng mũi tên, multiplicity, khoảng trắng.
3. Kiểm tra kích thước dự kiến khi chèn. Nếu có nhiệm vụ tạo DOCX, đặt chiều rộng rõ ràng, giữ tỉ lệ, xuất trang xem trước/PDF bằng công cụ sẵn có và kiểm tra ở 100% hoặc mức đọc trang bình thường.
4. Nếu chưa có Word/PDF preview, ghi “đã kiểm tra ảnh và kích thước dự kiến; chưa kiểm tra trong Word”; không gán PASS cho bước chưa chạy.
5. Sửa mã rồi render lại khi lỗi. Bàn giao mã cùng ảnh cuối, không chỉ ảnh; ghi đường dẫn chính xác và trạng thái từng bước.
