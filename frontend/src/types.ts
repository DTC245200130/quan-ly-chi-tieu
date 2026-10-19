export type CategoryType = "income" | "expense";
export type CategoryIconKey =
  | "circle-dollar-sign"
  | "wallet"
  | "utensils"
  | "shopping-bag"
  | "house"
  | "car"
  | "bus"
  | "fuel"
  | "smartphone"
  | "receipt"
  | "heart-pulse"
  | "graduation-cap"
  | "gamepad-2"
  | "dog"
  | "baby"
  | "dumbbell"
  | "plane"
  | "gift"
  | "piggy-bank"
  | "banknote"
  | "briefcase-business"
  | "trending-up"
  | "hand-coins"
  | "badge-dollar-sign";

export interface User {
  id: string;
  username: string;
  email: string;
  display_name: string | null;
  avatar_url: string | null;
}

export interface UserProfilePayload {
  display_name: string | null;
  username: string;
  email: string;
}

export interface ChangePasswordPayload {
  current_password: string;
  new_password: string;
}

export interface DeleteAccountPayload {
  current_password: string;
  confirmation: string;
}

export interface AuthToken {
  access_token: string;
  token_type: string;
}

export interface RegisterPayload {
  username: string;
  email: string;
  password: string;
}

export interface MessageResponse {
  message: string;
}

export interface Category {
  id: string;
  name: string;
  type: CategoryType;
  color: string;
  icon: CategoryIconKey;
}

export interface Budget {
  id: string;
  category_id: string;
  month: number;
  year: number;
  limit_amount: number;
  spent: number;
  is_over: boolean;
}

export interface CategoryPayload {
  name: string;
  type: CategoryType;
  color: string;
  icon: CategoryIconKey;
}

export interface BudgetPayload {
  category_id: string;
  month: number;
  year: number;
  limit_amount: number;
}

export type GoalStatus = "active" | "completed";
export type GoalCompleteMode = "keep" | "release" | "spend";

export interface GoalItem {
  id: string;
  name: string;
  cost: number;
  is_purchased: boolean;
}

export interface Goal {
  id: string;
  name: string;
  target_amount: number;
  deadline: string | null;
  status: GoalStatus;
  current_amount: number;
  completion_amount: number | null;
  completion_mode: GoalCompleteMode | null;
  items: GoalItem[];
}

export interface GoalPayload {
  name: string;
  target_amount: number;
  deadline: string | null;
}

export interface GoalTransaction {
  id: string;
  amount: number;
  type: "deposit" | "withdraw";
  txn_date: string;
  note: string | null;
}

export interface GoalCompletePayload {
  mode: GoalCompleteMode;
  category_id?: string;
  note?: string | null;
}

export interface Transaction {
  id: string;
  category_id: string;
  amount: number;
  type: CategoryType;
  txn_date: string;
  note: string | null;
}

export interface TransactionPayload {
  category_id: string;
  amount: number;
  txn_date: string;
  note: string | null;
}

export interface TransactionFilters {
  category_id?: string;
  type?: CategoryType;
  from_date?: string;
  to_date?: string;
  keyword?: string;
}

export interface DashboardSummary {
  income: number;
  expense: number;
  net: number;
  available_balance: number;
}

export interface DashboardCategorySpending {
  category_id: string;
  category_name: string;
  color: string;
  icon: CategoryIconKey;
  amount: number;
  percentage: number;
}

export interface DashboardTrendPoint {
  month: number;
  year: number;
  income: number;
  expense: number;
}

export interface DashboardBudget {
  id: string;
  category_id: string;
  category_name: string;
  color: string;
  icon: CategoryIconKey;
  limit_amount: number;
  spent: number;
  remaining: number;
  usage_percentage: number;
  is_over: boolean;
  status: "safe" | "warning" | "over";
}

export interface DashboardGoal {
  id: string;
  name: string;
  target_amount: number;
  current_amount: number;
  progress_percentage: number;
  deadline: string | null;
  status: string;
}

export interface DashboardRecentTransaction {
  id: string;
  category_id: string;
  category_name: string;
  category_color: string;
  category_icon: CategoryIconKey;
  amount: number;
  type: CategoryType;
  txn_date: string;
  note: string | null;
}

export interface DashboardData {
  month: number;
  year: number;
  summary: DashboardSummary;
  spending_by_category: DashboardCategorySpending[];
  trend: DashboardTrendPoint[];
  budgets: DashboardBudget[];
  goals: DashboardGoal[];
  recent_transactions: DashboardRecentTransaction[];
}

export interface ReportPeriod {
  month: number;
  year: number;
}

export interface ReportPeriodTotals {
  income: number;
  expense: number;
  net: number;
}

export interface ReportSummary {
  current: ReportPeriodTotals;
  previous: ReportPeriodTotals;
  income_difference: number;
  expense_difference: number;
  net_difference: number;
  income_change_percentage: number | null;
  expense_change_percentage: number | null;
  net_change_percentage: number | null;
}

export interface ReportCategoryComparison {
  category_id: string;
  category_name: string;
  icon: CategoryIconKey;
  current_amount: number;
  current_share: number;
  current_transaction_count: number;
  previous_amount: number;
  previous_share: number;
  previous_transaction_count: number;
  difference: number;
  change_percentage: number | null;
}

export interface ReportData {
  current_period: ReportPeriod;
  previous_period: ReportPeriod;
  summary: ReportSummary;
  categories: ReportCategoryComparison[];
  has_data: boolean;
}

export interface AssistantPeriod {
  month: number;
  year: number;
}

export interface AssistantTotals {
  income: number;
  expense: number;
  net: number;
  transaction_count: number;
}

export interface AssistantCategoryEvidence {
  label: string;
  icon: string;
  current_amount: number;
  previous_amount: number;
  difference: number;
  current_share: number;
  current_transaction_count: number;
}

export interface AssistantForecast {
  elapsed_days: number;
  days_in_month: number;
  average_expense_per_day: number;
  projected_expense: number;
  projected_net: number;
  confidence: "low" | "medium";
}

export interface AssistantEvidence {
  current_period: AssistantPeriod;
  previous_period: AssistantPeriod;
  current: AssistantTotals;
  previous: AssistantTotals;
  available_balance: number;
  expense_difference: number;
  expense_change_percentage: number | null;
  categories: AssistantCategoryEvidence[];
  forecast: AssistantForecast;
  active_budget_count: number;
  over_budget_count: number;
  active_goal_count: number;
  goal_target_total: number;
  goal_saved_total: number;
}

export interface AssistantContext {
  evidence: AssistantEvidence;
  has_data: boolean;
  privacy_notes: string[];
  model: string;
}

export interface AssistantMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  context_month: number | null;
  context_year: number | null;
  evidence: AssistantEvidence | null;
  created_at: string;
}

export interface AssistantConversationSummary {
  id: string;
  title: string;
  preview: string;
  message_count: number;
  created_at: string;
  updated_at: string;
}

export interface AssistantConversation extends AssistantConversationSummary {
  messages: AssistantMessage[];
}

export interface AssistantAskPayload {
  question: string;
  conversation_id?: string;
  month: number;
  year: number;
}

export interface AssistantReply {
  conversation: AssistantConversation;
  model: string;
}
