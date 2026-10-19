import type {
  AssistantAskPayload,
  AssistantContext,
  AssistantConversation,
  AssistantConversationSummary,
  AssistantEvidence,
  AssistantReply,
  Budget,
  BudgetPayload,
  ChangePasswordPayload,
  DeleteAccountPayload,
  Category,
  CategoryPayload,
  DashboardData,
  Goal,
  GoalCompletePayload,
  GoalItem,
  GoalPayload,
  GoalTransaction,
  AuthToken,
  MessageResponse,
  RegisterPayload,
  ReportData,
  Transaction,
  TransactionFilters,
  TransactionPayload,
  User,
  UserProfilePayload,
} from "../types";

const API_BASE = (import.meta.env.VITE_API_BASE_URL ?? "/api").replace(/\/+$/, "");
export const TOKEN_KEY = "access_token";
export const AUTH_UNAUTHORIZED_EVENT = "auth:unauthorized";

export class ApiError extends Error {
  status: number;

  constructor(message: string, status: number) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const token = localStorage.getItem(TOKEN_KEY);
  const usesFormData = init?.body instanceof FormData;
  const response = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: {
      ...(!usesFormData ? { "Content-Type": "application/json" } : {}),
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...init?.headers,
    },
  });

  if (!response.ok) {
    const body = await response.json().catch(() => null) as { detail?: unknown } | null;
    const validationMessage = Array.isArray(body?.detail)
      ? body.detail.find((item): item is { msg: string } => Boolean(item) && typeof item === "object" && "msg" in item && typeof item.msg === "string")?.msg
      : undefined;
    const message = typeof body?.detail === "string"
      ? body.detail
      : validationMessage
        ? validationMessage
        : response.status === 401
          ? "Phiên đăng nhập không hợp lệ hoặc đã hết hạn."
          : "Không thể kết nối với máy chủ. Vui lòng thử lại.";
    if (response.status === 401 && token && path !== "/auth/login") {
      window.dispatchEvent(new Event(AUTH_UNAUTHORIZED_EVENT));
    }
    throw new ApiError(message, response.status);
  }

  if (response.status === 204) return undefined as T;
  return response.json() as Promise<T>;
}

const asNumber = (value: number) => {
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : 0;
};

const normalizeTransaction = (transaction: Transaction): Transaction => ({
  ...transaction,
  amount: asNumber(transaction.amount),
});

const normalizeBudget = (budget: Budget): Budget => ({
  ...budget,
  limit_amount: asNumber(budget.limit_amount),
  spent: asNumber(budget.spent),
});

const normalizeGoalItem = (item: GoalItem): GoalItem => ({
  ...item,
  cost: asNumber(item.cost),
});

const normalizeGoal = (goal: Goal): Goal => ({
  ...goal,
  target_amount: asNumber(goal.target_amount),
  current_amount: asNumber(goal.current_amount),
  completion_amount: goal.completion_amount == null ? null : asNumber(goal.completion_amount),
  items: goal.items.map(normalizeGoalItem),
});

const normalizeGoalTransaction = (transaction: GoalTransaction): GoalTransaction => ({
  ...transaction,
  amount: asNumber(transaction.amount),
});

const normalizeDashboard = (data: DashboardData): DashboardData => ({
  ...data,
  summary: {
    income: asNumber(data.summary.income),
    expense: asNumber(data.summary.expense),
    net: asNumber(data.summary.net),
    available_balance: asNumber(data.summary.available_balance),
  },
  spending_by_category: data.spending_by_category.map((item) => ({
    ...item,
    amount: asNumber(item.amount),
    percentage: asNumber(item.percentage),
  })),
  trend: data.trend.map((item) => ({
    ...item,
    income: asNumber(item.income),
    expense: asNumber(item.expense),
  })),
  budgets: data.budgets.map((item) => ({
    ...item,
    limit_amount: asNumber(item.limit_amount),
    spent: asNumber(item.spent),
    remaining: asNumber(item.remaining),
    usage_percentage: asNumber(item.usage_percentage),
  })),
  goals: data.goals.map((item) => ({
    ...item,
    target_amount: asNumber(item.target_amount),
    current_amount: asNumber(item.current_amount),
    progress_percentage: asNumber(item.progress_percentage),
  })),
  recent_transactions: data.recent_transactions.map((item) => ({
    ...item,
    amount: asNumber(item.amount),
  })),
});

