from copy import deepcopy
from pathlib import Path
from tempfile import NamedTemporaryFile
from zipfile import ZIP_DEFLATED, ZipFile
import re

from docx import Document
from docx.enum.text import WD_BREAK
from docx.oxml.ns import qn
from docx.shared import Cm, Pt
from docx.text.paragraph import Paragraph


ROOT = Path(__file__).resolve().parents[1]
SOURCE = Path(
    r"C:\Users\LENOVO\Downloads\Tai lieu du an\03_GenAI_SoftwareDevelopment_requirements-specification_updated (1).docx"
)
OUTPUT = ROOT / "docs" / "outputs" / "03_GenAI_SoftwareDevelopment_requirements-specification.docx"
DIAGRAM_DIR = ROOT / "docs" / "diagrams" / "uml" / "srs-use-cases"


def set_paragraph_text(paragraph, text):
    paragraph.clear()
    paragraph.add_run(text)


def insert_paragraph_after(paragraph, text, style=None):
    new_p = deepcopy(paragraph._p)
    for child in list(new_p):
        if child.tag.endswith("}r") or child.tag.endswith("}hyperlink"):
            new_p.remove(child)
    paragraph._p.addnext(new_p)
    result = Paragraph(new_p, paragraph._parent)
    if style:
        result.style = style
    set_paragraph_text(result, text)
    return result


def replace_drawing(paragraph, image_path, width_cm):
    paragraph.clear()
    paragraph.alignment = 1
    paragraph.add_run().add_picture(str(image_path), width=Cm(width_cm))


def table_key(table, row_index):
    return table.cell(row_index, 0).text.strip().lower()


def set_spec_value(table, label, value):
    wanted = label.strip().lower()
    for row_index in range(len(table.rows)):
        if table_key(table, row_index) == wanted:
            table.cell(row_index, 1).text = value
            return
    raise ValueError(f"Missing specification row: {label}")


def set_run_font(run):
    run.font.name = "Times New Roman"
    run.font.size = Pt(13)
    run._element.get_or_add_rPr().rFonts.set(qn("w:eastAsia"), "Times New Roman")


def apply_document_font(document):
    for style in document.styles:
        if hasattr(style, "font"):
            style.font.name = "Times New Roman"
            style.font.size = Pt(13)
            style._element.get_or_add_rPr().rFonts.set(qn("w:eastAsia"), "Times New Roman")

    containers = [document]
    for section in document.sections:
        containers.extend([section.header, section.footer])

    for container in containers:
        for paragraph in container.paragraphs:
            for run in paragraph.runs:
                set_run_font(run)
        for table in container.tables:
            for row in table.rows:
                for cell in row.cells:
                    for paragraph in cell.paragraphs:
                        for run in paragraph.runs:
                            set_run_font(run)


def patch_embedded_svg(docx_path):
    """Synchronize actor names, UC identifiers and font in legacy embedded diagrams."""
    with ZipFile(docx_path, "r") as source, NamedTemporaryFile(delete=False, suffix=".docx") as temp_file:
        temp_path = Path(temp_file.name)
        with ZipFile(temp_file, "w", ZIP_DEFLATED) as target:
            for item in source.infolist():
                data = source.read(item.filename)
                if item.filename.startswith("word/media/") and item.filename.endswith(".svg"):
                    svg = data.decode("utf-8")
                    svg = svg.replace("Khách", "Người sử dụng")
                    svg = svg.replace("Người dùng", "Người sử dụng")

                    def shift_uc(match):
                        old_id = int(match.group(1))
                        return f"UC{old_id + 1:03d}" if 3 <= old_id <= 11 else match.group(0)

                    svg = re.sub(r"UC(\d{3})", shift_uc, svg)
                    data = svg.encode("utf-8")
                target.writestr(item, data)
    temp_path.replace(docx_path)


document = Document(SOURCE)

# Capture the original UC003 position before renumbering. UC003 Logout is inserted here.
original_uc003_heading = next(p for p in document.paragraphs if p.text.strip().startswith("UC003"))

# Overview prose and list: one actor, separate Login and Logout use cases.
overview_text = next(p for p in document.paragraphs if p.text.strip().startswith("Hệ thống được xây dựng với một tác nhân chính"))
set_paragraph_text(
    overview_text,
    "Hệ thống có một tác nhân chính là Người sử dụng, đại diện cho cá nhân tương tác với hệ thống trước và sau khi xác thực. Google Gemini và Resend là các tác nhân ngoài hệ thống tham gia lần lượt vào chức năng trợ lý AI và khôi phục mật khẩu. Các chức năng bảo vệ yêu cầu tài khoản đã đăng ký và phiên xác thực hợp lệ; Đăng nhập là use case độc lập.",
)

