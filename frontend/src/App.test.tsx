import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";

import App from "./App";
import { api, TOKEN_KEY } from "./lib/api";

const user = {
  id: "u1", username: "owner", email: "owner@example.com",
  display_name: "Owner", avatar_url: null,
};
const categories = [
  { id: "food", name: "Ăn uống", type: "expense" as const, color: "#07845c", icon: "utensils" as const },
  { id: "salary", name: "Lương", type: "income" as const, color: "#2563eb", icon: "banknote" as const },
];
const transactions = [
  { id: "t1", category_id: "food", amount: 120, type: "expense" as const, txn_date: "2026-08-20", note: "Lunch" },
  { id: "t2", category_id: "salary", amount: 1000, type: "income" as const, txn_date: "2026-08-01", note: null },
];
const budgets = [
  { id: "b1", category_id: "food", month: 8, year: 2026, limit_amount: 100, spent: 120, is_over: true },
];
const goals = [
  {
    id: "g1", name: "Laptop", target_amount: 1000, deadline: "2026-12-31",
    status: "active" as const, current_amount: 500, completion_amount: null, completion_mode: null,
    items: [{ id: "i1", name: "Mouse", cost: 20, is_purchased: false }],
  },
  {
    id: "g2", name: "Trip", target_amount: 500, deadline: null,
    status: "completed" as const, current_amount: 500, completion_amount: 500, completion_mode: "keep" as const,
    items: [],
  },
];
const evidence = {
  current_period: { month: 8, year: 2026 }, previous_period: { month: 7, year: 2026 },
  current: { income: 1000, expense: 120, net: 880, transaction_count: 2 },
  previous: { income: 900, expense: 100, net: 800, transaction_count: 2 },
  available_balance: 880, expense_difference: 20, expense_change_percentage: 20,
  categories: [{
    label: "Ăn uống", icon: "utensils", current_amount: 120, previous_amount: 100,
    difference: 20, current_share: 100, current_transaction_count: 1,
  }],
  forecast: {
    elapsed_days: 20, days_in_month: 31, average_expense_per_day: 6,
    projected_expense: 186, projected_net: 814, confidence: "low" as const,
  },
  active_budget_count: 1, over_budget_count: 1, active_goal_count: 1,
  goal_target_total: 1000, goal_saved_total: 500,
};
const dashboard = {
  month: 8, year: 2026,
  summary: { income: 1000, expense: 120, net: 880, available_balance: 880 },
  spending_by_category: [{
    category_id: "food", category_name: "Ăn uống", color: "#07845c", icon: "utensils" as const,
    amount: 120, percentage: 100,
  }],
  trend: [
    { month: 6, year: 2026, income: 800, expense: 90 },
    { month: 7, year: 2026, income: 900, expense: 100 },
    { month: 8, year: 2026, income: 1000, expense: 120 },
  ],
  budgets: [{
    id: "b1", category_id: "food", category_name: "Ăn uống", color: "#07845c", icon: "utensils" as const,
    limit_amount: 100, spent: 120, remaining: -20, usage_percentage: 120, is_over: true, status: "over" as const,
  }],
  goals: [{
    id: "g1", name: "Laptop", target_amount: 1000, current_amount: 500,
    progress_percentage: 50, deadline: "2026-12-31", status: "active",
  }],
  recent_transactions: [{
    id: "t1", category_id: "food", category_name: "Ăn uống", category_color: "#07845c",
    category_icon: "utensils" as const, amount: 120, type: "expense" as const,
    txn_date: "2026-08-20", note: "Lunch",
  }],
};
const report = {
  current_period: { month: 8, year: 2026 }, previous_period: { month: 7, year: 2026 },
  summary: {
    current: { income: 1000, expense: 120, net: 880 },
    previous: { income: 900, expense: 100, net: 800 },
    income_difference: 100, expense_difference: 20, net_difference: 80,
    income_change_percentage: 11.1, expense_change_percentage: 20, net_change_percentage: 10,
  },
  categories: [
    {
      category_id: "food", category_name: "Ăn uống", icon: "utensils" as const,
      current_amount: 120, current_share: 100, current_transaction_count: 2,
      previous_amount: 100, previous_share: 100, previous_transaction_count: 1,
      difference: 20, change_percentage: 20,
    },
    {
      category_id: "travel", category_name: "Du lịch", icon: "plane" as const,
      current_amount: 0, current_share: 0, current_transaction_count: 0,
      previous_amount: 50, previous_share: 50, previous_transaction_count: 1,
      difference: -50, change_percentage: -100,
    },
  ],
  has_data: true,
};
const conversations = [{
  id: "c1", title: "Spending", preview: "Advice", message_count: 2,
  created_at: "2026-08-01T00:00:00Z", updated_at: "2026-08-02T00:00:00Z",
}];

function renderApp(path: string) {
  localStorage.setItem(TOKEN_KEY, "token");
  return render(<MemoryRouter initialEntries={[path]}><App /></MemoryRouter>);
}

