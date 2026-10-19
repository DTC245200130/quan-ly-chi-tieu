import { FormEvent, useState } from "react";
import { ArrowLeft, MailCheck, Send } from "lucide-react";
import { Link } from "react-router-dom";
import { AuthNotice } from "../../components/auth/AuthFormControls";
import { api } from "../../lib/api";

export function ForgotPasswordPage() {
  const [email, setEmail] = useState("");
  const [sent, setSent] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");

  const submit = async (event: FormEvent) => {
    event.preventDefault();
    setSaving(true);
    setError("");
    try {
      await api.forgotPassword(email.trim().toLocaleLowerCase("vi"));
      setSent(true);
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Không thể gửi yêu cầu. Vui lòng thử lại.");
    } finally {
      setSaving(false);
    }
  };

  if (sent) {
    return (
      <section className="auth-form-section auth-result-state">
        <span className="auth-result-icon"><MailCheck size={27} /></span>
        <h2>Kiểm tra hộp thư của bạn</h2>
        <p>Nếu <strong>{email}</strong> tồn tại trong hệ thống, liên kết đặt lại mật khẩu sẽ được gửi và có hiệu lực trong 15 phút.</p>
        <Link className="button button--primary auth-submit" to="/login"><ArrowLeft size={18} /> Trở về đăng nhập</Link>
        <button className="text-button" type="button" onClick={() => setSent(false)}>Dùng email khác</button>
      </section>
    );
  }

  return (
    <section className="auth-form-section">
      <header className="auth-form-header"><span className="auth-form-icon"><Send size={21} /></span><h2>Khôi phục mật khẩu</h2><p>Nhập email đã đăng ký để nhận liên kết đặt lại mật khẩu.</p></header>
      <form className="auth-form" onSubmit={submit}>
        <label className="auth-field" htmlFor="recovery-email"><span>Email</span><input id="recovery-email" name="email" type="email" value={email} onChange={(event) => setEmail(event.target.value)} autoComplete="email" autoFocus required disabled={saving} placeholder="ban@email.com" /></label>
        {error && <AuthNotice tone="error">{error}</AuthNotice>}
        <button className="button button--primary auth-submit" type="submit" disabled={saving}>{saving ? "Đang gửi…" : <><Send size={18} /> Gửi liên kết khôi phục</>}</button>
      </form>
      <p className="auth-back-link"><Link to="/login"><ArrowLeft size={17} /> Trở về đăng nhập</Link></p>
    </section>
  );
}
