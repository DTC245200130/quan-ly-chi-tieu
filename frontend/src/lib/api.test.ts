import { beforeEach, describe, expect, it, vi } from "vitest";

import { api, ApiError, AUTH_UNAUTHORIZED_EVENT, TOKEN_KEY } from "./api";

const response = (body: unknown, status = 200, ok = status >= 200 && status < 300) => ({
  ok,
  status,
  json: vi.fn().mockResolvedValue(body),
});

const goal = {
  id: "g1",
  name: "Goal",
  target_amount: "100",
  current_amount: "bad-number",
  completion_amount: "50",
  completion_mode: null,
  deadline: null,
  status: "active",
  items: [{ id: "i1", name: "Item", cost: "12", is_purchased: false }],
};

const evidence = {
  current_period: { month: 8, year: 2026 },
  previous_period: { month: 7, year: 2026 },
  current: { income: "100", expense: "bad", net: "50", transaction_count: 1 },
  previous: { income: "80", expense: "20", net: "60", transaction_count: 1 },
  available_balance: "30",
  expense_difference: "5",
  expense_change_percentage: null,
  categories: [{
    label: "Food", icon: "wallet", current_amount: "10", previous_amount: "5",
    difference: "5", current_share: "25", current_transaction_count: 1,
  }],
  forecast: {
    elapsed_days: 1, days_in_month: 31, average_expense_per_day: "2",
    projected_expense: "62", projected_net: "38", confidence: "low",
  },
  active_budget_count: 0,
  over_budget_count: 0,
  active_goal_count: 1,
  goal_target_total: "100",
  goal_saved_total: "10",
};