combined_item = next(p for p in document.paragraphs if p.text.strip() == "Đăng nhập và đăng xuất.")
set_paragraph_text(combined_item, "Đăng nhập.")
insert_paragraph_after(combined_item, "Đăng xuất.", style=combined_item.style)

# Replace the overview diagram, retaining the template paragraph and width.
overview_heading_index = next(i for i, p in enumerate(document.paragraphs) if p.text.strip() == "Mô hình Use case")
overview_drawing = next(
    p for p in document.paragraphs[overview_heading_index + 1:]
    if "<w:drawing" in p._p.xml or "<w:pict" in p._p.xml
)
replace_drawing(overview_drawing, DIAGRAM_DIR / "srs-use-case-overview.png", 16.0)

# Insert readable use-case decomposition diagrams after the overview.
actor_section = next(p for p in document.paragraphs if "Danh sách các tác nhân và mô tả" in p.text)
decomposition_marker = actor_section._p
decomposition_heading = document.add_paragraph("Phân rã Use Case", style="Heading 3")
decomposition_intro = document.add_paragraph(
    "Các sơ đồ sau phân rã 12 use case tổng quan thành những mục tiêu tương tác cụ thể; "
    "các use case cấp cao và phạm vi nghiệp vụ ban đầu vẫn được giữ nguyên."
)
for paragraph in (decomposition_heading, decomposition_intro):
    decomposition_marker.addprevious(paragraph._p)

decomposition_figures = [
    ("Tài khoản", "use-case-decomposition-account.png", 16.0),
    ("Danh mục và giao dịch", "use-case-decomposition-finance-1.png", 16.0),
    ("Ngân sách và mục tiêu tiết kiệm", "use-case-decomposition-finance-2.png", 16.0),
    ("Dashboard và báo cáo", "use-case-decomposition-analysis-1.png", 16.0),
    ("Trợ lý AI", "use-case-decomposition-analysis-2.png", 16.0),
]
for label, filename, width_cm in decomposition_figures:
    image_p = document.add_paragraph()
    image_p.alignment = 1
    image_p.paragraph_format.page_break_before = True
    image_p.add_run().add_picture(str(DIAGRAM_DIR / filename), width=Cm(width_cm))
    decomposition_marker.addprevious(image_p._p)

# Merge the two internal actor rows while preserving the two external actors.
actor_table = document.tables[2]
actor_table.cell(1, 0).text = "Người sử dụng"
actor_table.cell(1, 1).text = (
    "Cá nhân tương tác với hệ thống trước và sau xác thực: đăng ký, đăng nhập, khôi phục mật khẩu; "
    "sau khi có phiên hợp lệ thì quản lý hồ sơ và dữ liệu tài chính, sử dụng trợ lý AI và đăng xuất."
)
actor_table.cell(1, 2).text = "Tác nhân chính"
actor_table._tbl.remove(actor_table.rows[2]._tr)

# Preserve use-case order, split Login/Logout, then shift the original UC003–UC011 by one.
uc_table = document.tables[3]
uc_table.cell(1, 2).text = "Cho phép người sử dụng chưa xác thực tạo tài khoản trên hệ thống"
uc_table.cell(2, 1).text = "Đăng nhập"
uc_table.cell(2, 2).text = "Xác thực bằng username/email và mật khẩu; cấp token cho phiên hợp lệ"
for row_index in range(3, 12):
    old_id = row_index
    uc_table.cell(row_index, 0).text = f"UC{old_id + 1:03d}"
uc_table.cell(11, 1).text = "Trợ lý AI"
new_uc_row = uc_table.add_row()
for index, value in enumerate(
    [
        "UC003",
        "Đăng xuất",
        "Kết thúc phiên trên thiết bị, xóa token và thông tin phiên; tài khoản cùng dữ liệu vẫn được giữ nguyên",
        "FR01 – Quản lý tài khoản",
        "",
    ]
):
    new_uc_row.cells[index].text = value
uc_table.rows[3]._tr.addprevious(new_uc_row._tr)

# Normalize actor roles and shift original UC003–UC011 identifiers in detailed specifications.
for table in document.tables[4:15]:
    use_case = table.cell(1, 1).text.strip()
    if "UC003" in use_case:
        actor = "Người sử dụng; Resend"
    elif "UC011" in use_case:
        actor = "Người sử dụng; Google Gemini"
    else:
        actor = "Người sử dụng"
    set_spec_value(table, "Tác nhân", actor)
    if use_case.startswith("UC"):
        old_id = int(use_case[2:5])
        if 3 <= old_id <= 11:
            new_id = old_id + 1
            new_name = use_case.split("–", 1)[1].strip() if "–" in use_case else use_case[5:].strip()
            if old_id == 11:
                new_name = "Trợ lý AI"
            set_spec_value(table, "Use Case", f"UC{new_id:03d} – {new_name}")