describe("application route smoke tests", () => {
  beforeEach(() => {
    vi.spyOn(api, "getMe").mockResolvedValue(user);
    vi.spyOn(api, "getDashboard").mockResolvedValue(dashboard);
    vi.spyOn(api, "listCategories").mockResolvedValue(categories);
    vi.spyOn(api, "listTransactions").mockResolvedValue(transactions);
    vi.spyOn(api, "listBudgets").mockResolvedValue(budgets);
    vi.spyOn(api, "listGoals").mockResolvedValue(goals);
    vi.spyOn(api, "listGoalTransactions").mockResolvedValue([
      { id: "gt1", amount: 500, type: "deposit", txn_date: "2026-08-10", note: "Saved" },
    ]);
    vi.spyOn(api, "getReport").mockResolvedValue(report);
    vi.spyOn(api, "getAssistantContext").mockResolvedValue({
      evidence, has_data: true, privacy_notes: ["Aggregated only"], model: "gemini-test",
    });
    vi.spyOn(api, "listAssistantConversations").mockResolvedValue(conversations);
    vi.spyOn(api, "updateProfile").mockResolvedValue({ ...user, display_name: "Owner Updated" });
    vi.spyOn(api, "changePassword").mockResolvedValue({ message: "Đổi mật khẩu thành công." });
    vi.spyOn(api, "deleteAccount").mockResolvedValue({ message: "Tài khoản và dữ liệu cá nhân đã được xóa." });
    vi.spyOn(api, "uploadAvatar").mockResolvedValue({ ...user, avatar_url: "/avatar.png" });
    vi.spyOn(api, "deleteAvatar").mockResolvedValue(user);
  });

  it.each([
    ["/dashboard", "Tổng quan"],
    ["/transactions", "Giao dịch"],
    ["/categories", "Danh mục"],
    ["/reports", "Báo cáo"],
  ])("renders %s with successful API data", async (path, heading) => {
    renderApp(path);
    expect(await screen.findByRole("heading", { level: 1, name: heading })).toBeInTheDocument();
  });

  it.each(["/budgets", "/goals", "/assistant"])("redirects removed page %s to overview", async (path) => {
    renderApp(path);
    expect(await screen.findByRole("heading", { level: 1, name: "Tổng quan" })).toBeInTheDocument();
    expect(api.listBudgets).not.toHaveBeenCalled();
    expect(api.listGoals).not.toHaveBeenCalled();
    expect(api.getAssistantContext).not.toHaveBeenCalled();
  });

  it("opens navigation/profile controls, saves profile and logs out", async () => {
    renderApp("/dashboard");
    await screen.findByRole("heading", { level: 1, name: "Tổng quan" });

    const navigation = screen.getByRole("navigation", { name: "Điều hướng chính" });
    expect(navigation.querySelectorAll("a")).toHaveLength(4);
    expect(screen.queryByRole("link", { name: "Ngân sách" })).not.toBeInTheDocument();
    expect(screen.queryByRole("link", { name: "Mục tiêu" })).not.toBeInTheDocument();
    expect(screen.queryByRole("link", { name: "Trợ lý AI" })).not.toBeInTheDocument();

    await userEvent.click(screen.getAllByTitle("Chỉnh sửa thông tin cá nhân")[0]);
    expect(await screen.findByRole("dialog", { name: "Thông tin cá nhân" })).toBeInTheDocument();
    const displayName = screen.getByPlaceholderText("Ví dụ: Minh Đỗ");
    await userEvent.clear(displayName);
    await userEvent.type(displayName, "Owner Updated");
    await userEvent.click(screen.getByRole("button", { name: "Lưu thay đổi" }));
    await screen.findByText("Thông tin cá nhân đã được cập nhật.");
    expect(api.updateProfile).toHaveBeenCalledWith(expect.objectContaining({ display_name: "Owner Updated" }));
    const closeButtons = screen.getAllByRole("button", { name: "Đóng" });
    await userEvent.click(closeButtons[closeButtons.length - 1]);

    await userEvent.click(screen.getAllByRole("button", { name: "Đăng xuất" })[0]);
    expect(await screen.findByRole("heading", { name: "Chào mừng bạn trở lại" })).toBeInTheDocument();
    expect(screen.getByText("Bạn đã đăng xuất an toàn.")).toBeInTheDocument();
  });

  it("validates avatar files in the profile panel", async () => {
    const { container } = renderApp("/dashboard");
    await screen.findByRole("heading", { level: 1, name: "Tổng quan" });
    await userEvent.click(screen.getAllByTitle("Chỉnh sửa thông tin cá nhân")[0]);
    const input = document.body.querySelector('input[type="file"]') as HTMLInputElement;
    fireEvent.change(input, { target: { files: [new File(["x"], "bad.txt", { type: "text/plain" })] } });
    expect(await screen.findByRole("alert")).toHaveTextContent("PNG, JPEG hoặc WebP");

    const large = new File([new Uint8Array(2 * 1024 * 1024 + 1)], "large.png", { type: "image/png" });
    fireEvent.change(input, { target: { files: [large] } });
    expect(await screen.findByRole("alert")).toHaveTextContent("2 MB");

    fireEvent.change(input, { target: { files: [new File(["x"], "ok.png", { type: "image/png" })] } });
    await waitFor(() => expect(api.uploadAvatar).toHaveBeenCalledOnce());
  });

  it("validates and changes the password from the profile panel", async () => {
    renderApp("/dashboard");
    await screen.findByRole("heading", { level: 1, name: "Tổng quan" });
    await userEvent.click(screen.getAllByTitle("Chỉnh sửa thông tin cá nhân")[0]);

    await userEvent.type(screen.getByLabelText("Mật khẩu hiện tại"), "secret");
    await userEvent.type(screen.getByLabelText(/^Mật khẩu mới/), "new-secret");
    await userEvent.type(screen.getByLabelText("Xác nhận mật khẩu mới"), "different");
    await userEvent.click(screen.getByRole("button", { name: "Đổi mật khẩu" }));
    expect(await screen.findByRole("alert")).toHaveTextContent("chưa khớp");
    expect(api.changePassword).not.toHaveBeenCalled();

    await userEvent.clear(screen.getByLabelText("Xác nhận mật khẩu mới"));
    await userEvent.type(screen.getByLabelText("Xác nhận mật khẩu mới"), "new-secret");
    await userEvent.click(screen.getByRole("button", { name: "Đổi mật khẩu" }));
    expect(await screen.findByText("Đổi mật khẩu thành công.")).toBeInTheDocument();
    expect(api.changePassword).toHaveBeenCalledWith({
      current_password: "secret",
      new_password: "new-secret",
    });
    expect(screen.getByLabelText("Mật khẩu hiện tại")).toHaveValue("");
  });

  it("requires both account deletion confirmations and returns to login", async () => {
    renderApp("/dashboard");
    await screen.findByRole("heading", { level: 1, name: "Tổng quan" });
    await userEvent.click(screen.getAllByTitle("Chỉnh sửa thông tin cá nhân")[0]);
    await userEvent.click(screen.getByRole("button", { name: "Bắt đầu xóa tài khoản" }));

    const deleteButton = screen.getByRole("button", { name: "Xóa vĩnh viễn" });
    expect(deleteButton).toBeDisabled();
    await userEvent.type(screen.getAllByLabelText("Mật khẩu hiện tại")[1], "secret");
    await userEvent.type(screen.getByLabelText("Nhập XÓA TÀI KHOẢN để xác nhận"), "XÓA TÀI KHOẢN");
    expect(deleteButton).toBeEnabled();
    await userEvent.click(deleteButton);

    expect(api.deleteAccount).toHaveBeenCalledWith({
      current_password: "secret",
      confirmation: "XÓA TÀI KHOẢN",
    });
    expect(await screen.findByRole("heading", { name: "Chào mừng bạn trở lại" })).toBeInTheDocument();
  });

  it("shows and retries dashboard load errors", async () => {
    vi.mocked(api.getDashboard).mockRejectedValueOnce(new Error("dashboard failed"));
    renderApp("/dashboard");
    expect(await screen.findByText(/Không thể tải dữ liệu Dashboard/)).toBeInTheDocument();
    await userEvent.click(screen.getByRole("button", { name: "Thử lại" }));
    await waitFor(() => expect(screen.queryByText(/Không thể tải dữ liệu Dashboard/)).not.toBeInTheDocument());
    expect(api.getDashboard).toHaveBeenCalledTimes(2);
  });

  it("shows and retries transaction load errors", async () => {
    vi.mocked(api.listTransactions).mockRejectedValueOnce(new Error("transactions failed"));
    renderApp("/transactions");
    expect(await screen.findByRole("alert")).toHaveTextContent("transactions failed");
    await userEvent.click(screen.getByRole("button", { name: /Thử lại/ }));
    await waitFor(() => expect(screen.queryByRole("alert")).not.toBeInTheDocument());
  });

  it("shows and retries category load errors", async () => {
    vi.mocked(api.listCategories).mockRejectedValueOnce(new Error("categories failed"));
    renderApp("/categories");
    expect(await screen.findByRole("alert")).toHaveTextContent("categories failed");
    await userEvent.click(screen.getByRole("button", { name: /Thử lại/ }));
    await waitFor(() => expect(screen.queryByRole("alert")).not.toBeInTheDocument());
  });



  it("shows and retries report load errors", async () => {
    vi.mocked(api.getReport).mockRejectedValueOnce(new Error("report failed"));
    renderApp("/reports");
    expect(await screen.findByRole("alert")).toHaveTextContent("report failed");
    await userEvent.click(screen.getByRole("button", { name: /Thử lại/ }));
    await waitFor(() => expect(screen.queryByRole("alert")).not.toBeInTheDocument());
  });

});