describe("api request and normalization", () => {
  beforeEach(() => {
    vi.stubGlobal("fetch", vi.fn());
  });

  it("adds JSON and authorization headers and handles 204", async () => {
    localStorage.setItem(TOKEN_KEY, "token");
    vi.mocked(fetch).mockResolvedValueOnce(response(undefined, 204) as unknown as Response);
    await expect(api.deleteAssistantConversation("thread")).resolves.toBeUndefined();
    expect(fetch).toHaveBeenCalledWith("/api/assistant/conversations/thread", expect.objectContaining({
      method: "DELETE",
      headers: expect.objectContaining({
        "Content-Type": "application/json",
        Authorization: "Bearer token",
      }),
    }));
  });

  it("uses form encoding for login and multipart for avatar", async () => {
    vi.mocked(fetch)
      .mockResolvedValueOnce(response({ access_token: "t", token_type: "bearer" }) as unknown as Response)
      .mockResolvedValueOnce(response({ id: "u" }) as unknown as Response);
    await api.login("owner", "secret");
    const loginInit = vi.mocked(fetch).mock.calls[0][1] as RequestInit;
    expect(loginInit.headers).toEqual(expect.objectContaining({
      "Content-Type": "application/x-www-form-urlencoded",
    }));
    expect(loginInit.body).toBeInstanceOf(URLSearchParams);

    await api.uploadAvatar(new File(["avatar"], "a.png", { type: "image/png" }));
    const uploadInit = vi.mocked(fetch).mock.calls[1][1] as RequestInit;
    expect(uploadInit.body).toBeInstanceOf(FormData);
    expect(uploadInit.headers).not.toHaveProperty("Content-Type");
  });

  it("extracts string and validation errors", async () => {
    vi.mocked(fetch)
      .mockResolvedValueOnce(response({ detail: "Duplicate" }, 400, false) as unknown as Response)
      .mockResolvedValueOnce(response({ detail: [{ msg: "Invalid field" }] }, 422, false) as unknown as Response)
      .mockResolvedValueOnce(response({}, 500, false) as unknown as Response);
    await expect(api.register({ username: "x", email: "x@example.com", password: "secret" }))
      .rejects.toEqual(expect.objectContaining({ name: "ApiError", message: "Duplicate", status: 400 }));
    await expect(api.register({ username: "x", email: "x@example.com", password: "secret" }))
      .rejects.toThrow("Invalid field");
    await expect(api.register({ username: "x", email: "x@example.com", password: "secret" }))
      .rejects.toThrow("Không thể kết nối với máy chủ");
  });

  it("dispatches unauthorized only for authenticated non-login requests", async () => {
    const listener = vi.fn();
    window.addEventListener(AUTH_UNAUTHORIZED_EVENT, listener);
    localStorage.setItem(TOKEN_KEY, "token");
    vi.mocked(fetch).mockResolvedValue(response(null, 401, false) as unknown as Response);
    await expect(api.getMe()).rejects.toBeInstanceOf(ApiError);
    expect(listener).toHaveBeenCalledOnce();

    await expect(api.login("owner", "bad")).rejects.toThrow("Phiên đăng nhập");
    expect(listener).toHaveBeenCalledOnce();
    window.removeEventListener(AUTH_UNAUTHORIZED_EVENT, listener);
  });

  it("builds transaction filters and normalizes transaction amounts", async () => {
    vi.mocked(fetch).mockResolvedValueOnce(response([{ id: "t", amount: "12.5" }]) as unknown as Response);
    const result = await api.listTransactions({ category_id: "c", keyword: "", type: "expense" });
    expect(result[0].amount).toBe(12.5);
    expect(vi.mocked(fetch).mock.calls[0][0]).toBe("/api/transactions/?category_id=c&type=expense");

    vi.mocked(fetch).mockResolvedValueOnce(response({ id: "t", amount: "invalid" }) as unknown as Response);
    expect((await api.createTransaction({ category_id: "c", amount: 1, txn_date: "2026-01-01", note: null })).amount).toBe(0);
  });

  it("normalizes every nested dashboard numeric field", async () => {
    const body = {
      month: 8,
      year: 2026,
      summary: { income: "100", expense: "bad", net: "50", available_balance: "25" },
      spending_by_category: [{ amount: "10", percentage: "20" }],
      trend: [{ income: "3", expense: "4" }],
      budgets: [{ limit_amount: "20", spent: "10", remaining: "10", usage_percentage: "50" }],
      goals: [{ target_amount: "100", current_amount: "20", progress_percentage: "20" }],
      recent_transactions: [{ amount: "8" }],
    };
    vi.mocked(fetch).mockResolvedValueOnce(response(body) as unknown as Response);
    const result = await api.getDashboard(8, 2026);
    expect(result.summary).toEqual({ income: 100, expense: 0, net: 50, available_balance: 25 });
    expect(result.spending_by_category[0].percentage).toBe(20);
    expect(result.trend[0].expense).toBe(4);
    expect(result.budgets[0].usage_percentage).toBe(50);
    expect(result.goals[0].current_amount).toBe(20);
    expect(result.recent_transactions[0].amount).toBe(8);
  });

  it("normalizes reports including nullable percentages", async () => {
    const totals = { income: "1", expense: "2", net: "-1" };
    vi.mocked(fetch).mockResolvedValueOnce(response({
      current_period: { month: 8, year: 2026 },
      previous_period: { month: 7, year: 2026 },
      summary: {
        current: totals, previous: totals,
        income_difference: "0", expense_difference: "0", net_difference: "0",
        income_change_percentage: null, expense_change_percentage: "10", net_change_percentage: "bad",
      },
      categories: [{
        current_amount: "1", current_share: "2", current_transaction_count: "3",
        previous_amount: "4", previous_share: "5", previous_transaction_count: "6",
        difference: "-3", change_percentage: null,
      }],
      has_data: true,
    }) as unknown as Response);
    const result = await api.getReport(8, 2026);
    expect(result.summary.expense_change_percentage).toBe(10);
    expect(result.summary.net_change_percentage).toBe(0);
    expect(result.categories[0].previous_transaction_count).toBe(6);
    expect(result.categories[0].change_percentage).toBeNull();
  });

  it("normalizes assistant evidence and conversations", async () => {
    vi.mocked(fetch)
      .mockResolvedValueOnce(response({ evidence, has_data: true, privacy_notes: [], model: "m" }) as unknown as Response)
      .mockResolvedValueOnce(response({ id: "c", messages: [{ evidence }, { evidence: null }] }) as unknown as Response)
      .mockResolvedValueOnce(response({ conversation: { id: "c", messages: [{ evidence }] }, model: "m" }) as unknown as Response);
    const context = await api.getAssistantContext(8, 2026);
    expect(context.evidence.current.expense).toBe(0);
    expect(context.evidence.forecast.projected_expense).toBe(62);
    expect(context.evidence.expense_change_percentage).toBeNull();
    expect((await api.getAssistantConversation("c")).messages[0].evidence?.goal_saved_total).toBe(10);
    expect((await api.askAssistant({ question: "q", month: 8, year: 2026 })).conversation.messages[0].evidence?.available_balance).toBe(30);
  });

  it("normalizes goals and goal transactions across all mutations", async () => {
    vi.mocked(fetch)
      .mockResolvedValueOnce(response([goal]) as unknown as Response)
      .mockResolvedValue(response(goal) as unknown as Response);
    expect((await api.listGoals())[0].current_amount).toBe(0);
    expect((await api.createGoal({ name: "G", target_amount: 100, deadline: null })).items[0].cost).toBe(12);
    expect((await api.updateGoal("g1", { name: "G2" })).completion_amount).toBe(50);
    expect((await api.depositGoal("g1", 10, null)).target_amount).toBe(100);
    expect((await api.withdrawGoal("g1", 5, "note")).target_amount).toBe(100);
    expect((await api.completeGoal("g1", { mode: "keep", note: null })).target_amount).toBe(100);
    expect((await api.addGoalItem("g1", "I", 1)).target_amount).toBe(100);
    expect((await api.updateGoalItem("g1", "i1", { is_purchased: true })).target_amount).toBe(100);
    expect((await api.deleteGoalItem("g1", "i1")).target_amount).toBe(100);

    vi.mocked(fetch).mockResolvedValueOnce(response([{ id: "gt", amount: "7" }]) as unknown as Response);
    expect((await api.listGoalTransactions("g1"))[0].amount).toBe(7);
  });

  it("normalizes decimal budget fields for list, create and update", async () => {
    const serialized = {
      id: "b", category_id: "c", month: 8, year: 2026,
      limit_amount: "100.50", spent: "25.25", is_over: false,
    };
    vi.mocked(fetch)
      .mockResolvedValueOnce(response([serialized]) as unknown as Response)
      .mockResolvedValueOnce(response(serialized) as unknown as Response)
      .mockResolvedValueOnce(response({ ...serialized, limit_amount: "invalid", spent: "invalid" }) as unknown as Response);

    expect((await api.listBudgets(8, 2026))[0]).toEqual(expect.objectContaining({
      limit_amount: 100.5, spent: 25.25,
    }));
    expect(await api.createBudget({ category_id: "c", month: 8, year: 2026, limit_amount: 100.5 }))
      .toEqual(expect.objectContaining({ limit_amount: 100.5, spent: 25.25 }));
    expect(await api.updateBudget("b", 200))
      .toEqual(expect.objectContaining({ limit_amount: 0, spent: 0 }));
  });

  it("covers simple CRUD endpoint wrappers", async () => {
    vi.mocked(fetch).mockResolvedValue(response({ message: "ok" }) as unknown as Response);
    await api.getMe();
    await api.updateProfile({ display_name: "A", username: "a", email: "a@example.com" });
    await api.changePassword({ current_password: "old-secret", new_password: "new-secret" });
    await api.deleteAccount({ current_password: "old-secret", confirmation: "XÓA TÀI KHOẢN" });
    await api.deleteAvatar();
    await api.forgotPassword("a@example.com");
    await api.resetPassword("token", "secret");
    await api.listAssistantConversations();
    await api.listCategories();
    await api.createCategory({ name: "C", type: "expense", color: "#000", icon: "wallet" });
    await api.updateCategory("c", { name: "D" });
    await api.deleteCategory("c");
    await api.updateTransaction("t", { note: "n" });
    await api.deleteTransaction("t");
    await api.deleteBudget("b");
    await api.deleteGoal("g");
    expect(fetch).toHaveBeenCalledTimes(16);
  });
});
