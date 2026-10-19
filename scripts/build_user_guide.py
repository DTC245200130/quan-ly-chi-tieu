from __future__ import annotations

import shutil
import zipfile
from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor


ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = Path(r"C:\Users\LENOVO\Downloads\07_GenAI_SoftwareDevelopment_user-guide.docx")
SRS_BASE = ROOT / "docs/outputs/03_GenAI_SoftwareDevelopment_requirements-specification.docx"
SCREENFLOW = ROOT / "docs/outputs/06_GenAI_SoftwareDevelopment_screenflow_db_srs_ord_aligned.docx"
OUTPUT = ROOT / "docs/outputs/07_GenAI_SoftwareDevelopment_user-guide.docx"
MEDIA_DIR = ROOT / ".tmp/user-guide-media"

FONT = "Times New Roman"
ACCENT = RGBColor(41, 157, 120)


def clear_document_body(document: Document) -> None:
    body = document._element.body
    for child in list(body):
        if child.tag != qn("w:sectPr"):
            body.remove(child)


def set_cell_shading(cell, fill: str) -> None:
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = tc_pr.find(qn("w:shd"))
    if shd is None:
        shd = OxmlElement("w:shd")
        tc_pr.append(shd)
    shd.set(qn("w:fill"), fill)


def set_repeat_table_header(row) -> None:
    tr_pr = row._tr.get_or_add_trPr()
    tbl_header = OxmlElement("w:tblHeader")
    tbl_header.set(qn("w:val"), "true")
    tr_pr.append(tbl_header)


def set_cell_margins(cell, top=80, start=100, bottom=80, end=100) -> None:
    tc_pr = cell._tc.get_or_add_tcPr()
    tc_mar = tc_pr.first_child_found_in("w:tcMar")
    if tc_mar is None:
        tc_mar = OxmlElement("w:tcMar")
        tc_pr.append(tc_mar)
    for side, value in (("top", top), ("start", start), ("bottom", bottom), ("end", end)):
        node = tc_mar.find(qn(f"w:{side}"))
        if node is None:
            node = OxmlElement(f"w:{side}")
            tc_mar.append(node)
        node.set(qn("w:w"), str(value))
        node.set(qn("w:type"), "dxa")


def format_run(run, *, size=13, bold=None, italic=None, color=None) -> None:
    run.font.name = FONT
    run._element.get_or_add_rPr().rFonts.set(qn("w:eastAsia"), FONT)
    run.font.size = Pt(size)
    if bold is not None:
        run.bold = bold
    if italic is not None:
        run.italic = italic
    if color is not None:
        run.font.color.rgb = color


def add_body(document: Document, text: str = "", *, bold_prefix: str | None = None):
    paragraph = document.add_paragraph(style="Normal")
    paragraph.paragraph_format.space_after = Pt(6)
    paragraph.paragraph_format.line_spacing = 1.15
    paragraph.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    if bold_prefix and text.startswith(bold_prefix):
        format_run(paragraph.add_run(bold_prefix), bold=True)
        format_run(paragraph.add_run(text[len(bold_prefix) :]))
    else:
        format_run(paragraph.add_run(text))
    return paragraph


def add_bullet(document: Document, text: str):
    paragraph = document.add_paragraph(style="List Paragraph")
    paragraph.style = document.styles["List Paragraph"]
    paragraph.paragraph_format.left_indent = Cm(0.75)
    paragraph.paragraph_format.first_line_indent = Cm(-0.45)
    paragraph.paragraph_format.space_after = Pt(4)
    format_run(paragraph.add_run("•\t"))
    format_run(paragraph.add_run(text))
    return paragraph


def add_numbered_steps(document: Document, steps: list[str]):
    for index, step in enumerate(steps, 1):
        paragraph = document.add_paragraph(style="List Paragraph")
        paragraph.paragraph_format.left_indent = Cm(0.85)
        paragraph.paragraph_format.first_line_indent = Cm(-0.55)
        paragraph.paragraph_format.space_after = Pt(4)
        format_run(paragraph.add_run(f"{index}.\t"), bold=True)
        format_run(paragraph.add_run(step))