# UC005 includes changing the password for an authenticated user as part of profile management.
for row in uc_table.rows[1:]:
    if row.cells[0].text.strip() == "UC005":
        row.cells[2].text = (
            "Sửa tên hiển thị, username, email; tải lên hoặc xóa ảnh đại diện; đổi mật khẩu khi đang đăng nhập"
        )
        break

profile_table = document.tables[7]
set_spec_value(profile_table, "Mục đích", "Quản lý thông tin cá nhân và thông tin bảo mật của tài khoản.")
set_spec_value(
    profile_table,
    "Mô tả",
    "Cho phép người sử dụng đã đăng nhập thay đổi tên hiển thị, username, email, ảnh đại diện hoặc đổi mật khẩu. Đổi mật khẩu là chức năng con của Quản lý hồ sơ, không phải use case tổng quan độc lập.",
)
set_spec_value(
    profile_table,
    "Điều kiện sau",
    "Thông tin hồ sơ, ảnh đại diện hoặc mật khẩu được cập nhật theo thao tác hợp lệ; tài khoản vẫn giữ nguyên.",
)
set_spec_value(
    profile_table,
    "Luồng sự kiện chính (Basic Flows)",
    "B1. Người sử dụng mở khu vực Quản lý hồ sơ.\n"
    "B2. Người sử dụng chọn sửa thông tin, thay đổi ảnh đại diện hoặc đổi mật khẩu.\n"
    "B3. Với thông tin hồ sơ/ảnh đại diện, hệ thống kiểm tra định dạng và tính duy nhất rồi cập nhật.\n"
    "B4. Với đổi mật khẩu, người sử dụng nhập mật khẩu hiện tại, mật khẩu mới và xác nhận mật khẩu mới.\n"
    "B5. Hệ thống xác minh mật khẩu hiện tại, kiểm tra mật khẩu mới và lưu mật khẩu mới dưới dạng băm.\n"
    "B6. Hệ thống thông báo cập nhật thành công.",
)
set_spec_value(
    profile_table,
    "Luồng sự kiện phụ (Alternative Flows)",
    "A1. Username/email trùng → yêu cầu nhập lại.\n"
    "A2. Ảnh đại diện sai định dạng, rỗng hoặc vượt giới hạn → từ chối cập nhật.\n"
    "A3. Mật khẩu hiện tại không đúng → không thay đổi mật khẩu và hiển thị lỗi chung.\n"
    "A4. Mật khẩu mới không đạt chính sách hoặc xác nhận không khớp → yêu cầu nhập lại.",
)

for paragraph in document.paragraphs:
    text = paragraph.text.strip()
    if text.startswith("UC") and len(text) >= 5 and text[2:5].isdigit():
        old_id = int(text[2:5])
        if 3 <= old_id <= 11:
            separator = " – " if "–" in text else "_ "
            name = text.split("–", 1)[1].strip() if "–" in text else text.split("_", 1)[1].strip()
            if old_id == 11:
                name = "Trợ lý AI"
            set_paragraph_text(paragraph, f"UC{old_id + 1:03d}{separator}{name}")

# UC002 now specifies Login only.
login_table = document.tables[5]
set_spec_value(login_table, "Use case", "UC002 – Đăng nhập")
set_spec_value(login_table, "Mục đích", "Xác thực tài khoản để người sử dụng truy cập các chức năng được bảo vệ.")
set_spec_value(
    login_table,
    "Mô tả",
    "Người sử dụng nhập username hoặc email cùng mật khẩu. Hệ thống kiểm tra thông tin với tài khoản đã đăng ký; nếu hợp lệ thì cấp access token, tải hồ sơ hiện tại và chuyển đến Dashboard.",
)
set_spec_value(login_table, "Tác nhân", "Người sử dụng")
set_spec_value(
    login_table,
    "Điều kiện sau",
    "Thành công: token được lưu ở client, hồ sơ hiện tại được tải và Dashboard được mở. Thất bại: không tạo phiên xác thực.",
)
set_spec_value(
    login_table,
    "Luồng sự kiện phụ (Alternative Flows)",
    "A1. Username/email hoặc mật khẩu sai → API trả 401 bằng thông báo chung; biểu mẫu vẫn cho phép nhập lại.\nA2. Không tải được hồ sơ bằng token vừa nhận → client xóa token và trở về trạng thái chưa xác thực.\nA3. Lỗi kết nối → hiển thị thông báo phù hợp và không báo đăng nhập thành công.",
)

