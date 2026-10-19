# Chọn loại và kiểm tra ký hiệu UML

Nguồn ngữ nghĩa: [OMG UML 2.5.1](https://www.omg.org/spec/UML/2.5.1). PlantUML là renderer; render thành công không chứng minh mô hình đúng UML.

| Câu hỏi | Loại | Phần tử và kiểm tra chính |
|---|---|---|
| Ai dùng chức năng nào? | Use case | Actor ngoài system boundary, ellipse cho mục tiêu, association với actor |
| Các lớp có cấu trúc và trách nhiệm gì? | Class | Hộp lớp, thuộc tính/phương thức, quan hệ và multiplicity |
| Ai gọi ai theo thời gian? | Sequence | Lifeline, message, activation khi cần, fragments |
| Luồng công việc rẽ nhánh/song song thế nào? | Activity | Action, control flow, decision/merge, fork/join, final |
| Một đối tượng đổi trạng thái khi nào? | State machine | State, transition, trigger/guard/effect, initial/final |
| Thành phần cung cấp/phụ thuộc giao diện nào? | Component | Component, interface cung cấp/yêu cầu, dependency/connector |
| Phần mềm được đặt và kết nối ở đâu? | Deployment | Node/device/execution environment, artifact, deployment, communication path |

## Use case

Actor là vai trò tương tác, không phải lớp dữ liệu hoặc mỗi màn hình. Association là đường liền, không phải thứ tự thực hiện.

- Include: nét đứt, mũi tên từ use case bao gồm đến use case được bao gồm, nhãn «include»; hành vi được chèn vào use case chính.
- Extend: nét đứt từ use case mở rộng đến use case cơ sở, nhãn «extend»; nêu điều kiện/extension point thích hợp.
- Generalization: đường liền, tam giác rỗng hướng về phần tử tổng quát.
- Phân nhóm chức năng không đồng nghĩa include; không include đồng thời thêm/sửa/xóa chỉ vì thuộc CRUD.
- Điều kiện đã xác thực đặt ở đặc tả/note; Đăng nhập không mặc định thực hiện lại cho mỗi chức năng.

Ví dụ cú pháp: `A ..> B : <<include>>`; `Extra ..> Base : <<extend>>`. Nguồn: [PlantUML use case](https://plantuml.com/use-case-diagram).

## Class

Ghi tên, thuộc tính `name: Type`, operation `name(arg: Type): ReturnType` theo mức chi tiết cần thiết. Visibility: `+` public, `-` private, `#` protected, `~` package; không đoán visibility nếu mã/ngôn ngữ không quy định tương ứng.

- Association: đường liền; navigability nếu thực sự cần, không dùng như dependency một cách tùy tiện.
- Dependency: nét đứt, mũi tên hướng về bên được sử dụng.
- Generalization: đường liền, tam giác rỗng về cha; realization: nét đứt, tam giác rỗng về interface.
- Aggregation: thoi rỗng phía whole; composition: thoi đặc phía whole. Chỉ dùng khi ngữ nghĩa whole–part/lifecycle phù hợp, không suy ra từ mọi foreign key.
- Multiplicity `1`, `0..1`, `0..*`, `1..*` đặt đúng đầu; tên role khi cần.
- Entity không bắt buộc có phương thức chỉ để lấp ô. Không biến hàm router/module thành member của User trong sơ đồ As-built. PK/FK nếu thêm là chú giải dữ liệu; không thay quan hệ UML bằng ký hiệu ERD mà không giải thích.

Nguồn cú pháp: [PlantUML class](https://plantuml.com/class-diagram).

## Sequence

Thời gian từ trên xuống; lifeline có tên/vai trò rõ. Lời gọi đồng bộ có đầu mũi tên kín, bất đồng bộ đầu mở; return thường nét đứt. Kiểm tra ký hiệu renderer đang dùng, không coi mọi mũi tên giống nhau. Activation biểu diễn thời gian thực thi, không trang trí toàn lifeline.

Dùng `alt/else` cho lựa chọn, `opt` cho tùy chọn, `loop` cho lặp, `par` cho song song khi có căn cứ. Guard đặt rõ trong nhánh. Không vẽ UI truy cập database trực tiếp nếu hiện trạng đi qua API. Nguồn: [PlantUML sequence](https://plantuml.com/sequence-diagram).

## Activity

Initial là chấm đặc; activity final là chấm trong vòng tròn; flow final kết thúc một flow, không đồng nghĩa kết thúc toàn activity. Action là hộp bo góc; decision/merge hình thoi. Nhánh ra decision có guard rõ, gồm else nếu cần; fork/join dùng thanh đồng bộ, không thay bằng decision. Swimlane phân trách nhiệm, không là ranh giới bảo mật. Nguồn: [PlantUML activity](https://plantuml.com/activity-diagram-beta).

## State machine

State là tình trạng tồn tại của đối tượng, không đơn thuần đổi tên mỗi action. Transition ghi `trigger [guard] / effect`; phân biệt entry/do/exit nếu cần. Initial/final, composite state và choice dùng đúng ý nghĩa; không trộn trạng thái tài khoản tồn tại với trạng thái phiên đăng nhập. Nguồn: [PlantUML state](https://plantuml.com/state-diagram).

## Component và Deployment

Component: component rectangle có ký hiệu hoặc «component»; lollipop là provided interface, socket là required interface. Dependency hướng bên sử dụng → bên được dùng; một package không tự là runtime service.

Deployment: node và execution environment biểu diễn nơi chạy; artifact biểu diễn phần mềm triển khai. Communication path nối node; quan hệ deployment của artifact không phải lời gọi theo thời gian. Không dùng hộp class để thay mọi node hoặc bịa hạ tầng production. Nguồn: [component](https://plantuml.com/component-diagram), [deployment](https://plantuml.com/deployment-diagram).

## Loại khác

Object, package, composite structure, communication, interaction overview, timing và profile cần tra mục tương ứng của OMG và khả năng renderer trước khi dùng. Ghi giới hạn nếu renderer không hỗ trợ ký hiệu cần thiết; không thay bằng loại gần giống rồi gọi là đúng loại yêu cầu.
