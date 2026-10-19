import { FormEvent, useState } from "react";
import { ArrowLeft, KeyRound } from "lucide-react";
import { Link, useNavigate, useSearchParams } from "react-router-dom";
import { AuthNotice, PasswordField } from "../../components/auth/AuthFormControls";
import { api } from "../../lib/api";

export function ResetPasswordPage() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const token = searchParams.get("token")?.trim() ?? "";
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [passwordVisible, setPasswordVisible] = useState(false);
  const [confirmVisible, setConfirmVisible] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");

  const submit = async (event: FormEvent) => {
    event.preventDefault();
    if (!token) return setError("Liên kết đặt lại mật khẩu không hợp lệ.");
    if (password.length < 6) return setError("Mật khẩu phải có ít nhất 6 ký tự.");
    if (password !== confirmPassword) return setError("Mật khẩu xác nhận chưa khớp.");
    setSaving(true);
    setError("");
    try {
      await api.resetPassword(token, password);
      navigate("/login", { replace: true, state: { notice: "Đặt lại mật khẩu thành công. Hãy đăng nhập bằng mật khẩu mới." } });
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Không thể đặt lại mật khẩu. Vui lòng yêu cầu liên kết mới.");
    } finally {
      setSaving(false);
    }
  };

  if (!token) {
    return (
      <section className="auth-form-section auth-result-state">
        <span className="auth-result-icon auth-result-icon--error"><KeyRound size={27} /></span>
        <h2>Liên kết không hợp lệ</h2>
        <p>Liên kết đặt lại mật khẩu đang thiếu token. Hãy yêu cầu một liên kết mới.</p>
        <Link className="button button--primary auth-submit" to="/forgot-password">Yêu cầu liên kết mới</Link>
        <Link className="auth-inline-link" to="/login"><ArrowLeft size={17} /> Trở về đăng nhập</Link>
      </section>
    );
  }

  return (
    <section className="auth-form-section">
      <header className="auth-form-header"><span className="auth-form-icon"><KeyRound size={21} /></span><h2>Đặt mật khẩu mới</h2><p>Chọn mật khẩu mới cho tài khoản của bạn.</p></header>
      <form className="auth-form" onSubmit={submit}>
        <PasswordField id="reset-password" label="Mật khẩu mới" value={password} onChange={(event) => setPassword(event.target.value)} visible={passwordVisible} onToggle={() => setPasswordVisible((value) => !value)} autoComplete="new-password" disabled={saving} hint="Sử dụng ít nhất 6 ký tự." />
        <PasswordField id="reset-confirm-password" label="Xác nhận mật khẩu mới" value={confirmPassword} onChange={(event) => setConfirmPassword(event.target.value)} visible={confirmVisible} onToggle={() => setConfirmVisible((value) => !value)} autoComplete="new-password" disabled={saving} />
        {error && <AuthNotice tone="error">{error}</AuthNotice>}
        <button className="button button--primary auth-submit" type="submit" disabled={saving}>{saving ? "Đang cập nhật…" : "Cập nhật mật khẩu"}</button>
      </form>
      <p className="auth-back-link"><Link to="/login"><ArrowLeft size={17} /> Trở về đăng nhập</Link></p>
    </section>
  );
}