# Rename the UC002 section and replace its combined Login/Logout diagrams.
login_heading = next(p for p in document.paragraphs if p.text.strip() == "UC002_ Đăng nhập và đăng xuất")
set_paragraph_text(login_heading, "UC002_ Đăng nhập")
login_heading_index = next(i for i, p in enumerate(document.paragraphs) if p._p is login_heading._p)
login_drawings = [
    p for p in document.paragraphs[login_heading_index + 1:]
    if "<w:drawing" in p._p.xml or "<w:pict" in p._p.xml
][:2]
replace_drawing(login_drawings[0], DIAGRAM_DIR / "uc002-login-activity.png", 13.0)
replace_drawing(login_drawings[1], DIAGRAM_DIR / "uc002-login-sequence.png", 16.0)

# Build UC003 from the same table/heading styles and insert it before renumbered UC004.
marker = original_uc003_heading._p

logout_heading = document.add_paragraph("UC003 – Đăng xuất", style="Heading 2")
logout_heading.paragraph_format.page_break_before = True
logout_subheading = document.add_paragraph("Mô tả Use Case UC003", style="Heading 3")

logout_table_xml = deepcopy(document.tables[14]._tbl)
marker.addprevious(logout_heading._p)
marker.addprevious(logout_subheading._p)
marker.addprevious(logout_table_xml)

# Rebind the inserted table through the document table collection.
logout_table = next(
    table for table in document.tables
    if table._tbl is logout_table_xml
)
logout_values = [
    ("Use Case", "UC003 – Đăng xuất"),
    ("Mục đích", "Kết thúc phiên xác thực hiện tại trên thiết bị đang sử dụng."),
    ("Mô tả", "Người sử dụng chọn Đăng xuất. Ứng dụng xóa access token và thông tin phiên đăng nhập trên thiết bị, chuyển về màn hình Đăng nhập và hiển thị thông báo thành công. Tài khoản cùng dữ liệu đã lưu vẫn tồn tại; hiện trạng không có API logout phía máy chủ."),
    ("Tác nhân", "Người sử dụng"),
    ("Điều kiện trước", "Người sử dụng đang ở trong phiên đã xác thực và có thể chọn chức năng Đăng xuất."),
    ("Điều kiện sau", "Token và thông tin phiên đăng nhập trên thiết bị bị xóa; màn hình Đăng nhập được hiển thị. Tài khoản và dữ liệu đã lưu vẫn được giữ nguyên."),
    ("Luồng sự kiện chính (Basic Flows)", "B1. Người sử dụng chọn Đăng xuất.\nB2. Ứng dụng lưu thông báo đăng xuất an toàn cho màn hình kế tiếp.\nB3. Ứng dụng xóa access token và thông tin phiên đăng nhập trên thiết bị.\nB4. Ứng dụng chuyển đến màn hình Đăng nhập.\nB5. Màn hình Đăng nhập hiển thị thông báo thành công; tài khoản và dữ liệu đã lưu vẫn được giữ nguyên."),
    ("Luồng sự kiện phụ (Alternative Flows)", "A1. Token đã thiếu hoặc không còn hợp lệ → client vẫn dọn trạng thái phiên và chuyển đến Đăng nhập.\nA2. Token bị xóa ở tab khác → sự kiện storage làm sạch trạng thái phiên hiện tại."),
]
for row_index, (label, value) in enumerate(logout_values, start=1):
    logout_table.cell(row_index, 0).text = label
    logout_table.cell(row_index, 1).text = value

diagram_heading = document.add_paragraph("Biểu đồ", style="Heading 3")
diagram_note = document.add_paragraph("<Biểu đồ (diagram) chi tiết: Activity và Sequence Diagram>")
activity_p = document.add_paragraph()
activity_p.alignment = 1
activity_p.add_run().add_picture(str(DIAGRAM_DIR / "uc003-logout-activity.png"), width=Cm(13.0))
sequence_p = document.add_paragraph()
sequence_p.alignment = 1
sequence_p.add_run().add_picture(str(DIAGRAM_DIR / "uc003-logout-sequence.png"), width=Cm(16.0))
for paragraph in (diagram_heading, diagram_note, activity_p, sequence_p):
    marker.addprevious(paragraph._p)

apply_document_font(document)
OUTPUT.parent.mkdir(parents=True, exist_ok=True)
document.save(OUTPUT)
patch_embedded_svg(OUTPUT)
print(OUTPUT)