const normalizeReport = (data: ReportData): ReportData => ({
  ...data,
  summary: {
    ...data.summary,
    current: {
      income: asNumber(data.summary.current.income),
      expense: asNumber(data.summary.current.expense),
      net: asNumber(data.summary.current.net),
    },
    previous: {
      income: asNumber(data.summary.previous.income),
      expense: asNumber(data.summary.previous.expense),
      net: asNumber(data.summary.previous.net),
    },
    income_difference: asNumber(data.summary.income_difference),
    expense_difference: asNumber(data.summary.expense_difference),
    net_difference: asNumber(data.summary.net_difference),
    income_change_percentage: data.summary.income_change_percentage == null ? null : asNumber(data.summary.income_change_percentage),
    expense_change_percentage: data.summary.expense_change_percentage == null ? null : asNumber(data.summary.expense_change_percentage),
    net_change_percentage: data.summary.net_change_percentage == null ? null : asNumber(data.summary.net_change_percentage),
  },
  categories: data.categories.map((category) => ({
    ...category,
    current_amount: asNumber(category.current_amount),
    current_share: asNumber(category.current_share),
    current_transaction_count: asNumber(category.current_transaction_count),
    previous_amount: asNumber(category.previous_amount),
    previous_share: asNumber(category.previous_share),
    previous_transaction_count: asNumber(category.previous_transaction_count),
    difference: asNumber(category.difference),
    change_percentage: category.change_percentage == null ? null : asNumber(category.change_percentage),
  })),
});

const normalizeAssistantEvidence = (evidence: AssistantEvidence): AssistantEvidence => ({
  ...evidence,
  current: {
    ...evidence.current,
    income: asNumber(evidence.current.income),
    expense: asNumber(evidence.current.expense),
    net: asNumber(evidence.current.net),
  },
  previous: {
    ...evidence.previous,
    income: asNumber(evidence.previous.income),
    expense: asNumber(evidence.previous.expense),
    net: asNumber(evidence.previous.net),
  },
  available_balance: asNumber(evidence.available_balance),
  expense_difference: asNumber(evidence.expense_difference),
  expense_change_percentage: evidence.expense_change_percentage == null
    ? null
    : asNumber(evidence.expense_change_percentage),
  categories: evidence.categories.map((category) => ({
    ...category,
    current_amount: asNumber(category.current_amount),
    previous_amount: asNumber(category.previous_amount),
    difference: asNumber(category.difference),
    current_share: asNumber(category.current_share),
  })),
  forecast: {
    ...evidence.forecast,
    average_expense_per_day: asNumber(evidence.forecast.average_expense_per_day),
    projected_expense: asNumber(evidence.forecast.projected_expense),
    projected_net: asNumber(evidence.forecast.projected_net),
  },
  goal_target_total: asNumber(evidence.goal_target_total),
  goal_saved_total: asNumber(evidence.goal_saved_total),
});

const normalizeAssistantConversation = (conversation: AssistantConversation): AssistantConversation => ({
  ...conversation,
  messages: conversation.messages.map((message) => ({
    ...message,
    evidence: message.evidence ? normalizeAssistantEvidence(message.evidence) : null,
  })),
});