def add_heading(document: Document, text: str, level: int):
    paragraph = document.add_paragraph(style=f"Heading {level}")
    paragraph.paragraph_format.keep_with_next = True
    paragraph.paragraph_format.space_before = Pt(8 if level > 1 else 12)
    paragraph.paragraph_format.space_after = Pt(6)
    run = paragraph.add_run(text)
    format_run(run, size=13 if level > 1 else 14, bold=True)
    if level == 1:
        run.font.color.rgb = RGBColor(0, 0, 0)
    return paragraph


def add_caption(document: Document, text: str):
    paragraph = document.add_paragraph()
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    paragraph.paragraph_format.keep_with_next = False
    paragraph.paragraph_format.space_after = Pt(6)
    format_run(paragraph.add_run(text), size=11, italic=True)


def add_image(document: Document, image: Path, caption: str, width_cm: float = 15.5):
    paragraph = document.add_paragraph()
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    paragraph.paragraph_format.keep_together = True
    run = paragraph.add_run()
    run.add_picture(str(image), width=Cm(width_cm))
    add_caption(document, caption)


def add_info_table(document: Document, rows: list[tuple[str, str]]):
    table = document.add_table(rows=1, cols=2)
    table.style = "Table Grid"
    table.autofit = False
    table.columns[0].width = Cm(4.1)
    table.columns[1].width = Cm(11.5)
    header = table.rows[0]
    header.cells[0].text = "Nội dung"
    header.cells[1].text = "Hướng dẫn"
    set_repeat_table_header(header)
    for cell in header.cells:
        set_cell_shading(cell, "299D78")
        set_cell_margins(cell)
        for paragraph in cell.paragraphs:
            paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
            for run in paragraph.runs:
                format_run(run, size=12, bold=True, color=RGBColor(255, 255, 255))
    for left, right in rows:
        cells = table.add_row().cells
        cells[0].text = left
        cells[1].text = right
        for index, cell in enumerate(cells):
            set_cell_margins(cell)
            for paragraph in cell.paragraphs:
                paragraph.paragraph_format.space_after = Pt(2)
                paragraph.paragraph_format.line_spacing = 1.0
                for run in paragraph.runs:
                    format_run(run, size=11, bold=index == 0)
    document.add_paragraph().paragraph_format.space_after = Pt(2)


def add_feature(
    document: Document,
    title: str,
    purpose: str,
    steps: list[str],
    result: str,
    notes: list[str] | None = None,
    image: Path | None = None,
    caption: str | None = None,
):
    add_heading(document, title, 3)
    add_body(document, f"Mục đích: {purpose}", bold_prefix="Mục đích:")
    add_body(document, "Các bước thực hiện:", bold_prefix="Các bước thực hiện:")
    add_numbered_steps(document, steps)
    add_body(document, f"Kết quả: {result}", bold_prefix="Kết quả:")
    if notes:
        add_body(document, "Lưu ý:", bold_prefix="Lưu ý:")
        for note in notes:
            add_bullet(document, note)
    if image and caption:
        add_image(document, image, caption)


def add_page_number(section) -> None:
    footer = section.footer
    paragraph = footer.paragraphs[0]
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    paragraph.clear()
    run = paragraph.add_run("Trang ")
    format_run(run, size=10)
    begin = OxmlElement("w:fldChar")
    begin.set(qn("w:fldCharType"), "begin")
    instr = OxmlElement("w:instrText")
    instr.set(qn("xml:space"), "preserve")
    instr.text = "PAGE"
    separate = OxmlElement("w:fldChar")
    separate.set(qn("w:fldCharType"), "separate")
    value = OxmlElement("w:t")
    value.text = "1"
    end = OxmlElement("w:fldChar")
    end.set(qn("w:fldCharType"), "end")
    run._r.extend([begin, instr, separate, value, end])


def extract_screenflow_media() -> dict[str, Path]:
    MEDIA_DIR.mkdir(parents=True, exist_ok=True)
    wanted = {f"image{i}.png" for i in range(1, 27)}
    result: dict[str, Path] = {}
    with zipfile.ZipFile(SCREENFLOW) as archive:
        for member in archive.namelist():
            name = Path(member).name
            if member.startswith("word/media/") and name in wanted:
                target = MEDIA_DIR / name
                target.write_bytes(archive.read(member))
                result[name] = target
    return result


