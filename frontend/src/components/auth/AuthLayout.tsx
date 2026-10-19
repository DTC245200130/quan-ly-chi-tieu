import { Wallet, ReceiptText, ShieldCheck, Tags, BarChart3 } from "lucide-react";
import { Outlet } from "react-router-dom";
import { ThemeToggle } from "../ThemeToggle";

const capabilities = [
  { icon: ReceiptText, title: "Ghi chép rõ ràng", copy: "Theo dõi các khoản thu và chi trong một nơi." },
  { icon: Tags, title: "Sắp xếp gọn gàng", copy: "Phân loại thu chi theo những danh mục phù hợp với bạn." },
  { icon: BarChart3, title: "Hiểu dòng tiền", copy: "Xem báo cáo và so sánh chi tiêu giữa các tháng." },
];

export function AuthLayout() {
  return (
    <div className="auth-shell">
      <section className="auth-brand-panel" aria-label="Giới thiệu Sổ Chi Tiêu">
        <div className="auth-brand"><span className="brand__mark"><Wallet size={22} /></span><strong>Sổ Chi Tiêu</strong></div>
        <div className="auth-brand-copy">
          <h1>Tài chính rõ ràng bắt đầu từ những ghi chép nhỏ.</h1>
          <p>Một không gian riêng để ghi chép giao dịch, sắp xếp danh mục và hiểu rõ tình hình tài chính của bạn.</p>
        </div>
        <div className="auth-capability-list">
          {capabilities.map(({ icon: Icon, title, copy }) => (
            <div className="auth-capability" key={title}>
              <span><Icon size={19} /></span>
              <div><strong>{title}</strong><p>{copy}</p></div>
            </div>
          ))}
        </div>
        <p className="auth-privacy-note"><ShieldCheck size={17} /> Dữ liệu được tách biệt theo từng tài khoản.</p>
      </section>

      <main className="auth-workspace">
        <div className="auth-theme"><ThemeToggle /></div>
        <div className="auth-form-frame"><Outlet /></div>
      </main>
    </div>
  );
}