export const api = {
  login: (identifier: string, password: string) => {
    const body = new URLSearchParams({ username: identifier, password });
    return request<AuthToken>("/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body,
    });
  },
  register: (payload: RegisterPayload) =>
    request<User>("/auth/register", { method: "POST", body: JSON.stringify(payload) }),
  getMe: (signal?: AbortSignal) => request<User>("/auth/me", { signal }),
  updateProfile: (payload: UserProfilePayload) =>
    request<User>("/auth/me", { method: "PUT", body: JSON.stringify(payload) }),
  changePassword: (payload: ChangePasswordPayload) =>
    request<MessageResponse>("/auth/me/password", { method: "PUT", body: JSON.stringify(payload) }),
  deleteAccount: (payload: DeleteAccountPayload) =>
    request<MessageResponse>("/auth/me", { method: "DELETE", body: JSON.stringify(payload) }),
  uploadAvatar: (file: File) => {
    const body = new FormData();
    body.append("file", file);
    return request<User>("/auth/me/avatar", { method: "POST", body });
  },
  deleteAvatar: () => request<User>("/auth/me/avatar", { method: "DELETE" }),
  forgotPassword: (email: string) =>
    request<MessageResponse>("/auth/forgot-password", { method: "POST", body: JSON.stringify({ email }) }),
  resetPassword: (token: string, newPassword: string) =>
    request<MessageResponse>("/auth/reset-password", { method: "POST", body: JSON.stringify({ token, new_password: newPassword }) }),
  getDashboard: (month: number, year: number, signal?: AbortSignal) =>
    request<DashboardData>(`/dashboard/?month=${month}&year=${year}`, { signal }).then(normalizeDashboard),
  getReport: (month: number, year: number, signal?: AbortSignal) =>
    request<ReportData>(`/reports/?month=${month}&year=${year}`, { signal }).then(normalizeReport),
  getAssistantContext: (month: number, year: number, signal?: AbortSignal) =>
    request<AssistantContext>(`/assistant/context?month=${month}&year=${year}`, { signal })
      .then((context) => ({ ...context, evidence: normalizeAssistantEvidence(context.evidence) })),
  listAssistantConversations: (signal?: AbortSignal) =>
    request<AssistantConversationSummary[]>("/assistant/conversations", { signal }),
  getAssistantConversation: (id: string, signal?: AbortSignal) =>
    request<AssistantConversation>(`/assistant/conversations/${id}`, { signal })
      .then(normalizeAssistantConversation),
  askAssistant: (payload: AssistantAskPayload) =>
    request<AssistantReply>("/assistant/messages", { method: "POST", body: JSON.stringify(payload) })
      .then((reply) => ({ ...reply, conversation: normalizeAssistantConversation(reply.conversation) })),
  deleteAssistantConversation: (id: string) =>
    request<void>(`/assistant/conversations/${id}`, { method: "DELETE" }),
  listCategories: (signal?: AbortSignal) => request<Category[]>("/categories/", { signal }),
  createCategory: (payload: CategoryPayload) =>
    request<Category>("/categories/", { method: "POST", body: JSON.stringify(payload) }),
  updateCategory: (id: string, payload: Partial<CategoryPayload>) =>
    request<Category>(`/categories/${id}`, { method: "PUT", body: JSON.stringify(payload) }),
  deleteCategory: (id: string) => request<{ message: string }>(`/categories/${id}`, { method: "DELETE" }),
  listTransactions: (filters: TransactionFilters = {}, signal?: AbortSignal) => {
    const query = new URLSearchParams();
    Object.entries(filters).forEach(([key, value]) => {
      if (value) query.set(key, value);
    });
    const suffix = query.size ? `?${query.toString()}` : "";
    return request<Transaction[]>(`/transactions/${suffix}`, { signal })
      .then((items) => items.map(normalizeTransaction));
  },
  createTransaction: (payload: TransactionPayload) =>
    request<Transaction>("/transactions/", { method: "POST", body: JSON.stringify(payload) }).then(normalizeTransaction),
  updateTransaction: (id: string, payload: Partial<TransactionPayload>) =>
    request<Transaction>(`/transactions/${id}`, { method: "PUT", body: JSON.stringify(payload) }).then(normalizeTransaction),
  deleteTransaction: (id: string) => request<{ message: string }>(`/transactions/${id}`, { method: "DELETE" }),
  listBudgets: (month: number, year: number, signal?: AbortSignal) =>
    request<Budget[]>(`/budgets/?month=${month}&year=${year}`, { signal })
      .then((items) => items.map(normalizeBudget)),
  createBudget: (payload: BudgetPayload) =>
    request<Budget>("/budgets/", { method: "POST", body: JSON.stringify(payload) }).then(normalizeBudget),
  updateBudget: (id: string, limitAmount: number) =>
    request<Budget>(`/budgets/${id}`, { method: "PUT", body: JSON.stringify({ limit_amount: limitAmount }) }).then(normalizeBudget),
  deleteBudget: (id: string) => request<{ message: string }>(`/budgets/${id}`, { method: "DELETE" }),
  listGoals: (signal?: AbortSignal) => request<Goal[]>("/goals/", { signal }).then((items) => items.map(normalizeGoal)),
  createGoal: (payload: GoalPayload) =>
    request<Goal>("/goals/", { method: "POST", body: JSON.stringify(payload) }).then(normalizeGoal),
  updateGoal: (id: string, payload: Partial<GoalPayload>) =>
    request<Goal>(`/goals/${id}`, { method: "PATCH", body: JSON.stringify(payload) }).then(normalizeGoal),
  deleteGoal: (id: string) => request<{ message: string }>(`/goals/${id}`, { method: "DELETE" }),
  listGoalTransactions: (id: string, signal?: AbortSignal) =>
    request<GoalTransaction[]>(`/goals/${id}/transactions`, { signal }).then((items) => items.map(normalizeGoalTransaction)),
  depositGoal: (id: string, amount: number, note: string | null) =>
    request<Goal>(`/goals/${id}/deposit`, { method: "POST", body: JSON.stringify({ amount, note }) }).then(normalizeGoal),
  withdrawGoal: (id: string, amount: number, note: string | null) =>
    request<Goal>(`/goals/${id}/withdraw`, { method: "POST", body: JSON.stringify({ amount, note }) }).then(normalizeGoal),
  completeGoal: (id: string, payload: GoalCompletePayload) =>
    request<Goal>(`/goals/${id}/complete`, { method: "POST", body: JSON.stringify(payload) }).then(normalizeGoal),
  addGoalItem: (goalId: string, name: string, cost: number) =>
    request<Goal>(`/goals/${goalId}/items`, { method: "POST", body: JSON.stringify({ name, cost }) }).then(normalizeGoal),
  updateGoalItem: (goalId: string, itemId: string, payload: Partial<Pick<GoalItem, "name" | "cost" | "is_purchased">>) =>
    request<Goal>(`/goals/${goalId}/items/${itemId}`, { method: "PATCH", body: JSON.stringify(payload) }).then(normalizeGoal),
  deleteGoalItem: (goalId: string, itemId: string) =>
    request<Goal>(`/goals/${goalId}/items/${itemId}`, { method: "DELETE" }).then(normalizeGoal),
};
