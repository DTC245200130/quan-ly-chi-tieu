import { fireEvent, render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";

import App from "../../App";
import { api } from "../../lib/api";

const user = {
  id: "u1", username: "owner", email: "owner@example.com",
  display_name: null, avatar_url: null,
};

function renderPublic(path: string) {
  return render(<MemoryRouter initialEntries={[path]}><App /></MemoryRouter>);
}

describe("authentication pages", () => {
  beforeEach(() => {
    vi.spyOn(api, "login").mockResolvedValue({ access_token: "token", token_type: "bearer" });
    vi.spyOn(api, "getMe").mockResolvedValue(user);
    vi.spyOn(api, "register").mockResolvedValue(user);
    vi.spyOn(api, "forgotPassword").mockResolvedValue({ message: "sent" });
    vi.spyOn(api, "resetPassword").mockResolvedValue({ message: "reset" });
    vi.spyOn(api, "getDashboard").mockResolvedValue({
      month: 8, year: 2026,
      summary: { income: 0, expense: 0, net: 0, available_balance: 0 },
      spending_by_category: [], trend: [], budgets: [], goals: [], recent_transactions: [],
    });
  });

  it("validates login and displays an API failure", async () => {
    const { container } = renderPublic("/login");
    await screen.findByRole("heading", { name: "Chào mừng bạn trở lại" });
    fireEvent.submit(container.querySelector("form")!);
    expect(await screen.findByRole("alert")).toHaveTextContent("Hãy nhập tên đăng nhập");

    vi.mocked(api.login).mockRejectedValueOnce(new Error("Sai thông tin"));
    await userEvent.type(screen.getByLabelText("Tên đăng nhập hoặc email"), "owner");
    await userEvent.type(screen.getByLabelText("Mật khẩu"), "wrongpass");
    fireEvent.submit(container.querySelector("form")!);
    expect(await screen.findByRole("alert")).toHaveTextContent("Sai thông tin");
  });

  it("logs in successfully and reaches the dashboard", async () => {
    const { container } = renderPublic("/login");
    await userEvent.type(await screen.findByLabelText("Tên đăng nhập hoặc email"), " owner ");
    await userEvent.type(screen.getByLabelText("Mật khẩu"), "secret");
    fireEvent.submit(container.querySelector("form")!);
    expect(await screen.findByRole("heading", { level: 1, name: "Tổng quan" })).toBeInTheDocument();
    expect(api.login).toHaveBeenCalledWith("owner", "secret");
  });

  it("validates registration branches then submits normalized values", async () => {
    const { container } = renderPublic("/register");
    const form = container.querySelector("form")!;
    await userEvent.type(screen.getByLabelText("Tên đăng nhập"), "x");
    fireEvent.submit(form);
    expect(await screen.findByRole("alert")).toHaveTextContent("ít nhất 3");

    await userEvent.clear(screen.getByLabelText("Tên đăng nhập"));
    await userEvent.type(screen.getByLabelText("Tên đăng nhập"), " owner ");
    await userEvent.type(screen.getByPlaceholderText("ban@email.com"), "OWNER@EXAMPLE.COM");
    await userEvent.type(screen.getByLabelText("Mật khẩu"), "123");
    fireEvent.submit(form);
    expect(await screen.findByRole("alert")).toHaveTextContent("Mật khẩu phải có ít nhất 6");

    await userEvent.clear(screen.getByLabelText("Mật khẩu"));
    await userEvent.type(screen.getByLabelText("Mật khẩu"), "secret1");
    await userEvent.type(screen.getByLabelText("Xác nhận mật khẩu"), "secret2");
    fireEvent.submit(form);
    expect(await screen.findByRole("alert")).toHaveTextContent("chưa khớp");

    await userEvent.clear(screen.getByLabelText("Xác nhận mật khẩu"));
    await userEvent.type(screen.getByLabelText("Xác nhận mật khẩu"), "secret1");
    fireEvent.submit(form);
    expect(await screen.findByRole("heading", { name: "Chào mừng bạn trở lại" })).toBeInTheDocument();
    expect(api.register).toHaveBeenCalledWith({
      username: "owner", email: "owner@example.com", password: "secret1",
    });
    expect(screen.getByText("Tạo tài khoản thành công. Bạn có thể đăng nhập ngay.")).toBeInTheDocument();
  });

  it("submits forgot password and can return to the form", async () => {
    const { container } = renderPublic("/forgot-password");
    await userEvent.type(await screen.findByLabelText("Email"), " OWNER@EXAMPLE.COM ");
    fireEvent.submit(container.querySelector("form")!);
    expect(await screen.findByRole("heading", { name: "Kiểm tra hộp thư của bạn" })).toBeInTheDocument();
    expect(api.forgotPassword).toHaveBeenCalledWith("owner@example.com");
    await userEvent.click(screen.getByRole("button", { name: "Dùng email khác" }));
    expect(screen.getByRole("heading", { name: "Khôi phục mật khẩu" })).toBeInTheDocument();
  });

  it("handles missing token and validates then completes reset", async () => {
    const { unmount } = renderPublic("/reset-password");
    expect(await screen.findByRole("heading", { name: "Liên kết không hợp lệ" })).toBeInTheDocument();
    unmount();

    const { container } = renderPublic("/reset-password?token= reset-token ");
    await screen.findByRole("heading", { name: "Đặt mật khẩu mới" });
    fireEvent.submit(container.querySelector("form")!);
    expect(await screen.findByRole("alert")).toHaveTextContent("ít nhất 6");
    await userEvent.type(screen.getByLabelText("Mật khẩu mới"), "secret1");
    await userEvent.type(screen.getByLabelText("Xác nhận mật khẩu mới"), "secret2");
    fireEvent.submit(container.querySelector("form")!);
    expect(await screen.findByRole("alert")).toHaveTextContent("chưa khớp");
    await userEvent.clear(screen.getByLabelText("Xác nhận mật khẩu mới"));
    await userEvent.type(screen.getByLabelText("Xác nhận mật khẩu mới"), "secret1");
    fireEvent.submit(container.querySelector("form")!);
    expect(await screen.findByRole("heading", { name: "Chào mừng bạn trở lại" })).toBeInTheDocument();
    expect(api.resetPassword).toHaveBeenCalledWith("reset-token", "secret1");
  });
});
