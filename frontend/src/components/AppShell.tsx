import { BarChart3, Grid2X2, LogOut, ReceiptText, Tags, Wallet, UserRoundPen } from "lucide-react";
import { useEffect, useState } from "react";
import { NavLink, Outlet, useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "../auth/AuthContext";
import { ProfileAvatar, ProfilePanel } from "./ProfilePanel";

const navItems = [
  { to: "/dashboard", label: "Tổng quan", icon: Grid2X2 },
  { to: "/transactions", label: "Giao dịch", icon: ReceiptText },
  { to: "/categories", label: "Danh mục", icon: Tags },
  { to: "/reports", label: "Báo cáo", icon: BarChart3 },
];

export function AppShell() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [profileOpen, setProfileOpen] = useState(false);
  const profileLabel = user?.display_name?.trim() || user?.username || "Người dùng";

  useEffect(() => { setProfileOpen(false); }, [location.pathname]);

  const handleLogout = () => {
    sessionStorage.setItem("auth_notice", "Bạn đã đăng xuất an toàn.");
    logout();
    navigate("/login", { replace: true });
  };

  return (
    <div className="app-shell finance-shell">
      <header className="finance-topbar">
        <NavLink to="/dashboard" className="finance-brand" aria-label="Sổ Chi Tiêu - Trang chủ">
          <span className="finance-brand__mark"><Wallet size={23} /></span>
          <span><strong>Sổ Chi Tiêu</strong><small>TÀI CHÍNH CÁ NHÂN</small></span>
        </NavLink>
        <nav className="finance-nav" aria-label="Điều hướng chính">
          {navItems.map(({ to, label, icon: Icon }) => (
            <NavLink key={to} to={to} className={({ isActive }) => `finance-nav__item${isActive ? " is-active" : ""}`}>
              <Icon size={18} /><span>{label}</span>
            </NavLink>
          ))}
        </nav>
        <div className="finance-account">
          <button className="finance-profile" type="button" onClick={() => setProfileOpen(true)} title="Chỉnh sửa thông tin cá nhân">
            <ProfileAvatar avatarUrl={user?.avatar_url ?? null} label={profileLabel} />
            <span><strong>{profileLabel}</strong><small>Tài khoản cá nhân</small></span>
            <UserRoundPen size={16} />
          </button>
          <button className="icon-button" type="button" onClick={handleLogout} aria-label="Đăng xuất" title="Đăng xuất"><LogOut size={19} /></button>
        </div>
      </header>
      <main className="main-content finance-content"><Outlet /></main>
      <footer className="finance-footer"><span>Sổ Chi Tiêu</span><span>Ghi chép hôm nay. Chủ động ngày mai.</span></footer>
      <ProfilePanel open={profileOpen} onClose={() => setProfileOpen(false)} />
    </div>
  );
}
