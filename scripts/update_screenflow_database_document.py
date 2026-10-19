from __future__ import annotations

from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt
from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
SOURCE = Path(
    r"C:\Users\LENOVO\Downloads\Tai lieu du an\06_GenAI_SoftwareDevelopment_screenflow_db_updated.docx"
)
OUTPUT_DIR = ROOT / "docs" / "outputs"
OUTPUT = OUTPUT_DIR / "06_GenAI_SoftwareDevelopment_screenflow_db_srs_ord_aligned.docx"
ERD_DIR = ROOT / "docs" / "diagrams" / "erd" / "screenflow-database"
ERD_PNG = ERD_DIR / "screenflow-database-erd.png"
PROFILE_ACTIVITY = (
    ROOT / "docs" / "diagrams" / "uml" / "srs-use-cases" / "uc005-profile-activity.png"
)


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    name = "arialbd.ttf" if bold else "arial.ttf"
    return ImageFont.truetype(str(Path(r"C:\Windows\Fonts") / name), size)


def draw_erd() -> None:
    ERD_DIR.mkdir(parents=True, exist_ok=True)
    image = Image.new("RGB", (3600, 2450), "white")
    draw = ImageDraw.Draw(image)
    title_font = font(58, True)
    heading_font = font(32, True)
    body_font = font(25)
    small_font = font(22)

    draw.text(
        (1800, 70),
        "ERD SỔ CHI TIÊU — AS-BUILT VÀ THIẾT KẾ MỤC TIÊU",
        fill="#17324D",
        font=title_font,
        anchor="ma",
    )
    draw.rounded_rectangle((180, 145, 1660, 255), 18, fill="#EAF4FF", outline="#2F75B5", width=4)
    draw.text((220, 176), "Xanh: đã có trong model/migration 0001–0003", fill="#17324D", font=body_font)
    draw.rounded_rectangle((1940, 145, 3420, 255), 18, fill="#FFF4E5", outline="#C77800", width=4)
    draw.text((1980, 176), "Cam/nét đứt: thiết kế mục tiêu, chưa có đủ migration", fill="#6B3D00", font=body_font)

    boxes: dict[str, tuple[int, int, int, int]] = {
        "users": (1280, 330, 2320, 750),
        "categories": (80, 940, 730, 1390),
        "transactions": (790, 940, 1440, 1390),
        "budgets": (1500, 940, 2150, 1390),
        "saving_goals": (2210, 940, 2820, 1390),
        "ai_conversations": (2870, 330, 3530, 750),
        "goal_items": (1990, 1710, 2650, 2100),
        "goal_transactions": (2730, 1710, 3490, 2140),
        "ai_messages": (2890, 940, 3540, 1450),
    }
    fields = {
        "users": [
            "PK id: UUID string", "username, email", "username_normalized [đã có]",
            "email_normalized [đã có]", "display_name, password_hash", "avatar_url, created_at",
            "reset_token_hash/expiry",
        ],
        "categories": [
            "PK id", "FK user_id → users", "name", "name_normalized [đã có]",
            "type, color, icon", "UQ(user_id,type,name_norm) [đã có]",
        ],
        "transactions": [
            "PK id", "FK user_id → users", "FK category_id → categories",
            "amount, type, txn_date, note", "FK(category_id,user_id) [mục tiêu]",
        ],
        "budgets": [
            "PK id", "FK user_id → users", "FK category_id → categories",
            "month, year, limit_amount", "CHECK year 2000–2100 [đã có]",
            "UQ owner/category/period [mục tiêu]",
        ],
        "saving_goals": [
            "PK id", "FK user_id → users", "name, target_amount, deadline", "status",
            "completion_amount/mode",
        ],
        "goal_items": ["PK id", "FK goal_id → saving_goals", "name, cost, is_purchased"],
        "goal_transactions": [
            "PK id", "FK goal_id → saving_goals", "amount, type, txn_date, note",
        ],
        "ai_conversations": [
            "PK id", "FK user_id → users", "title", "created_at, updated_at",
        ],
        "ai_messages": [
            "PK id", "FK conversation_id → ai_conversations", "role, content",
            "context_month/year", "evidence_json, created_at",
        ],
    }

    def box(name: str) -> None:
        x1, y1, x2, y2 = boxes[name]
        draw.rounded_rectangle((x1, y1, x2, y2), 22, fill="#F8FBFE", outline="#2F75B5", width=5)
        draw.rectangle((x1, y1, x2, y1 + 70), fill="#2F75B5")
        draw.text(((x1 + x2) // 2, y1 + 34), name.upper(), fill="white", font=heading_font, anchor="mm")
        y = y1 + 92
        for value in fields[name]:
            color = "#9C5700" if "[mục tiêu]" in value else "#1F1F1F"
            draw.text((x1 + 24, y), value, fill=color, font=small_font)
            y += 43

    for name in boxes:
        box(name)

    def center_bottom(name: str) -> tuple[int, int]:
        x1, _y1, x2, y2 = boxes[name]
        return ((x1 + x2) // 2, y2)

    def center_top(name: str) -> tuple[int, int]:
        x1, y1, x2, _y2 = boxes[name]
        return ((x1 + x2) // 2, y1)

    def relation(
        start: tuple[int, int],
        end: tuple[int, int],
        label: str,
        target: bool = False,
        label_offset_y: int = 0,
    ) -> None:
        color = "#C77800" if target else "#456B8A"
        width = 6 if target else 5
        draw.line((start, end), fill=color, width=width)
        ex, ey = end
        draw.polygon(((ex, ey), (ex - 16, ey - 28), (ex + 16, ey - 28)), fill=color)
        mx, my = (start[0] + end[0]) // 2, (start[1] + end[1]) // 2 + label_offset_y
        bbox = draw.textbbox((0, 0), label, font=small_font)
        pad = 9
        draw.rounded_rectangle(
            (mx - (bbox[2] - bbox[0]) // 2 - pad, my - 22, mx + (bbox[2] - bbox[0]) // 2 + pad, my + 22),
            8,
            fill="white",
            outline=color,
            width=2,
        )
        draw.text((mx, my), label, fill=color, font=small_font, anchor="mm")

    user_bottom = center_bottom("users")
    for child in ("categories", "transactions", "budgets", "saving_goals"):
        relation(user_bottom, center_top(child), "1 — N / CASCADE mục tiêu", target=True)
    relation((2320, 540), (2870, 540), "1 — N / CASCADE mục tiêu", target=True)
    relation(center_bottom("saving_goals"), center_top("goal_items"), "1 — N / CASCADE mục tiêu", target=True)
    relation(center_bottom("saving_goals"), center_top("goal_transactions"), "1 — N / CASCADE mục tiêu", target=True)
    relation(center_bottom("ai_conversations"), center_top("ai_messages"), "1 — N / CASCADE mục tiêu", target=True)
    relation((730, 1120), (790, 1120), "RESTRICT + owner", target=True, label_offset_y=-85)
    relation((730, 1270), (1500, 1270), "RESTRICT + owner", target=True, label_offset_y=-85)

    draw.text(
        (180, 2305),
        "Ghi chú: RQ-009 không làm phát sinh bảng USER mới. RQ-011 dùng hard delete dữ liệu active theo owner; "
        "backup hết retention tối đa 30 ngày.",
        fill="#404040",
        font=body_font,
    )
    image.save(ERD_PNG, dpi=(300, 300))


def set_update_fields(document: Document) -> None:
    settings = document.settings._element
    update = settings.find(qn("w:updateFields"))
    if update is None:
        update = OxmlElement("w:updateFields")
        settings.append(update)
    update.set(qn("w:val"), "true")


def set_paragraph_text(paragraph, text: str) -> None:
    for child in list(paragraph._p):
        if child.tag != qn("w:pPr"):
            paragraph._p.remove(child)
    run = paragraph.add_run(text)
    run.font.name = "Times New Roman"
    run.font.size = Pt(13)


def insert_before(reference, text: str = "", style: str = "Normal"):
    paragraph = reference.insert_paragraph_before(text)
    paragraph.style = style
    for run in paragraph.runs:
        run.font.name = "Times New Roman"
        run.font.size = Pt(13)
    return paragraph


def add_table_row(table, values: tuple[str, str, str, str]) -> None:
    row = table.add_row()
    for cell, value in zip(row.cells, values, strict=True):
        cell.text = value
        for paragraph in cell.paragraphs:
            for run in paragraph.runs:
                run.font.name = "Times New Roman"
                run.font.size = Pt(12)


def replace_picture_by_part(document: Document, part_name: str, image_path: Path, width: Cm) -> None:
    for paragraph in document.paragraphs:
        for blip in paragraph._p.xpath(".//a:blip"):
            relationship_id = blip.get(qn("r:embed"))
            related_part = document.part.related_parts[relationship_id]
            if str(related_part.partname) == part_name:
                for child in list(paragraph._p):
                    if child.tag != qn("w:pPr"):
                        paragraph._p.remove(child)
                paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
                paragraph.add_run().add_picture(str(image_path), width=width)
                return
    raise KeyError(part_name)


def update_document() -> None:
    document = Document(SOURCE)

    replacements = {
        "Tên ứng dụng: Hệ thống quản lý bán hàng có tích hợp AI": "Tên ứng dụng: Sổ chi tiêu — Hệ thống quản lý chi tiêu cá nhân tích hợp AI",
        "11": "11",
        "Quản lý thông tin cá nhân người dùng": "Quản lý hồ sơ, ảnh đại diện, đổi mật khẩu và xóa tài khoản theo UC005/RQ-011",
    }
    for paragraph in document.paragraphs:
        value = paragraph.text.strip()
        if value in replacements:
            set_paragraph_text(paragraph, replacements[value])

    for paragraph in document.paragraphs:
        text = paragraph.text.strip()
        if text.startswith("Ứng dụng chia làm hai vùng:"):
            set_paragraph_text(
                paragraph,
                "Ứng dụng chia làm hai vùng: vùng công khai phục vụ xác thực (Đăng nhập, Đăng ký, Quên mật khẩu) "
                "và vùng đã xác thực nằm trong AppShell. Theo RQ-009, tất cả tương tác thuộc một tác nhân Người sử dụng; "
                "bản ghi USER chỉ tồn tại sau đăng ký và không mất đi khi đăng xuất. AppShell dẫn tới Dashboard, Giao dịch, "
                "Danh mục, Ngân sách, Mục tiêu, Báo cáo, Trợ lý AI và khu vực Quản lý hồ sơ. Khi mất kết nối, ứng dụng "
                "không được báo thành công giả, giữ dữ liệu nhập khi phù hợp và cho phép thử lại.",
            )
        elif text.startswith("Người dùng nhập email đã đăng ký để yêu cầu đặt lại mật khẩu;"):
            set_paragraph_text(
                paragraph,
                "Người sử dụng nhập email đã đăng ký để yêu cầu khôi phục mật khẩu. Hệ thống phản hồi trung tính để không "
                "tiết lộ tài khoản có tồn tại hay không. Liên kết đặt lại có thời hạn theo chính sách được phê duyệt; baseline "
                "hiện chưa ấn định con số cụ thể. Token sai hoặc hết hạn bị từ chối và người sử dụng có thể gửi yêu cầu mới; "
                "đặt lại thành công chuyển về màn hình Đăng nhập.",
            )
        elif text.startswith("Từ khu vực avatar ở AppShell"):
            set_paragraph_text(
                paragraph,
                "Từ khu vực avatar ở AppShell, bảng Quản lý hồ sơ mở mà không làm mất màn hình nghiệp vụ đang xem. Người "
                "sử dụng có thể cập nhật tên hiển thị, quản lý ảnh đại diện, đổi mật khẩu bằng mật khẩu hiện tại và mở vùng "
                "nguy hiểm để xóa tài khoản. Quy tắc MIME, dung lượng, quota và xử lý ảnh chỉ được mô tả sau khi có quyết định "
                "được phê duyệt; tài liệu này không tự đặt thêm chính sách upload.",
            )

    # Update the screen list row without creating a fictitious standalone screen.
    screen_table = document.tables[0]
    for row in screen_table.rows:
        if row.cells[0].text.strip() == "11":
            row.cells[1].text = "Quản lý hồ sơ"
            row.cells[2].text = "Cập nhật hồ sơ/avatar, đổi mật khẩu và xóa tài khoản theo UC005"

    logout_heading = next(p for p in document.paragraphs if p.text.strip() == "1.2.11. Luồng đăng xuất")
    new_heading = insert_before(logout_heading, "1.2.11. Luồng đổi mật khẩu và xóa tài khoản", "Heading 3")
    insert_before(
        logout_heading,
        "Đổi mật khẩu là chức năng con của UC005: người sử dụng nhập mật khẩu hiện tại, mật khẩu mới và xác nhận; dữ liệu "
        "chỉ thay đổi khi mọi kiểm tra hợp lệ. Xóa tài khoản là UC005e theo RQ-011: người sử dụng phải đang đăng nhập, nhập "
        "đúng mật khẩu hiện tại và chuỗi XÓA TÀI KHOẢN trong cùng yêu cầu. Backend lấy danh tính từ phiên, hard delete toàn "
        "bộ dữ liệu active đúng owner trong một transaction; lỗi quan hệ phải rollback. Sau commit, avatar được dọn idempotent, "
        "client xóa token/cache/bản nháp và chuyển về vùng công khai. Đây là thiết kế mục tiêu, chưa phải bằng chứng implementation.",
    )
    picture = insert_before(logout_heading)
    picture.alignment = WD_ALIGN_PARAGRAPH.CENTER
    picture.add_run().add_picture(str(PROFILE_ACTIVITY), width=Cm(16))
    caption = insert_before(logout_heading, "Hình 22. Activity diagram UC005e — xóa tài khoản (thiết kế mục tiêu)")
    caption.alignment = WD_ALIGN_PARAGRAPH.CENTER
    set_paragraph_text(logout_heading, "1.2.12. Luồng đăng xuất")
    old_logout_caption = next(p for p in document.paragraphs if p.text.strip() == "Hình 22. Luồng đăng xuất")
    set_paragraph_text(old_logout_caption, "Hình 23. Luồng đăng xuất")

    erd_intro = next(p for p in document.paragraphs if p.text.strip().startswith("Sơ đồ dưới đây thể hiện các bảng"))
    set_paragraph_text(
        erd_intro,
        "Sơ đồ phân biệt màu xanh là cấu trúc đã có trong models/migrations 0001–0003 và màu cam là constraint thiết kế "
        "mục tiêu đã được Database Gate chấp thuận nhưng chưa có đủ migration. USERS là bảng tài khoản đã đăng ký; theo "
        "RQ-009, đăng xuất chỉ kết thúc phiên và không xóa bản ghi USER.",
    )
    replace_picture_by_part(document, "/word/media/image24.png", ERD_PNG, Cm(16))
    erd_caption = next(p for p in document.paragraphs if p.text.strip() == "Hình 23. Sơ đồ quan hệ tổng quát (ERD)")
    set_paragraph_text(erd_caption, "Hình 24. ERD as-built và thiết kế mục tiêu")

    add_table_row(document.tables[1], ("username_normalized", "VARCHAR", "NOT NULL, UNIQUE (đã có 0002)", "NFKC → trim → case-fold của username"))
    add_table_row(document.tables[1], ("email_normalized", "VARCHAR", "NOT NULL, UNIQUE (đã có 0002)", "NFKC → trim → case-fold của email"))
    add_table_row(document.tables[2], ("name_normalized", "VARCHAR", "NOT NULL; UQ theo owner/type (đã có 0003)", "Khóa chuẩn hóa tên danh mục"))
    for row in document.tables[4].rows:
        if row.cells[0].text.strip() == "year":
            row.cells[2].text = "NOT NULL, CHECK 2000–2100 (đã có 0003)"
        elif row.cells[0].text.strip() == "limit_amount":
            row.cells[2].text = "NOT NULL; CHECK > 0 (thiết kế mục tiêu)"

    unique_heading = next(p for p in document.paragraphs if p.text.strip() == "2.2.3. Ràng buộc duy nhất")
    for paragraph in document.paragraphs:
        if paragraph.text.strip() == "– Tên đăng nhập USERS.username.":
            set_paragraph_text(paragraph, "– USERS.username_normalized và USERS.email_normalized là unique key đã có từ migration 0002.")
        elif paragraph.text.strip() == "– Email USERS.email.":
            set_paragraph_text(paragraph, "– CATEGORIES(user_id, type, name_normalized) là unique key đã có từ migration 0003; BUDGETS(user_id, category_id, month, year) là thiết kế mục tiêu.")

    domain_heading = next(p for p in document.paragraphs if p.text.strip() == "2.2.4. Ràng buộc miền giá trị")
    note = insert_before(
        domain_heading,
        "Trạng thái FK: các FK đơn đã tồn tại nhưng models/migrations hiện chưa khai báo đầy đủ ON DELETE. Thiết kế mục tiêu "
        "dùng CASCADE từ USERS tới dữ liệu thuộc tài khoản và từ SAVING_GOALS/AI_CONVERSATIONS tới bảng con; tham chiếu "
        "TRANSACTIONS/BUDGETS tới CATEGORIES dùng composite FK (category_id, user_id) và RESTRICT để ngăn tham chiếu chéo owner.",
    )
    note.style = "Normal"

    business_heading = next(p for p in document.paragraphs if p.text.strip() == "2.2.5. Ràng buộc nghiệp vụ")
    insert_before(
        business_heading,
        "Các CHECK còn lại như amount > 0, miền type/role, tháng 1–12, limit_amount > 0 và cặp context_month/context_year "
        "thuộc thiết kế mục tiêu nếu chưa xuất hiện trong migrations. Không trình bày chúng như schema đã triển khai.",
    )
    for row in document.tables[11].rows:
        if row.cells[0].text.strip() == "BUDGETS.limit_amount":
            row.cells[1].text = "Phải lớn hơn 0 (thiết kế mục tiêu)"
        elif row.cells[0].text.strip() == "BUDGETS.month":
            row.cells[1].text = "Trong khoảng 1–12; year trong 2000–2100 (year đã có 0003)"
        elif row.cells[0].text.strip() == "GOAL_ITEMS.cost":
            row.cells[1].text = "Phải lớn hơn 0 (thiết kế mục tiêu)"

    conclusion = next(p for p in document.paragraphs if p.text.strip() == "Kết luận")
    conclusion.style = "Heading 1"
    last = document.paragraphs[-1]
    set_paragraph_text(
        last,
        "Screen Flow đã được đồng bộ với RQ-009, RQ-010 và RQ-011: một tác nhân Người sử dụng, USER độc lập với phiên, "
        "đổi mật khẩu và xóa tài khoản nằm trong UC005, cùng hành vi lỗi kết nối không báo thành công giả. ERD và mô tả "
        "CSDL phân biệt rõ phần đã triển khai qua migrations 0001–0003 với constraint thiết kế mục tiêu còn cần migration "
        "và kiểm chứng PostgreSQL. Tài liệu không được dùng như bằng chứng rằng chức năng xóa tài khoản, retention backup hoặc "
        "toàn bộ cascade/ownership constraint đã vận hành.",
    )

    set_update_fields(document)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    document.save(OUTPUT)


def main() -> None:
    for path in (SOURCE, PROFILE_ACTIVITY):
        if not path.is_file():
            raise FileNotFoundError(path)
    draw_erd()
    update_document()
    print(ERD_PNG)
    print(OUTPUT)


if __name__ == "__main__":
    main()
