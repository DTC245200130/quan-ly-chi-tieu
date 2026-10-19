import { Navigate, Outlet, useLocation } from "react-router-dom";
import { PiggyBank } from "lucide-react";
import { useAuth } from "./AuthContext";

function SessionLoading() {
  return (
    <main className="session-loading" aria-live="polite" aria-busy="true">
      <span><PiggyBank size={24} /></span>
      <p>Đang kiểm tra phiên truy cập…</p>
    </main>
  );
}

export function ProtectedRoute() {
  const { user, loading } = useAuth();
  const location = useLocation();
  if (loading) return <SessionLoading />;
  if (!user) return <Navigate to="/login" replace state={{ from: location }} />;
  return <Outlet />;
}

export function PublicOnlyRoute() {
  const { user, loading } = useAuth();
  if (loading) return <SessionLoading />;
  if (user) return <Navigate to="/dashboard" replace />;
  return <Outlet />;
}