def build() -> None:
    if not TEMPLATE.exists():
        raise FileNotFoundError(TEMPLATE)
    if not SRS_BASE.exists():
        raise FileNotFoundError(SRS_BASE)
    if not SCREENFLOW.exists():
        raise FileNotFoundError(SCREENFLOW)

    images = extract_screenflow_media()
    # The supplied template defines the required three-part content topology, but its
    # package is rejected as corrupt by Microsoft Word. Use the valid SRS package as
    # the style/package base while retaining the template's topology and page geometry.
    document = Document(SRS_BASE)
    clear_document_body(document)

    # Keep the supplied template's A4 page geometry and align typography with SRS/ORD.
    for style_name in ("Normal", "No Spacing", "List Paragraph", "Heading 1", "Heading 2", "Heading 3"):
        style = document.styles[style_name]
        style.font.name = FONT
        style._element.get_or_add_rPr().rFonts.set(qn("w:eastAsia"), FONT)
    document.styles["Normal"].font.size = Pt(13)
    document.styles["List Paragraph"].font.size = Pt(13)
    for section in document.sections:
        add_page_number(section)

    # Cover page.
    for _ in range(4):
        document.add_paragraph()
    title = document.add_paragraph()
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    format_run(title.add_run("HỆ THỐNG QUẢN LÝ CHI TIÊU CÁ NHÂN CÓ TÍCH HỢP AI"), size=16, bold=True)
    subtitle = document.add_paragraph()
    subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER
    subtitle.paragraph_format.space_before = Pt(18)
    format_run(subtitle.add_run("TÀI LIỆU HƯỚNG DẪN SỬ DỤNG – V1.0"), size=16, bold=True, color=ACCENT)
    meta = document.add_paragraph()
    meta.alignment = WD_ALIGN_PARAGRAPH.CENTER
    meta.paragraph_format.space_before = Pt(24)
    format_run(meta.add_run("Nhóm 47 – Sổ chi tiêu\nNgày hoàn thiện: 27/09/2026"), size=13)
    meta.add_run().add_break(WD_BREAK.PAGE)

    add_heading(document, "GIỚI THIỆU ỨNG DỤNG", 1)
    add_body(
        document,
        "Sổ chi tiêu là ứng dụng hỗ trợ cá nhân ghi nhận thu nhập và chi tiêu, lập ngân sách theo tháng, quản lý mục tiêu tiết kiệm, xem số liệu tổng hợp và tham khảo gợi ý từ trợ lý AI. Dữ liệu của mỗi tài khoản được tách biệt và chỉ người sử dụng đã đăng nhập mới truy cập được các chức năng nghiệp vụ của mình.",
    )
    add_body(
        document,
        "Tài liệu này hướng dẫn thao tác trên giao diện web/PWA và ứng dụng cài đặt Windows. Hai kênh sử dụng cùng một Backend và đều cần kết nối Internet trong phạm vi phát hành hiện tại. Giao diện có thể thay đổi kích thước theo thiết bị nhưng tên chức năng và trình tự nghiệp vụ không thay đổi.",
    )
    add_info_table(
        document,
        [
            ("Đối tượng sử dụng", "Cá nhân cần theo dõi tài chính và mục tiêu tiết kiệm."),
            ("Chức năng chính", "Tài khoản; danh mục; giao dịch; ngân sách; mục tiêu tiết kiệm; Dashboard; báo cáo; trợ lý AI."),
            ("Đơn vị tiền tệ", "Việt Nam đồng (VND)."),
            ("Kỳ dữ liệu", "Theo tháng, sử dụng múi giờ Asia/Ho_Chi_Minh."),
            ("Giới hạn", "Không kết nối ngân hàng, không thanh toán hoặc đầu tư tự động, không hỗ trợ làm việc ngoại tuyến."),
        ],
    )
    add_image(document, images["image2.png"], "Hình 1. Luồng sử dụng tổng thể của ứng dụng")
    document.add_paragraph().add_run().add_break(WD_BREAK.PAGE)

    add_heading(document, "CẤU HÌNH PHẦN CỨNG - PHẦN MỀM", 1)
    add_heading(document, "Phần cứng", 2)
    add_body(document, "Đối với người dùng cuối, thiết bị chỉ cần đủ khả năng chạy trình duyệt hiện đại hoặc ứng dụng Windows. Cấu hình tham chiếu theo SRS:")
    add_bullet(document, "CPU Intel Core i5 thế hệ 10 hoặc tương đương.")
    add_bullet(document, "RAM tối thiểu 8 GB.")
    add_bullet(document, "Dung lượng trống tối thiểu 10 GB nếu cài ứng dụng và lưu bộ nhớ đệm.")
    add_bullet(document, "Kết nối Internet ổn định cho toàn bộ chức năng, đặc biệt là khôi phục mật khẩu và trợ lý AI.")
    add_heading(document, "Phần mềm", 2)
    add_bullet(document, "Trình duyệt Google Chrome hoặc Microsoft Edge phiên bản hiện đại; bật JavaScript và cho phép lưu trữ cục bộ.")
    add_bullet(document, "Hoặc ứng dụng Windows được nhóm phát triển cung cấp. Người dùng không cần cài Python, Git, VS Code hay hệ quản trị cơ sở dữ liệu.")
    add_bullet(document, "Có tài khoản Sổ chi tiêu hợp lệ. Một số chức năng cần dịch vụ ngoài Google Gemini hoặc Resend đang hoạt động.")
    add_body(document, "Khuyến nghị: không dùng thiết bị công cộng để lưu phiên đăng nhập; đăng xuất sau khi sử dụng và không chia sẻ liên kết đặt lại mật khẩu.")
    document.add_paragraph().add_run().add_break(WD_BREAK.PAGE)

    add_heading(document, "CÁC CHỨC NĂNG CHÍNH", 1)
    add_body(document, "Các chức năng được chia theo danh sách tác nhân trong SRS: Người sử dụng là tác nhân chính; Google Gemini và Resend là các hệ thống ngoài hỗ trợ hai luồng chuyên biệt.")
    add_heading(document, "Chức năng của Người sử dụng", 2)

    add_feature(
        document,
        "Đăng ký tài khoản",
        "Tạo tài khoản cá nhân mới.",
        [
            "Tại màn hình Đăng nhập, chọn liên kết Đăng ký.",
            "Nhập tên đăng nhập, email, mật khẩu và xác nhận mật khẩu.",
            "Kiểm tra lại thông tin rồi chọn nút Đăng ký.",
            "Khi đăng ký thành công, quay lại màn hình Đăng nhập để sử dụng tài khoản vừa tạo.",
        ],
        "Hệ thống tạo tài khoản khi username/email chưa được dùng và dữ liệu hợp lệ.",
        ["Username và email được so khớp không phân biệt chữ hoa, chữ thường.", "Mật khẩu và xác nhận mật khẩu phải trùng nhau."],
        images["image4.png"],
        "Hình 2. Luồng đăng ký tài khoản",
    )
    add_feature(
        document,
        "Đăng nhập",
        "Xác thực để truy cập dữ liệu tài chính cá nhân.",
        [
            "Mở ứng dụng và nhập username hoặc email đã đăng ký.",
            "Nhập mật khẩu.",
            "Chọn Đăng nhập.",
            "Sau khi xác thực thành công, hệ thống chuyển đến Dashboard.",
        ],
        "Phiên đăng nhập được tạo trên thiết bị và các menu nghiệp vụ được hiển thị.",
        ["Nếu thông tin không đúng, kiểm tra bàn phím, khoảng trắng và thử lại; không chia sẻ mật khẩu."],
        images["image3.png"],
        "Hình 3. Luồng đăng nhập",
    )
    add_feature(
        document,
        "Khôi phục mật khẩu",
        "Tạo mật khẩu mới khi người sử dụng quên mật khẩu hiện tại.",
        [
            "Chọn Quên mật khẩu tại màn hình Đăng nhập.",
            "Nhập email đã đăng ký và gửi yêu cầu.",
            "Mở email nhận được từ hệ thống và chọn liên kết đặt lại mật khẩu.",
            "Nhập mật khẩu mới, xác nhận và hoàn tất; sau đó đăng nhập lại.",
        ],
        "Mật khẩu mới thay thế mật khẩu cũ nếu liên kết còn hiệu lực.",
        ["Thông báo gửi yêu cầu không xác nhận email có tồn tại nhằm bảo vệ thông tin tài khoản.", "Không chuyển tiếp liên kết đặt lại mật khẩu cho người khác."],
        images["image5.png"],
        "Hình 4. Luồng khôi phục mật khẩu",
    )
    add_feature(
        document,
        "Xem Dashboard",
        "Theo dõi nhanh tổng thu, tổng chi, số dư, ngân sách và các giao dịch gần đây theo tháng.",
        [
            "Đăng nhập hoặc chọn Dashboard trên thanh điều hướng.",
            "Chọn tháng cần xem.",
            "Đọc các thẻ tổng quan, biểu đồ phân bổ và danh sách giao dịch gần đây.",
            "Nếu chưa có dữ liệu, tạo danh mục và giao dịch để bắt đầu.",
        ],
        "Dashboard tổng hợp lại dữ liệu thuộc tài khoản ở kỳ đã chọn.",
        ["Số liệu thay đổi khi giao dịch, ngân sách hoặc mục tiêu liên quan được cập nhật."],
        images["image6.png"],
        "Hình 5. Luồng xem Dashboard",
    )
    add_feature(
        document,
        "Quản lý hồ sơ và mật khẩu",
        "Cập nhật thông tin hiển thị, ảnh đại diện và mật khẩu của tài khoản.",
        [
            "Chọn avatar ở góc giao diện và mở Quản lý hồ sơ.",
            "Sửa tên hiển thị hoặc chọn ảnh đại diện phù hợp, sau đó lưu.",
            "Để đổi mật khẩu, nhập mật khẩu hiện tại, mật khẩu mới và xác nhận mật khẩu mới.",
            "Chọn lưu và kiểm tra thông báo thành công.",
        ],
        "Thông tin hồ sơ được cập nhật; mật khẩu chỉ đổi khi mật khẩu hiện tại đúng và dữ liệu mới hợp lệ.",
        ["Ảnh tải lên phải đáp ứng loại tệp và dung lượng mà giao diện chấp nhận.", "Sau khi đổi mật khẩu, dùng mật khẩu mới cho lần đăng nhập tiếp theo."],
        images["image22.png"],
        "Hình 6. Luồng quản lý hồ sơ và ảnh đại diện",
    )
    add_feature(
        document,
        "Quản lý danh mục",
        "Tạo cấu trúc phân loại cho các khoản thu và chi.",
        [
            "Mở Danh mục và chọn nhóm Chi tiêu hoặc Thu nhập.",
            "Chọn Thêm danh mục, nhập tên, chọn biểu tượng và màu rồi lưu.",
            "Để sửa, mở menu của danh mục, thay đổi thông tin và lưu.",
            "Để xóa, chọn Xóa và xác nhận khi danh mục không bị ràng buộc bởi dữ liệu liên quan.",
        ],
        "Danh mục xuất hiện trong danh sách và có thể được chọn khi tạo giao dịch; tên không được trùng trong cùng loại của tài khoản.",
        ["Nên tạo danh mục trước khi nhập giao dịch."],
        images["image7.png"],
        "Hình 7. Luồng tạo danh mục",
    )
    add_feature(
        document,
        "Quản lý giao dịch",
        "Ghi nhận, tìm kiếm, chỉnh sửa và xóa các khoản thu/chi.",
        [
            "Mở Giao dịch và chọn Khoản thu hoặc Khoản chi.",
            "Nhập số tiền, chọn danh mục cùng loại, ngày giao dịch và ghi chú nếu cần.",
            "Chọn lưu; kiểm tra bản ghi mới trong danh sách.",
            "Dùng từ khóa, loại, danh mục và khoảng ngày để lọc dữ liệu.",
            "Mở giao dịch để chỉnh sửa hoặc xóa; xác nhận trước khi xóa.",
        ],
        "Giao dịch được ghi nhận và các số liệu Dashboard, báo cáo, ngân sách liên quan được tính lại.",
        ["Chọn đúng loại và danh mục; số tiền phải lớn hơn 0."],
        images["image9.png"],
        "Hình 8. Luồng tạo giao dịch",
    )
    add_feature(
        document,
        "Quản lý ngân sách",
        "Đặt và theo dõi hạn mức chi theo danh mục trong một tháng.",
        [
            "Mở Ngân sách và chọn tháng cần quản lý.",
            "Chọn Thêm ngân sách, chọn danh mục chi và nhập hạn mức.",
            "Lưu để xem số đã chi, số còn lại và tỷ lệ sử dụng.",
            "Mở ngân sách để sửa hạn mức hoặc xóa khi không còn cần theo dõi.",
        ],
        "Hệ thống so sánh tổng chi của danh mục với hạn mức và hiển thị trạng thái còn lại/vượt mức.",
        ["Mỗi danh mục chi chỉ có một ngân sách trong cùng tháng và năm."],
        images["image12.png"],
        "Hình 9. Luồng đặt ngân sách",
    )
    add_feature(
        document,
        "Quản lý mục tiêu tiết kiệm",
        "Lập mục tiêu, chia hạng mục, nạp/rút tiền và hoàn thành mục tiêu.",
        [
            "Mở Mục tiêu và chọn Thêm mục tiêu.",
            "Nhập tên, số tiền cần đạt, thời hạn nếu có rồi lưu.",
            "Mở chi tiết để thêm/sửa/xóa hạng mục con và theo dõi tổng chi phí dự kiến.",
            "Chọn Nạp tiền hoặc Rút tiền, nhập số tiền và xác nhận; xem lại lịch sử.",
            "Khi tiến độ đạt 100%, chọn Hoàn thành và phương án xử lý khoản tiền theo giao diện.",
        ],
        "Tiến độ và số dư mục tiêu được cập nhật sau mỗi thao tác hợp lệ.",
        ["Số tiền nạp không được vượt số dư khả dụng; số tiền rút không được vượt số đang có trong mục tiêu.", "Mục tiêu chưa đủ 100% không thể hoàn thành."],
        images["image14.png"],
        "Hình 10. Luồng tạo mục tiêu tiết kiệm",
    )
    add_feature(
        document,
        "Xem báo cáo so sánh",
        "So sánh thu nhập, chi tiêu và số dư giữa tháng được chọn với tháng liền trước.",
        [
            "Mở Báo cáo.",
            "Chọn tháng cần phân tích.",
            "Xem các chỉ số tổng, mức thay đổi và biểu đồ theo danh mục.",
            "Đối chiếu giao dịch nguồn khi cần kiểm tra một số liệu.",
        ],
        "Báo cáo thể hiện số liệu của kỳ hiện tại và kỳ trước thuộc cùng tài khoản.",
        ["Nếu kỳ không có dữ liệu, báo cáo có thể hiển thị trạng thái trống hoặc giá trị 0."],
        images["image20.png"],
        "Hình 11. Luồng xem báo cáo so sánh",
    )
    add_feature(
        document,
        "Sử dụng trợ lý AI",
        "Đặt câu hỏi và nhận nội dung tham khảo dựa trên số liệu tài chính tổng hợp.",
        [
            "Mở Trợ lý AI và chọn kỳ dữ liệu.",
            "Bắt đầu cuộc trò chuyện mới hoặc mở lại cuộc trò chuyện cũ.",
            "Nhập câu hỏi rõ ràng, ví dụ yêu cầu nhận xét xu hướng chi tiêu của tháng.",
            "Gửi câu hỏi; đọc câu trả lời, kỳ dữ liệu, bằng chứng và mức tin cậy nếu giao diện hiển thị.",
            "Quay lại Báo cáo hoặc Giao dịch để kiểm tra số liệu trước khi quyết định.",
        ],
        "Câu trả lời được lưu trong lịch sử hội thoại của tài khoản khi dịch vụ AI hoạt động.",
        ["AI chỉ tư vấn và không tự tạo, sửa hoặc xóa dữ liệu tài chính.", "Không nhập mật khẩu, token, thông tin định danh nhạy cảm hoặc bí mật vào câu hỏi."],
        images["image21.png"],
        "Hình 12. Luồng sử dụng trợ lý AI",
    )
    add_feature(
        document,
        "Đăng xuất",
        "Kết thúc phiên sử dụng trên thiết bị hiện tại.",
        [
            "Mở menu tài khoản từ avatar.",
            "Chọn Đăng xuất.",
            "Kiểm tra ứng dụng quay về màn hình Đăng nhập.",
        ],
        "Token và thông tin phiên trên thiết bị bị xóa; tài khoản và dữ liệu vẫn được giữ nguyên.",
        ["Luôn đăng xuất khi dùng máy tính dùng chung."],
        images["image23.png"],
        "Hình 13. Luồng đăng xuất",
    )

    add_heading(document, "Chức năng của Google Gemini", 2)
    add_body(document, "Google Gemini là hệ thống ngoài hỗ trợ Trợ lý AI. Khi người sử dụng gửi câu hỏi, Backend chuẩn bị ngữ cảnh tài chính đã tổng hợp và tối thiểu hóa dữ liệu trước khi gửi sang Gemini để tạo câu trả lời.")
    add_bullet(document, "Người sử dụng không thao tác trực tiếp với tài khoản Gemini trong ứng dụng.")
    add_bullet(document, "Nếu Gemini tạm thời không khả dụng, ứng dụng hiển thị thông báo lỗi ổn định; hãy thử lại sau.")
    add_bullet(document, "Câu trả lời chỉ mang tính tham khảo; luôn kiểm tra bằng chứng và dữ liệu gốc trước khi ra quyết định tài chính.")

    add_heading(document, "Chức năng của Resend", 2)
    add_body(document, "Resend là hệ thống ngoài gửi email chứa liên kết đặt lại mật khẩu. Người sử dụng chỉ cần nhập email đã đăng ký trong luồng Khôi phục mật khẩu và kiểm tra hộp thư của mình.")
    add_bullet(document, "Kiểm tra thư rác nếu chưa thấy email sau một khoảng thời gian hợp lý.")
    add_bullet(document, "Chỉ mở liên kết do hệ thống gửi cho chính yêu cầu của mình; không chia sẻ hoặc tái sử dụng liên kết.")
    add_bullet(document, "Nếu dịch vụ gửi email không khả dụng hoặc cấu hình triển khai chưa hoàn tất, liên hệ nhóm vận hành thay vì gửi yêu cầu liên tục.")

    add_heading(document, "XỬ LÝ SỰ CỐ THƯỜNG GẶP", 1)
    add_info_table(
        document,
        [
            ("Không đăng nhập được", "Kiểm tra username/email, mật khẩu, kết nối mạng; dùng Quên mật khẩu nếu cần."),
            ("Phiên đăng nhập hết hạn", "Đăng nhập lại. Không cố sử dụng token hoặc liên kết cũ."),
            ("Không tạo được giao dịch", "Kiểm tra số tiền lớn hơn 0 và đã có danh mục đúng loại thu/chi."),
            ("Ngân sách không khớp", "Kiểm tra tháng đang chọn, danh mục và các giao dịch chi trong cùng kỳ."),
            ("Không nạp/rút mục tiêu", "Kiểm tra số dư khả dụng và số tiền hiện có trong mục tiêu."),
            ("Không nhận email reset", "Kiểm tra đúng email, thư rác và thử lại sau; không thể xác định sự tồn tại tài khoản từ thông báo chung."),
            ("Trợ lý AI báo lỗi", "Kiểm tra Internet, thử lại sau và dùng Báo cáo/Giao dịch để xem số liệu trong lúc dịch vụ ngoài gián đoạn."),
        ],
    )

    # Normalize direct formatting to avoid font fallback for Vietnamese text.
    for paragraph in document.paragraphs:
        for run in paragraph.runs:
            if run.text:
                run.font.name = FONT
                run._element.get_or_add_rPr().rFonts.set(qn("w:eastAsia"), FONT)
    for table in document.tables:
        for row in table.rows:
            for cell in row.cells:
                for paragraph in cell.paragraphs:
                    for run in paragraph.runs:
                        run.font.name = FONT
                        run._element.get_or_add_rPr().rFonts.set(qn("w:eastAsia"), FONT)

    document.core_properties.title = "Tài liệu hướng dẫn sử dụng Sổ chi tiêu"
    document.core_properties.subject = "User guide aligned with SRS and ORD"
    document.core_properties.author = "Nhóm 47"
    document.core_properties.comments = "Tạo từ mẫu 07; nội dung đối chiếu SRS/ORD và giao diện hiện có."
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    document.save(OUTPUT)
    print(OUTPUT)


if __name__ == "__main__":
    build()
