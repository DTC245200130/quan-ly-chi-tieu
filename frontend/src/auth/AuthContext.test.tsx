import { act, render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { api, AUTH_UNAUTHORIZED_EVENT, TOKEN_KEY } from "../lib/api";
import { AuthProvider, useAuth } from "./AuthContext";
import { ProtectedRoute, PublicOnlyRoute } from "./RouteGuards";
import type { User } from "../types";

const user: User = {
  id: "u1",
  username: "owner",
  email: "owner@example.com",
  display_name: "Owner",
  avatar_url: null,
};

let currentAuth: ReturnType<typeof useAuth>;

function Probe() {
  currentAuth = useAuth();
  return <div>{currentAuth.loading ? "loading" : currentAuth.user?.username ?? "anonymous"}</div>;
}

describe("AuthProvider", () => {
  beforeEach(() => {
    vi.spyOn(api, "getMe").mockResolvedValue(user);
    vi.spyOn(api, "login").mockResolvedValue({ access_token: "new-token", token_type: "bearer" });
    vi.spyOn(api, "updateProfile").mockResolvedValue({ ...user, username: "updated" });
    vi.spyOn(api, "changePassword").mockResolvedValue({ message: "Đổi mật khẩu thành công." });
    vi.spyOn(api, "deleteAccount").mockResolvedValue({ message: "Tài khoản và dữ liệu cá nhân đã được xóa." });
    vi.spyOn(api, "uploadAvatar").mockResolvedValue({ ...user, avatar_url: "/avatar.png" });
    vi.spyOn(api, "deleteAvatar").mockResolvedValue({ ...user, avatar_url: null });
  });

  it("finishes anonymous initialization when there is no token", async () => {
    render(<AuthProvider><Probe /></AuthProvider>);
    await screen.findByText("anonymous");
    expect(api.getMe).not.toHaveBeenCalled();
  });

  it("restores a stored session", async () => {
    localStorage.setItem(TOKEN_KEY, "stored");
    render(<AuthProvider><Probe /></AuthProvider>);
    expect(screen.getByText("loading")).toBeInTheDocument();
    await screen.findByText("owner");
    expect(api.getMe).toHaveBeenCalledOnce();
  });

  it("clears a stored token when session restoration fails", async () => {
    localStorage.setItem(TOKEN_KEY, "stored");
    vi.mocked(api.getMe).mockRejectedValueOnce(new Error("expired"));
    render(<AuthProvider><Probe /></AuthProvider>);
    await screen.findByText("anonymous");
    expect(localStorage.getItem(TOKEN_KEY)).toBeNull();
  });

  it("logs in and applies all profile mutations", async () => {
    render(<AuthProvider><Probe /></AuthProvider>);
    await screen.findByText("anonymous");
    await act(async () => { await currentAuth.login("owner", "secret"); });
    expect(screen.getByText("owner")).toBeInTheDocument();
    expect(localStorage.getItem(TOKEN_KEY)).toBe("new-token");

    await act(async () => {
      await currentAuth.updateProfile({ display_name: "Owner", username: "updated", email: user.email });
    });
    expect(screen.getByText("updated")).toBeInTheDocument();
    await act(async () => {
      await currentAuth.changePassword({ current_password: "secret", new_password: "new-secret" });
    });
    expect(api.changePassword).toHaveBeenCalledWith({
      current_password: "secret",
      new_password: "new-secret",
    });
    await act(async () => { await currentAuth.uploadAvatar(new File(["x"], "a.png")); });
    expect(currentAuth.user?.avatar_url).toBe("/avatar.png");
    await act(async () => { await currentAuth.deleteAvatar(); });
    expect(currentAuth.user?.avatar_url).toBeNull();
  });

  it("removes the token when fetching the user after login fails", async () => {
    vi.mocked(api.getMe).mockReset().mockRejectedValue(new Error("failed"));
    render(<AuthProvider><Probe /></AuthProvider>);
    await screen.findByText("anonymous");
    let failure: unknown;
    await act(async () => {
      try {
        await currentAuth.login("owner", "secret");
      } catch (cause) {
        failure = cause;
      }
    });
    expect(failure).toEqual(new Error("failed"));
    await waitFor(() => expect(localStorage.getItem(TOKEN_KEY)).toBeNull());
  });

  it("clears the session after account deletion succeeds", async () => {
    localStorage.setItem(TOKEN_KEY, "stored");
    render(<AuthProvider><Probe /></AuthProvider>);
    await screen.findByText("owner");
    await act(async () => {
      await currentAuth.deleteAccount({
        current_password: "secret",
        confirmation: "XÓA TÀI KHOẢN",
      });
    });
    expect(screen.getByText("anonymous")).toBeInTheDocument();
    expect(localStorage.getItem(TOKEN_KEY)).toBeNull();
  });

  it("logs out for unauthorized and cross-tab removal events", async () => {
    localStorage.setItem(TOKEN_KEY, "stored");
    render(<AuthProvider><Probe /></AuthProvider>);
    await screen.findByText("owner");
    act(() => window.dispatchEvent(new Event(AUTH_UNAUTHORIZED_EVENT)));
    expect(screen.getByText("anonymous")).toBeInTheDocument();

    await act(async () => { await currentAuth.login("owner", "secret"); });
    act(() => window.dispatchEvent(new StorageEvent("storage", { key: TOKEN_KEY, newValue: null })));
    expect(screen.getByText("anonymous")).toBeInTheDocument();
  });
});

describe("route guards", () => {
  beforeEach(() => {
    vi.spyOn(api, "getMe").mockResolvedValue(user);
  });

  it("redirects an anonymous protected route to login", async () => {
    render(
      <AuthProvider>
        <MemoryRouter initialEntries={["/dashboard"]}>
          <Routes>
            <Route element={<ProtectedRoute />}><Route path="/dashboard" element={<div>dashboard</div>} /></Route>
            <Route path="/login" element={<div>login</div>} />
          </Routes>
        </MemoryRouter>
      </AuthProvider>,
    );
    await screen.findByText("login");
  });

  it("renders a protected route and redirects public-only routes for a user", async () => {
    localStorage.setItem(TOKEN_KEY, "stored");
    const { unmount } = render(
      <AuthProvider>
        <MemoryRouter initialEntries={["/dashboard"]}>
          <Routes>
            <Route element={<ProtectedRoute />}><Route path="/dashboard" element={<div>dashboard</div>} /></Route>
          </Routes>
        </MemoryRouter>
      </AuthProvider>,
    );
    expect(screen.getByText("Đang kiểm tra phiên truy cập…")).toBeInTheDocument();
    await screen.findByText("dashboard");
    unmount();

    render(
      <AuthProvider>
        <MemoryRouter initialEntries={["/login"]}>
          <Routes>
            <Route element={<PublicOnlyRoute />}><Route path="/login" element={<div>login form</div>} /></Route>
            <Route path="/dashboard" element={<div>redirect dashboard</div>} />
          </Routes>
        </MemoryRouter>
      </AuthProvider>,
    );
    await screen.findByText("redirect dashboard");
  });

  it("renders a public-only route for anonymous users", async () => {
    render(
      <AuthProvider>
        <MemoryRouter initialEntries={["/login"]}>
          <Routes>
            <Route element={<PublicOnlyRoute />}><Route path="/login" element={<div>login form</div>} /></Route>
          </Routes>
        </MemoryRouter>
      </AuthProvider>,
    );
    await waitFor(() => expect(screen.getByText("login form")).toBeInTheDocument());
  });
});
