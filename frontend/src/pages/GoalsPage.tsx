import {
  AlertCircle,
  AlertTriangle,
  ArrowDownToLine,
  ArrowUpFromLine,
  CalendarDays,
  Check,
  CheckCircle2,
  ChevronDown,
  CircleDollarSign,
  Clock3,
  GraduationCap,
  Laptop,
  MoreHorizontal,
  Pencil,
  PiggyBank,
  Plane,
  Plus,
  RefreshCw,
  Search,
  ShieldAlert,
  Target,
  Trash2,
  WalletCards,
  type LucideIcon,
} from "lucide-react";
import { type CSSProperties, type FormEvent, useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { SidePanel } from "../components/SidePanel";
import { ThemeToggle } from "../components/ThemeToggle";
import { api } from "../lib/api";
import { formatCurrency } from "../lib/format";
import type {
  Category,
  Goal,
  GoalCompleteMode,
  GoalItem,
  GoalTransaction,
} from "../types";

type GoalTab = "active" | "completed";
type GoalPanel = "create" | "edit" | "detail" | "deposit" | "withdraw" | "complete" | null;
type GoalSort = "priority" | "deadline" | "progress";

const DAY_IN_MS = 86_400_000;

const parseAmount = (value: string) => Number(value.replace(/[^0-9]/g, ""));
const displayAmountOf = (goal: Goal) => goal.status === "completed"
  ? goal.completion_amount ?? goal.target_amount
  : goal.current_amount;
const progressOf = (goal: Goal) => goal.status === "completed"
  ? 100
  : goal.target_amount > 0 ? (goal.current_amount / goal.target_amount) * 100 : 0;
const remainingOf = (goal: Goal) => goal.status === "completed"
  ? 0
  : Math.max(0, goal.target_amount - goal.current_amount);
const completionModeCopy: Record<GoalCompleteMode, string> = {
  keep: "Tiếp tục dành riêng",
  release: "Đã chuyển về số dư",
  spend: "Đã ghi nhận chi tiêu",
};

const parseDate = (value: string) => new Date(`${value}T00:00:00`);
const daysUntil = (value: string) => Math.ceil((parseDate(value).getTime() - new Date().setHours(0, 0, 0, 0)) / DAY_IN_MS);
const formatDate = (value: string) => new Intl.DateTimeFormat("vi-VN").format(parseDate(value));

const isAttentionGoal = (goal: Goal) => {
  if (goal.status !== "active" || progressOf(goal) >= 100 || !goal.deadline) return false;
  return daysUntil(goal.deadline) <= 30;
};

const monthlyRequired = (goal: Goal) => {
  if (!goal.deadline || remainingOf(goal) <= 0) return null;
  const days = daysUntil(goal.deadline);
  if (days < 0) return null;
  return remainingOf(goal) / Math.max(1, Math.ceil(days / 30));
};

const goalIcon = (goal: Goal, index = 0): LucideIcon => {
  const name = goal.name.toLocaleLowerCase("vi");
  if (/du lịch|nghỉ|nhật|vé/.test(name)) return Plane;
  if (/laptop|máy tính|điện thoại|thiết bị/.test(name)) return Laptop;
  if (/học|chứng chỉ|giáo dục|khóa/.test(name)) return GraduationCap;
  if (/khẩn cấp|dự phòng|an toàn/.test(name)) return ShieldAlert;
  return [Target, PiggyBank, WalletCards, CircleDollarSign][index % 4];
};

export function GoalsPage() {
  const [goals, setGoals] = useState<Goal[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState("");
  const [reloadKey, setReloadKey] = useState(0);
  const [tab, setTab] = useState<GoalTab>("active");
  const [sort, setSort] = useState<GoalSort>("priority");
  const [search, setSearch] = useState("");
  const [panel, setPanel] = useState<GoalPanel>(null);
  const [selectedGoalId, setSelectedGoalId] = useState<string | null>(null);
  const [menuGoalId, setMenuGoalId] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);
  const [formError, setFormError] = useState("");
  const [goalName, setGoalName] = useState("");
  const [goalAmount, setGoalAmount] = useState("");
  const [goalDeadline, setGoalDeadline] = useState("");
  const [moneyAmount, setMoneyAmount] = useState("");
  const [moneyNote, setMoneyNote] = useState("");
  const [completeMode, setCompleteMode] = useState<GoalCompleteMode>("keep");
  const [completeCategoryId, setCompleteCategoryId] = useState("");
  const [completeNote, setCompleteNote] = useState("");
  const [itemName, setItemName] = useState("");
  const [itemCost, setItemCost] = useState("");
  const [itemSaving, setItemSaving] = useState(false);
  const [history, setHistory] = useState<GoalTransaction[]>([]);
  const [historyLoading, setHistoryLoading] = useState(false);

  useEffect(() => {
    const controller = new AbortController();
    setLoading(true);
    setLoadError("");
    Promise.all([api.listGoals(controller.signal), api.listCategories(controller.signal)])
      .then(([goalData, categoryData]) => {
        setGoals(goalData);
        setCategories(categoryData);
      })
      .catch((cause: unknown) => {
        if (cause instanceof DOMException && cause.name === "AbortError") return;
        setLoadError(cause instanceof Error ? cause.message : "Không thể tải danh sách mục tiêu.");
      })
      .finally(() => {
        if (!controller.signal.aborted) setLoading(false);
      });
    return () => controller.abort();
  }, [reloadKey]);

  const selectedGoal = goals.find((goal) => goal.id === selectedGoalId) ?? null;
  const activeGoals = useMemo(() => goals.filter((goal) => goal.status === "active"), [goals]);
  const completedGoals = useMemo(() => goals.filter((goal) => goal.status === "completed"), [goals]);
  const expenseCategories = categories.filter((category) => category.type === "expense");

  const summary = useMemo(() => {
    const current = activeGoals.reduce((sum, goal) => sum + goal.current_amount, 0);
    const target = activeGoals.reduce((sum, goal) => sum + goal.target_amount, 0);
    return {
      current,
      target,
      progress: target > 0 ? Math.min(100, (current / target) * 100) : 0,
      attention: activeGoals.filter(isAttentionGoal).length,
    };
  }, [activeGoals]);

  const visibleGoals = useMemo(() => {
    const source = tab === "active" ? activeGoals : completedGoals;
    const query = search.trim().toLocaleLowerCase("vi");
    const result = query ? source.filter((goal) => goal.name.toLocaleLowerCase("vi").includes(query)) : [...source];
    return result.sort((a, b) => {
      if (sort === "progress") return progressOf(b) - progressOf(a) || a.name.localeCompare(b.name, "vi");
      if (sort === "deadline") {
        const aDate = a.deadline ? parseDate(a.deadline).getTime() : Number.MAX_SAFE_INTEGER;
        const bDate = b.deadline ? parseDate(b.deadline).getTime() : Number.MAX_SAFE_INTEGER;
        return aDate - bDate || a.name.localeCompare(b.name, "vi");
      }
      return Number(isAttentionGoal(b)) - Number(isAttentionGoal(a))
        || (a.deadline ? parseDate(a.deadline).getTime() : Number.MAX_SAFE_INTEGER) - (b.deadline ? parseDate(b.deadline).getTime() : Number.MAX_SAFE_INTEGER)
        || a.name.localeCompare(b.name, "vi");
    });
  }, [activeGoals, completedGoals, search, sort, tab]);

  const attentionGoals = visibleGoals.filter(isAttentionGoal);
  const steadyGoals = visibleGoals.filter((goal) => !isAttentionGoal(goal));
  const showSearch = (tab === "active" ? activeGoals.length : completedGoals.length) > 8 || Boolean(search);

  const replaceGoal = (updated: Goal) => {
    setGoals((items) => items.map((item) => item.id === updated.id ? updated : item));
  };

  const loadHistory = async (goalId: string) => {
    setHistoryLoading(true);
    try {
      setHistory(await api.listGoalTransactions(goalId));
    } catch {
      setHistory([]);
    } finally {
      setHistoryLoading(false);
    }
  };

  const closePanel = () => {
    setPanel(null);
    setFormError("");
    setMenuGoalId(null);
  };

  const openCreate = () => {
    setSelectedGoalId(null);
    setGoalName("");
    setGoalAmount("");
    setGoalDeadline("");
    setFormError("");
    setPanel("create");
  };

  const openEdit = (goal: Goal) => {
    setSelectedGoalId(goal.id);
    setGoalName(goal.name);
    setGoalAmount(String(goal.target_amount));
    setGoalDeadline(goal.deadline ?? "");
    setFormError("");
    setMenuGoalId(null);
    setPanel("edit");
  };

  const openDetail = (goal: Goal) => {
    setSelectedGoalId(goal.id);
    setFormError("");
    setMenuGoalId(null);
    setPanel("detail");
    void loadHistory(goal.id);
  };

  const openMoney = (goal: Goal, mode: "deposit" | "withdraw") => {
    setSelectedGoalId(goal.id);
    setMoneyAmount("");
    setMoneyNote("");
    setFormError("");
    setMenuGoalId(null);
    setPanel(mode);
  };

  const openComplete = (goal: Goal) => {
    setSelectedGoalId(goal.id);
    setCompleteMode("keep");
    setCompleteCategoryId(expenseCategories[0]?.id ?? "");
    setCompleteNote("");
    setFormError("");
    setPanel("complete");
  };

  const submitGoal = async (event: FormEvent) => {
    event.preventDefault();
    const amount = parseAmount(goalAmount);
    if (!goalName.trim()) return setFormError("Hãy nhập tên mục tiêu.");
    if (!Number.isFinite(amount) || amount <= 0) return setFormError("Số tiền mục tiêu phải lớn hơn 0 ₫.");
    setSaving(true);
    setFormError("");
    try {
      const payload = { name: goalName.trim(), target_amount: amount, deadline: goalDeadline || null };
      if (panel === "edit" && selectedGoal) {
        replaceGoal(await api.updateGoal(selectedGoal.id, payload));
      } else {
        const created = await api.createGoal(payload);
        setGoals((items) => [...items, created]);
        setTab("active");
      }
      closePanel();
    } catch (cause) {
      setFormError(cause instanceof Error ? cause.message : "Không thể lưu mục tiêu.");
    } finally {
      setSaving(false);
    }
  };

  const submitMoney = async (event: FormEvent) => {
    event.preventDefault();
    if (!selectedGoal || (panel !== "deposit" && panel !== "withdraw")) return;
    const amount = parseAmount(moneyAmount);
    if (!Number.isFinite(amount) || amount <= 0) return setFormError("Số tiền phải lớn hơn 0 ₫.");
    setSaving(true);
    setFormError("");
    try {
      const updated = panel === "deposit"
        ? await api.depositGoal(selectedGoal.id, amount, moneyNote.trim() || null)
        : await api.withdrawGoal(selectedGoal.id, amount, moneyNote.trim() || null);
      replaceGoal(updated);
      await loadHistory(selectedGoal.id);
      setPanel("detail");
    } catch (cause) {
      setFormError(cause instanceof Error ? cause.message : "Không thể cập nhật số tiền mục tiêu.");
    } finally {
      setSaving(false);
    }
  };

  const submitComplete = async (event: FormEvent) => {
    event.preventDefault();
    if (!selectedGoal) return;
    if (completeMode === "spend" && !completeCategoryId) return setFormError("Hãy chọn danh mục cho khoản chi.");
    setSaving(true);
    setFormError("");
    try {
      const updated = await api.completeGoal(selectedGoal.id, {
        mode: completeMode,
        category_id: completeMode === "spend" ? completeCategoryId : undefined,
        note: completeNote.trim() || null,
      });
      replaceGoal(updated);
      setTab("completed");
      closePanel();
    } catch (cause) {
      setFormError(cause instanceof Error ? cause.message : "Không thể hoàn thành mục tiêu.");
    } finally {
      setSaving(false);
    }
  };

  const removeGoal = async () => {
    if (!selectedGoal || !window.confirm(`Xóa mục tiêu chưa có giao dịch “${selectedGoal.name}”?`)) return;
    setSaving(true);
    setFormError("");
    try {
      await api.deleteGoal(selectedGoal.id);
      setGoals((items) => items.filter((item) => item.id !== selectedGoal.id));
      closePanel();
    } catch (cause) {
      setFormError(cause instanceof Error ? cause.message : "Không thể xóa mục tiêu.");
    } finally {
      setSaving(false);
    }
  };

  const addItem = async (event: FormEvent) => {
    event.preventDefault();
    if (!selectedGoal) return;
    const cost = parseAmount(itemCost);
    if (!itemName.trim()) return setFormError("Hãy nhập tên hạng mục.");
    if (!Number.isFinite(cost) || cost <= 0) return setFormError("Chi phí hạng mục phải lớn hơn 0 ₫.");
    setItemSaving(true);
    setFormError("");
    try {
      replaceGoal(await api.addGoalItem(selectedGoal.id, itemName.trim(), cost));
      setItemName("");
      setItemCost("");
    } catch (cause) {
      setFormError(cause instanceof Error ? cause.message : "Không thể thêm hạng mục.");
    } finally {
      setItemSaving(false);
    }
  };

  const toggleItem = async (item: GoalItem) => {
    if (!selectedGoal) return;
    setItemSaving(true);
    setFormError("");
    try {
      replaceGoal(await api.updateGoalItem(selectedGoal.id, item.id, { is_purchased: !item.is_purchased }));
    } catch (cause) {
      setFormError(cause instanceof Error ? cause.message : "Không thể cập nhật hạng mục.");
    } finally {
      setItemSaving(false);
    }
  };

  const removeItem = async (item: GoalItem) => {
    if (!selectedGoal || !window.confirm(`Xóa hạng mục “${item.name}”?`)) return;
    setItemSaving(true);
    setFormError("");
    try {
      replaceGoal(await api.deleteGoalItem(selectedGoal.id, item.id));
    } catch (cause) {
      setFormError(cause instanceof Error ? cause.message : "Không thể xóa hạng mục.");
    } finally {
      setItemSaving(false);
    }
  };

  const panelTitle = panel === "create" ? "Thêm mục tiêu"
    : panel === "edit" ? "Chỉnh sửa mục tiêu"
      : panel === "deposit" ? "Nạp tiền vào mục tiêu"
        : panel === "withdraw" ? "Rút tiền khỏi mục tiêu"
          : panel === "complete" ? "Hoàn thành mục tiêu"
            : selectedGoal?.name ?? "Chi tiết mục tiêu";

  const panelDescription = panel === "create" ? "Đặt một đích đến rõ ràng cho kế hoạch tiết kiệm của bạn."
    : panel === "edit" ? "Điều chỉnh số tiền hoặc thời hạn mà không làm mất lịch sử."
      : panel === "deposit" ? `Số tiền sẽ được dành riêng cho “${selectedGoal?.name ?? "mục tiêu"}”.`
        : panel === "withdraw" ? "Tiền rút sẽ trở lại số dư khả dụng của bạn."
          : panel === "complete" ? "Chọn rõ cách xử lý khoản tiền đã dành trước khi kết thúc."
            : "Xem tiến độ, kế hoạch chi tiết và lịch sử đóng góp.";

  const panelFooter = panel === "create" || panel === "edit" ? (
    <><button className="button button--secondary" type="button" onClick={closePanel}>Hủy</button><button className="button button--primary" type="submit" form="goal-form" disabled={saving}>{saving ? "Đang lưu…" : panel === "edit" ? "Lưu thay đổi" : "Tạo mục tiêu"}</button></>
  ) : panel === "deposit" || panel === "withdraw" ? (
    <><button className="button button--secondary" type="button" onClick={() => selectedGoal && openDetail(selectedGoal)}>Quay lại</button><button className="button button--primary" type="submit" form="goal-money-form" disabled={saving}>{saving ? "Đang cập nhật…" : panel === "deposit" ? "Nạp tiền" : "Rút tiền"}</button></>
  ) : panel === "complete" ? (
    <><button className="button button--secondary" type="button" onClick={() => selectedGoal && openDetail(selectedGoal)}>Quay lại</button><button className="button button--primary" type="submit" form="goal-complete-form" disabled={saving}>{saving ? "Đang hoàn thành…" : "Xác nhận hoàn thành"}</button></>
  ) : panel === "detail" && selectedGoal ? (
    <div className="goal-detail-footer"><button className="button button--danger-text" type="button" onClick={removeGoal} disabled={saving || historyLoading || history.length > 0} title={history.length > 0 ? "Không thể xóa mục tiêu đã có lịch sử tiền" : "Xóa mục tiêu chưa có giao dịch"}><Trash2 size={17} /> Xóa</button><div className="goal-detail-footer__actions"><button className="button button--secondary" type="button" onClick={() => openEdit(selectedGoal)}><Pencil size={16} /> Sửa</button>{selectedGoal.current_amount > 0 && <button className="button button--secondary" type="button" onClick={() => openMoney(selectedGoal, "withdraw")}><ArrowUpFromLine size={16} /> Rút</button>}{selectedGoal.status === "active" && <button className="button button--primary" type="button" onClick={() => openMoney(selectedGoal, "deposit")}><ArrowDownToLine size={17} /> Nạp tiền</button>}</div></div>
  ) : null;

  return (
    <div className="page goals-page">
      <header className="page-header">
        <div><h1>Mục tiêu</h1><p>Theo dõi tiến độ và biến kế hoạch thành hiện thực.</p></div>
        <div className="header-actions"><ThemeToggle /><button className="button button--primary" type="button" onClick={openCreate} disabled={loading || Boolean(loadError)}><Plus size={19} /> Thêm mục tiêu</button></div>
      </header>

      {loadError ? (
        <section className="surface data-load-state" role="alert"><span><AlertCircle size={25} /></span><h2>Chưa tải được mục tiêu</h2><p>{loadError}</p><button className="button button--primary" type="button" onClick={() => setReloadKey((value) => value + 1)}><RefreshCw size={17} /> Thử lại</button></section>
      ) : loading ? (
        <GoalsSkeleton />
      ) : (
        <>
          <GoalSummary current={summary.current} progress={summary.progress} activeCount={activeGoals.length} attentionCount={summary.attention} />

          <section className="goals-control-bar" aria-label="Lọc mục tiêu">
            <div className="goals-tabs" role="tablist" aria-label="Trạng thái mục tiêu">
              <button type="button" role="tab" aria-selected={tab === "active"} className={tab === "active" ? "is-active" : ""} onClick={() => setTab("active")}>Đang thực hiện <span>{activeGoals.length}</span></button>
              <button type="button" role="tab" aria-selected={tab === "completed"} className={tab === "completed" ? "is-active" : ""} onClick={() => setTab("completed")}>Đã hoàn thành <span>{completedGoals.length}</span></button>
            </div>
            <div className="goals-control-actions">
              {showSearch && <label className="goals-search"><Search size={16} /><input value={search} onChange={(event) => setSearch(event.target.value)} placeholder="Tìm mục tiêu" aria-label="Tìm mục tiêu" /></label>}
              <select className="compact-select" value={sort} onChange={(event) => setSort(event.target.value as GoalSort)} aria-label="Sắp xếp mục tiêu"><option value="priority">Ưu tiên</option><option value="deadline">Gần đến hạn</option><option value="progress">Tiến độ cao nhất</option></select>
            </div>
          </section>

          {visibleGoals.length === 0 ? (
            <GoalsEmpty tab={tab} hasSearch={Boolean(search)} onCreate={openCreate} onClearSearch={() => setSearch("")} />
          ) : tab === "active" ? (
            <div className="goals-sections">
              {attentionGoals.length > 0 && <GoalSection title="Cần chú ý" icon={AlertTriangle} tone="attention" goals={attentionGoals} menuGoalId={menuGoalId} setMenuGoalId={setMenuGoalId} onOpen={openDetail} onDeposit={(goal) => openMoney(goal, "deposit")} onEdit={openEdit} onWithdraw={(goal) => openMoney(goal, "withdraw")} />}
              {steadyGoals.length > 0 && <GoalSection title="Đang đúng tiến độ" icon={CheckCircle2} goals={steadyGoals} menuGoalId={menuGoalId} setMenuGoalId={setMenuGoalId} onOpen={openDetail} onDeposit={(goal) => openMoney(goal, "deposit")} onEdit={openEdit} onWithdraw={(goal) => openMoney(goal, "withdraw")} />}
            </div>
          ) : (
            <div className="goals-sections"><GoalSection title="Đã hoàn thành" icon={CheckCircle2} goals={visibleGoals} menuGoalId={menuGoalId} setMenuGoalId={setMenuGoalId} onOpen={openDetail} onDeposit={(goal) => openMoney(goal, "deposit")} onEdit={openEdit} onWithdraw={(goal) => openMoney(goal, "withdraw")} /></div>
          )}
        </>
      )}

      <SidePanel open={Boolean(panel)} onClose={closePanel} title={panelTitle} description={panelDescription} footer={panelFooter}>
        {(panel === "create" || panel === "edit") && <GoalForm name={goalName} amount={goalAmount} deadline={goalDeadline} setName={setGoalName} setAmount={setGoalAmount} setDeadline={setGoalDeadline} error={formError} onSubmit={submitGoal} />}
        {(panel === "deposit" || panel === "withdraw") && selectedGoal && <MoneyForm goal={selectedGoal} mode={panel} amount={moneyAmount} note={moneyNote} setAmount={setMoneyAmount} setNote={setMoneyNote} error={formError} onSubmit={submitMoney} />}
        {panel === "complete" && selectedGoal && <CompleteForm goal={selectedGoal} mode={completeMode} setMode={setCompleteMode} categoryId={completeCategoryId} setCategoryId={setCompleteCategoryId} note={completeNote} setNote={setCompleteNote} categories={expenseCategories} error={formError} onSubmit={submitComplete} />}
        {panel === "detail" && selectedGoal && <GoalDetail goal={selectedGoal} history={history} historyLoading={historyLoading} itemName={itemName} itemCost={itemCost} itemSaving={itemSaving} formError={formError} setItemName={setItemName} setItemCost={setItemCost} onAddItem={addItem} onToggleItem={toggleItem} onRemoveItem={removeItem} onComplete={() => openComplete(selectedGoal)} />}
      </SidePanel>
    </div>
  );
}

function GoalSummary({ current, progress, activeCount, attentionCount }: { current: number; progress: number; activeCount: number; attentionCount: number }) {
  return (
    <section className="goal-summary" aria-label="Tổng quan mục tiêu">
      <div className="goal-summary__primary"><div><span>Đang dành cho mục tiêu</span><strong>{formatCurrency(current)}</strong><small>{activeCount > 0 ? "Tổng số tiền đã tiết kiệm" : "Chưa có mục tiêu đang thực hiện"}</small></div><span className="goal-summary__ring" style={{ "--goal-progress": `${progress * 3.6}deg` } as CSSProperties}><b>{Math.round(progress)}%</b></span></div>
      <div className="goal-summary__stat"><span className="goal-summary__icon"><Target size={25} /></span><div><strong>{activeCount}</strong><span>mục tiêu<br />đang thực hiện</span></div></div>
      <div className={`goal-summary__stat${attentionCount > 0 ? " is-attention" : ""}`}><span className="goal-summary__icon"><ShieldAlert size={25} /></span><div><strong>{attentionCount}</strong><span>mục tiêu<br />cần chú ý</span></div></div>
    </section>
  );
}

function GoalSection({ title, icon: Icon, tone, goals, menuGoalId, setMenuGoalId, onOpen, onDeposit, onEdit, onWithdraw }: { title: string; icon: LucideIcon; tone?: "attention"; goals: Goal[]; menuGoalId: string | null; setMenuGoalId: (id: string | null) => void; onOpen: (goal: Goal) => void; onDeposit: (goal: Goal) => void; onEdit: (goal: Goal) => void; onWithdraw: (goal: Goal) => void }) {
  return (
    <section className={`goal-section${tone ? ` goal-section--${tone}` : ""}`}>
      <h2><Icon size={22} /> {title}</h2>
      <div className={tone ? "goal-attention-list" : "goal-card-grid"}>
        {goals.map((goal, index) => <GoalCard key={goal.id} goal={goal} index={index} attention={tone === "attention"} menuOpen={menuGoalId === goal.id} onToggleMenu={() => setMenuGoalId(menuGoalId === goal.id ? null : goal.id)} onOpen={() => onOpen(goal)} onDeposit={() => onDeposit(goal)} onEdit={() => onEdit(goal)} onWithdraw={() => onWithdraw(goal)} />)}
      </div>
    </section>
  );
}

function GoalCard({ goal, index, attention, menuOpen, onToggleMenu, onOpen, onDeposit, onEdit, onWithdraw }: { goal: Goal; index: number; attention?: boolean; menuOpen: boolean; onToggleMenu: () => void; onOpen: () => void; onDeposit: () => void; onEdit: () => void; onWithdraw: () => void }) {
  const Icon = goalIcon(goal, index);
  const progress = Math.min(100, progressOf(goal));
  const displayAmount = displayAmountOf(goal);
  const monthly = monthlyRequired(goal);
  const deadlineDays = goal.deadline ? daysUntil(goal.deadline) : null;
  const deadlineCopy = !goal.deadline ? "Không có thời hạn" : deadlineDays !== null && deadlineDays < 0 ? `Quá hạn ${Math.abs(deadlineDays)} ngày` : formatDate(goal.deadline);
  return (
    <article className={`goal-card${attention ? " goal-card--attention" : ""}${goal.status === "completed" ? " goal-card--completed" : ""}`}>
      <span className="goal-card__icon"><Icon size={attention ? 34 : 28} /></span>
      <div className="goal-card__main">
        <button className="goal-card__title" type="button" onClick={onOpen}>{goal.name}</button>
        <div className="goal-card__amount"><strong>{formatCurrency(displayAmount)}</strong><span>/ {formatCurrency(goal.target_amount)}</span></div>
        <div className="goal-card__progress"><span style={{ "--goal-scale": Math.min(1, progress / 100) } as CSSProperties} /></div>
        <div className="goal-card__meta"><span>{goal.status === "completed" ? `Đã đạt ${formatCurrency(displayAmount)}` : `Còn thiếu ${formatCurrency(remainingOf(goal))}`}</span><b>{Math.round(progress)}%</b></div>
      </div>
      <div className="goal-card__deadline"><CalendarDays size={17} /><span><small>Hạn hoàn thành</small><strong>{goal.status === "completed" ? "Đã hoàn thành" : deadlineCopy}</strong></span></div>
      {attention && <div className="goal-card__monthly"><Clock3 size={17} /><span><small>Cần thêm</small><strong>{monthly ? `${formatCurrency(monthly)}/tháng` : "Điều chỉnh thời hạn"}</strong></span></div>}
      <div className="goal-card__actions">{goal.status === "active" && <button className="button button--primary button--small" type="button" onClick={onDeposit}>Nạp tiền</button>}<div className="row-menu-wrap"><button className="icon-button" type="button" onClick={onToggleMenu} aria-label={`Mở hành động cho ${goal.name}`} aria-expanded={menuOpen}><MoreHorizontal size={20} /></button>{menuOpen && <div className="row-menu"><button type="button" onClick={onOpen}><Target size={16} /> Xem chi tiết</button><button type="button" onClick={onEdit}><Pencil size={16} /> Chỉnh sửa</button>{goal.current_amount > 0 && <button type="button" onClick={onWithdraw}><ArrowUpFromLine size={16} /> Rút tiền</button>}</div>}</div></div>
    </article>
  );
}

function GoalsEmpty({ tab, hasSearch, onCreate, onClearSearch }: { tab: GoalTab; hasSearch: boolean; onCreate: () => void; onClearSearch: () => void }) {
  return (
    <section className="surface goals-empty"><span><Target size={28} /></span><h2>{hasSearch ? "Không tìm thấy mục tiêu" : tab === "active" ? "Bắt đầu với mục tiêu đầu tiên" : "Chưa có mục tiêu hoàn thành"}</h2><p>{hasSearch ? "Thử một tên khác hoặc xóa nội dung tìm kiếm." : tab === "active" ? "Đặt số tiền và thời hạn để biến kế hoạch lớn thành những bước nhỏ có thể theo dõi." : "Các mục tiêu bạn hoàn thành sẽ được lưu tại đây."}</p>{hasSearch ? <button className="button button--secondary" type="button" onClick={onClearSearch}>Xóa tìm kiếm</button> : tab === "active" && <button className="button button--primary" type="button" onClick={onCreate}><Plus size={18} /> Thêm mục tiêu</button>}</section>
  );
}

function GoalForm({ name, amount, deadline, setName, setAmount, setDeadline, error, onSubmit }: { name: string; amount: string; deadline: string; setName: (value: string) => void; setAmount: (value: string) => void; setDeadline: (value: string) => void; error: string; onSubmit: (event: FormEvent) => void }) {
  return <form id="goal-form" className="form-stack" onSubmit={onSubmit}><label className="field"><span>Tên mục tiêu</span><input data-panel-initial-focus value={name} onChange={(event) => setName(event.target.value)} placeholder="Ví dụ: Quỹ khẩn cấp" maxLength={100} /></label><label className="field"><span>Số tiền cần đạt</span><div className="currency-input"><input inputMode="numeric" value={amount} onChange={(event) => setAmount(event.target.value)} placeholder="0" /><span>₫</span></div></label><label className="field"><span>Thời hạn <small>Không bắt buộc · DD/MM/YYYY</small></span><input type="date" lang="vi" aria-label="Thời hạn, định dạng ngày tháng năm" value={deadline} onChange={(event) => setDeadline(event.target.value)} /></label>{error && <div className="form-error" role="alert">{error}</div>}</form>;
}

function MoneyForm({ goal, mode, amount, note, setAmount, setNote, error, onSubmit }: { goal: Goal; mode: "deposit" | "withdraw"; amount: string; note: string; setAmount: (value: string) => void; setNote: (value: string) => void; error: string; onSubmit: (event: FormEvent) => void }) {
  return <form id="goal-money-form" className="form-stack" onSubmit={onSubmit}><div className="goal-money-context"><span className={mode === "deposit" ? "is-positive" : "is-neutral"}>{mode === "deposit" ? <ArrowDownToLine size={21} /> : <ArrowUpFromLine size={21} />}</span><div><small>{mode === "deposit" ? "Đã tiết kiệm" : "Có thể rút tối đa"}</small><strong>{formatCurrency(goal.current_amount)}</strong></div></div><label className="field"><span>{mode === "deposit" ? "Số tiền muốn nạp" : "Số tiền muốn rút"}</span><div className="currency-input"><input data-panel-initial-focus inputMode="numeric" value={amount} onChange={(event) => setAmount(event.target.value)} placeholder="0" /><span>₫</span></div></label><label className="field"><span>Ghi chú <small>Không bắt buộc</small></span><textarea value={note} onChange={(event) => setNote(event.target.value)} placeholder={mode === "deposit" ? "Nguồn tiền hoặc lý do đóng góp" : "Lý do rút tiền"} rows={3} /></label>{error && <div className="form-error" role="alert">{error}</div>}</form>;
}

function CompleteForm({ goal, mode, setMode, categoryId, setCategoryId, note, setNote, categories, error, onSubmit }: { goal: Goal; mode: GoalCompleteMode; setMode: (value: GoalCompleteMode) => void; categoryId: string; setCategoryId: (value: string) => void; note: string; setNote: (value: string) => void; categories: Category[]; error: string; onSubmit: (event: FormEvent) => void }) {
  return <form id="goal-complete-form" className="form-stack" onSubmit={onSubmit}><div className="goal-complete-banner"><CheckCircle2 size={25} /><div><strong>Bạn đã đạt {Math.round(progressOf(goal))}% mục tiêu</strong><p>Khoản tiền hiện tại: {formatCurrency(goal.current_amount)}</p></div></div><fieldset className="goal-complete-options"><legend>Xử lý khoản tiền đã dành</legend><label className={mode === "keep" ? "is-selected" : ""}><input type="radio" name="complete-mode" checked={mode === "keep"} onChange={() => setMode("keep")} /><span><strong>Đánh dấu hoàn thành</strong><small>Giữ nguyên tiền trong mục tiêu để xử lý sau.</small></span></label><label className={mode === "spend" ? "is-selected" : ""}><input type="radio" name="complete-mode" checked={mode === "spend"} onChange={() => setMode("spend")} /><span><strong>Ghi nhận đã sử dụng</strong><small>Tạo một giao dịch chi và kết thúc mục tiêu.</small></span></label><label className={mode === "release" ? "is-selected" : ""}><input type="radio" name="complete-mode" checked={mode === "release"} onChange={() => setMode("release")} /><span><strong>Chuyển về số dư</strong><small>Giải phóng toàn bộ tiền về số dư khả dụng.</small></span></label></fieldset>{mode === "spend" && <label className="field"><span>Danh mục chi tiêu</span>{categories.length > 0 ? <select value={categoryId} onChange={(event) => setCategoryId(event.target.value)}><option value="">Chọn danh mục</option>{categories.map((category) => <option key={category.id} value={category.id}>{category.name}</option>)}</select> : <p className="field-hint">Bạn chưa có danh mục chi tiêu. <Link to="/categories">Tạo danh mục</Link> trước khi ghi nhận.</p>}</label>}<label className="field"><span>Ghi chú <small>Không bắt buộc</small></span><textarea value={note} onChange={(event) => setNote(event.target.value)} rows={3} placeholder="Ghi lại kết quả hoặc mục đích sử dụng" /></label>{error && <div className="form-error" role="alert">{error}</div>}</form>;
}

function GoalDetail({ goal, history, historyLoading, itemName, itemCost, itemSaving, formError, setItemName, setItemCost, onAddItem, onToggleItem, onRemoveItem, onComplete }: { goal: Goal; history: GoalTransaction[]; historyLoading: boolean; itemName: string; itemCost: string; itemSaving: boolean; formError: string; setItemName: (value: string) => void; setItemCost: (value: string) => void; onAddItem: (event: FormEvent) => void; onToggleItem: (item: GoalItem) => void; onRemoveItem: (item: GoalItem) => void; onComplete: () => void }) {
  const Icon = goalIcon(goal);
  const progress = Math.min(100, progressOf(goal));
  const displayAmount = displayAmountOf(goal);
  const planTotal = goal.items.reduce((sum, item) => sum + item.cost, 0);
  return <div className="goal-detail"><section className="goal-detail__hero"><span><Icon size={30} /></span><div><div><strong>{formatCurrency(displayAmount)}</strong><small>/ {formatCurrency(goal.target_amount)}</small></div><div className="goal-card__progress"><span style={{ "--goal-scale": Math.min(1, progress / 100) } as CSSProperties} /></div><p><span>{goal.status === "completed" ? `Đã đạt ${formatCurrency(displayAmount)}` : `Còn thiếu ${formatCurrency(remainingOf(goal))}`}</span><b>{Math.round(progress)}%</b></p></div></section><dl className="goal-detail__facts"><div><dt>Trạng thái</dt><dd>{goal.status === "completed" ? "Đã hoàn thành" : isAttentionGoal(goal) ? "Cần chú ý" : "Đang thực hiện"}</dd></div>{goal.status === "completed" && goal.completion_mode && <div><dt>Xử lý khoản tiền</dt><dd>{completionModeCopy[goal.completion_mode]}</dd></div>}<div><dt>Thời hạn</dt><dd>{goal.deadline ? formatDate(goal.deadline) : "Không có thời hạn"}</dd></div>{monthlyRequired(goal) && <div><dt>Cần thêm mỗi tháng</dt><dd>{formatCurrency(monthlyRequired(goal)!)}</dd></div>}</dl>{goal.status === "active" && progress >= 100 && <button className="goal-ready-action" type="button" onClick={onComplete}><CheckCircle2 size={22} /><span><strong>Mục tiêu đã sẵn sàng hoàn thành</strong><small>Chọn cách xử lý khoản tiền đã dành.</small></span><ChevronDown size={18} /></button>}<details className="goal-plan" open={goal.items.length > 0}><summary><span><Target size={18} /><strong>Kế hoạch chi tiết</strong><small>{goal.items.length > 0 ? `${goal.items.filter((item) => item.is_purchased).length}/${goal.items.length} hạng mục · ${formatCurrency(planTotal)}` : "Chỉ thêm khi bạn cần chia nhỏ kế hoạch"}</small></span><ChevronDown size={18} /></summary><div className="goal-plan__body">{goal.items.map((item) => <div className={`goal-plan-item${item.is_purchased ? " is-complete" : ""}`} key={item.id}><button type="button" onClick={() => onToggleItem(item)} disabled={itemSaving} aria-label={item.is_purchased ? `Đánh dấu ${item.name} chưa hoàn tất` : `Đánh dấu ${item.name} hoàn tất`}>{item.is_purchased && <Check size={14} />}</button><div><strong>{item.name}</strong><small>{formatCurrency(item.cost)}</small></div><button className="icon-button" type="button" onClick={() => onRemoveItem(item)} disabled={itemSaving} aria-label={`Xóa ${item.name}`}><Trash2 size={16} /></button></div>)}<form className="goal-item-form" onSubmit={onAddItem}><input value={itemName} onChange={(event) => setItemName(event.target.value)} placeholder="Tên hạng mục" aria-label="Tên hạng mục" /><div className="currency-input"><input inputMode="numeric" value={itemCost} onChange={(event) => setItemCost(event.target.value)} placeholder="Chi phí" aria-label="Chi phí hạng mục" /><span>₫</span></div><button className="button button--outline button--small" type="submit" disabled={itemSaving}><Plus size={15} /> Thêm</button></form></div></details><section className="goal-history"><h3>Lịch sử đóng góp</h3>{historyLoading ? <div className="goal-history__loading">Đang tải lịch sử…</div> : history.length === 0 ? <p>Chưa có lần nạp hoặc rút tiền nào.</p> : history.map((transaction) => <div className="goal-history__row" key={transaction.id}><span className={transaction.type === "deposit" ? "is-deposit" : "is-withdraw"}>{transaction.type === "deposit" ? <ArrowDownToLine size={17} /> : <ArrowUpFromLine size={17} />}</span><div><strong>{transaction.note || (transaction.type === "deposit" ? "Nạp tiền" : "Rút tiền")}</strong><small>{formatDate(transaction.txn_date)}</small></div><b className={transaction.type === "deposit" ? "amount--positive" : ""}>{transaction.type === "deposit" ? "+" : "−"}{formatCurrency(transaction.amount)}</b></div>)}</section>{formError && <div className="form-error" role="alert">{formError}</div>}</div>;
}

function GoalsSkeleton() {
  return <div className="goals-loading" aria-live="polite" aria-busy="true"><span className="sr-only">Đang tải mục tiêu</span><div className="goal-summary skeleton-block" /><div className="goals-control-bar skeleton-block" /><div className="goal-card-grid"><div className="surface skeleton-block" /><div className="surface skeleton-block" /><div className="surface skeleton-block" /></div></div>;
}
