import {
  AlertCircle,
  AlertTriangle,
  CalendarDays,
  CircleGauge,
  Info,
  MoreHorizontal,
  Plus,
  RefreshCw,
  Trash2,
  WalletCards,
} from "lucide-react";
import { FormEvent, useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { CategoryAvatar } from "../components/CategoryAvatar";
import { SidePanel } from "../components/SidePanel";
import { ThemeToggle } from "../components/ThemeToggle";
import { api } from "../lib/api";
import { formatCurrency } from "../lib/format";
import type { Budget, Category } from "../types";

type BudgetRow = { category: Category; budget?: Budget; percent: number; tone: "safe" | "warning" | "over" | "unset" };

const now = new Date();
const currentPeriod = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, "0")}`;
const monthOptions = Array.from({ length: 30 }, (_, index) => {
  const date = new Date(now.getFullYear(), now.getMonth() + 6 - index, 1);
  const optionMonth = date.getMonth() + 1;
  const optionYear = date.getFullYear();
  return {
    value: `${optionYear}-${String(optionMonth).padStart(2, "0")}`,
    label: `Tháng ${optionMonth}, ${optionYear}`,
  };
});

export function BudgetsPage() {
  const [monthValue, setMonthValue] = useState(currentPeriod);
  const [categories, setCategories] = useState<Category[]>([]);
  const [budgets, setBudgets] = useState<Budget[]>([]);
  const [panelOpen, setPanelOpen] = useState(false);
  const [editingBudget, setEditingBudget] = useState<Budget | null>(null);
  const [categoryId, setCategoryId] = useState("");
  const [limitInput, setLimitInput] = useState("");
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [loadError, setLoadError] = useState("");
  const [actionError, setActionError] = useState("");
  const [formError, setFormError] = useState("");
  const [reloadKey, setReloadKey] = useState(0);
  const [year, month] = monthValue.split("-").map(Number);

  useEffect(() => {
    const controller = new AbortController();
    setLoading(true);
    setLoadError("");
    setActionError("");
    Promise.all([
      api.listCategories(controller.signal),
      api.listBudgets(month, year, controller.signal),
    ])
      .then(([categoryData, budgetData]) => {
        setCategories(categoryData);
        setBudgets(budgetData);
      })
      .catch((cause: unknown) => {
        if (cause instanceof DOMException && cause.name === "AbortError") return;
        setLoadError(cause instanceof Error ? cause.message : "Không thể tải ngân sách.");
      })
      .finally(() => {
        if (!controller.signal.aborted) setLoading(false);
      });
    return () => controller.abort();
  }, [month, reloadKey, year]);

  const expenseCategories = categories.filter((category) => category.type === "expense");
  const rows: BudgetRow[] = expenseCategories.map((category) => {
    const budget = budgets.find((item) => item.category_id === category.id);
    const limit = budget ? Number(budget.limit_amount) : 0;
    const percent = budget && limit > 0 ? Math.round((Number(budget.spent) / limit) * 100) : 0;
    return { category, budget, percent, tone: !budget ? "unset" : percent > 100 ? "over" : percent >= 80 ? "warning" : "safe" };
  });

  const summary = useMemo(() => {
    const total = budgets.reduce((sum, budget) => sum + Number(budget.limit_amount), 0);
    const spent = budgets.reduce((sum, budget) => sum + Number(budget.spent), 0);
    return { total, spent, remaining: total - spent, percent: total ? Math.round((spent / total) * 100) : 0 };
  }, [budgets]);

  const warnings = rows.filter((row) => row.tone === "warning" || row.tone === "over");
  const unbudgeted = rows.filter((row) => row.tone === "unset");
  const availableCategories = expenseCategories.filter((category) => !budgets.some((budget) => budget.category_id === category.id));
  const selectedCategory = categories.find((category) => category.id === categoryId);
  const daysRemaining = useMemo(() => {
    const today = new Date();
    if (today.getFullYear() === year && today.getMonth() + 1 === month) {
      return Math.max(1, new Date(year, month, 0).getDate() - today.getDate());
    }
    return new Date(year, month, 0).getDate();
  }, [month, year]);

  const openCreate = (presetCategory?: Category) => {
    setEditingBudget(null);
    setCategoryId(presetCategory?.id ?? unbudgeted[0]?.category.id ?? "");
    setLimitInput("");
    setFormError("");
    setActionError("");
    setPanelOpen(true);
  };

  const openEdit = (budget: Budget) => {
    setEditingBudget(budget);
    setCategoryId(budget.category_id);
    setLimitInput(String(Number(budget.limit_amount)));
    setFormError("");
    setActionError("");
    setPanelOpen(true);
  };

  const submit = async (event: FormEvent) => {
    event.preventDefault();
    const limit = Number(limitInput.replace(/[^0-9]/g, ""));
    if (!categoryId) return setFormError("Hãy chọn một danh mục chi tiêu.");
    if (!Number.isFinite(limit) || limit <= 0) return setFormError("Hạn mức phải lớn hơn 0 ₫.");
    setSaving(true);
    setFormError("");
    try {
      if (editingBudget) {
        const updated = await api.updateBudget(editingBudget.id, limit);
        setBudgets((items) => items.map((item) => item.id === editingBudget.id ? updated : item));
      } else {
        const created = await api.createBudget({ category_id: categoryId, month, year, limit_amount: limit });
        setBudgets((items) => [...items, created]);
      }
      setPanelOpen(false);
    } catch (cause) {
      setFormError(cause instanceof Error ? cause.message : "Không thể lưu ngân sách.");
    } finally {
      setSaving(false);
    }
  };

  const remove = async () => {
    if (!editingBudget || !window.confirm("Xóa hạn mức ngân sách này?")) return;
    setSaving(true);
    setFormError("");
    try {
      await api.deleteBudget(editingBudget.id);
      setBudgets((items) => items.filter((item) => item.id !== editingBudget.id));
      setPanelOpen(false);
    } catch (cause) {
      setFormError(cause instanceof Error ? cause.message : "Không thể xóa ngân sách.");
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="page budgets-page">
      <header className="page-header">
        <div><h1>Ngân sách</h1><p>Lập kế hoạch chi tiêu và giữ vững mục tiêu mỗi tháng</p></div>
        <div className="header-actions">
          <label className="month-input"><CalendarDays size={18} /><select value={monthValue} onChange={(event) => setMonthValue(event.target.value)} aria-label="Chọn tháng ngân sách">{monthOptions.map((option) => <option key={option.value} value={option.value}>{option.label}</option>)}</select></label>
          <ThemeToggle />
          <button className="button button--primary" type="button" onClick={() => openCreate()} disabled={loading || Boolean(loadError) || availableCategories.length === 0}><Plus size={19} /> Đặt ngân sách</button>
        </div>
      </header>

      {actionError && <div className="inline-alert" role="alert">{actionError}</div>}

      {loadError ? (
        <DataLoadError title="Chưa tải được ngân sách" description={loadError} onRetry={() => setReloadKey((value) => value + 1)} />
      ) : loading ? (
        <div className="budget-layout" aria-label="Đang tải ngân sách" aria-busy="true"><div className="surface skeleton-block" /><div className="surface skeleton-block" /></div>
      ) : (
        <>
          <section className="surface budget-summary" aria-label="Tổng quan ngân sách">
            <SummaryItem icon={WalletCards} label="Tổng ngân sách" value={summary.total} tone="positive" />
            <SummaryItem icon={CircleGauge} label="Đã chi" value={summary.spent} tone="negative" />
            <SummaryItem icon={WalletCards} label="Còn lại" value={summary.remaining} tone={summary.remaining < 0 ? "negative" : "positive"} />
            <div className="summary-progress"><span className="progress-ring" style={{ "--progress": `${Math.min(summary.percent, 100) * 3.6}deg` } as React.CSSProperties}><b>{summary.percent}%</b></span><div><small>Tiến độ</small><strong>{summary.percent}%</strong></div></div>
          </section>

          <div className="budget-layout">
            <section className="surface budget-list-surface">
              <div className="section-heading"><h2>Tiến độ theo danh mục</h2></div>
              {rows.length === 0 ? (
                <div className="empty-state budget-empty-state"><p>Chưa có danh mục chi tiêu để lập ngân sách.</p><Link className="text-button" to="/categories"><Plus size={17} /> Tạo danh mục chi tiêu</Link></div>
              ) : (
                <><div className="budget-table-head"><span>Danh mục</span><span>Đã chi / Hạn mức</span><span>Tiến độ</span><span /></div><div className="budget-rows">{rows.map((row) => <BudgetRowView key={row.category.id} row={row} onEdit={openEdit} onCreate={openCreate} />)}</div></>
              )}
            </section>

            <aside className="attention-column" aria-label="Cảnh báo ngân sách">
              <section className="surface attention-surface">
                <div className="section-heading"><h2>Cần chú ý</h2></div>
                {rows.length === 0 && <div className="empty-state"><p>Chưa có dữ liệu để đánh giá ngân sách.</p></div>}
                {rows.length > 0 && warnings.length === 0 && unbudgeted.length === 0 && <div className="empty-state"><p>Mọi ngân sách đều đang trong tầm kiểm soát.</p></div>}
                {warnings.map((row) => <div className={`attention-item attention-item--${row.tone}`} key={row.category.id}><span className="attention-icon"><AlertTriangle size={21} /></span><div><strong>{row.category.name} đã dùng {row.percent}%</strong><p>{row.tone === "over" ? "Khoản chi đã vượt hạn mức tháng này." : `Bạn đã dùng ${row.percent}% hạn mức của danh mục ${row.category.name}.`}</p></div><button className="button button--outline" type="button" onClick={() => row.budget && openEdit(row.budget)}>Điều chỉnh</button></div>)}
                {unbudgeted.length > 0 && <div className="attention-item attention-item--info"><span className="attention-icon"><Info size={21} /></span><div><strong>{unbudgeted.length} danh mục chưa có hạn mức</strong><p>{unbudgeted.slice(0, 3).map((row) => row.category.name).join(", ")}{unbudgeted.length > 3 ? "…" : ""}</p></div><button className="button button--outline" type="button" onClick={() => openCreate(unbudgeted[0].category)}>Đặt ngân sách</button></div>}
              </section>
              <section className="surface daily-allowance"><span className="metric-icon metric-icon--positive"><CalendarDays size={21} /></span><div>{budgets.length === 0 ? <><p>Chưa có hạn mức ngân sách cho tháng này.</p><small>Hãy đặt ngân sách để theo dõi mức chi mỗi ngày.</small></> : <><p>Bạn còn <strong>{formatCurrency(summary.remaining)}</strong> cho {daysRemaining} ngày</p><small>{formatCurrency(Math.max(0, summary.remaining) / daysRemaining)} / ngày</small></>}</div></section>
            </aside>
          </div>
        </>
      )}

      <SidePanel
        open={panelOpen}
        onClose={() => setPanelOpen(false)}
        title={editingBudget ? "Chỉnh sửa ngân sách" : "Đặt ngân sách"}
        footer={<>{editingBudget && <button className="button button--danger-text" type="button" onClick={remove} disabled={saving}><Trash2 size={17} /> Xóa</button>}<span className="panel-footer-spacer" /><button className="button button--secondary" type="button" onClick={() => setPanelOpen(false)}>Hủy</button><button className="button button--primary" type="submit" form="budget-form" disabled={saving}>{saving ? "Đang lưu…" : editingBudget ? "Lưu thay đổi" : "Đặt ngân sách"}</button></>}
      >
        <form id="budget-form" className="form-stack" onSubmit={submit}>
          <label className="field"><span>Danh mục</span><select data-panel-initial-focus={editingBudget ? undefined : ""} value={categoryId} onChange={(event) => setCategoryId(event.target.value)} disabled={Boolean(editingBudget)}><option value="">Chọn danh mục chi tiêu</option>{(editingBudget ? expenseCategories : availableCategories).map((category) => <option key={category.id} value={category.id}>{category.name}</option>)}</select></label>
          {selectedCategory && <div className="selected-category"><CategoryAvatar category={selectedCategory} /><div><strong>{selectedCategory.name}</strong><small>Ngân sách tháng {month}/{year}</small></div></div>}
          <label className="field"><span>Hạn mức ngân sách</span><div className="currency-input"><input data-panel-initial-focus={editingBudget ? "" : undefined} inputMode="numeric" value={limitInput} onChange={(event) => setLimitInput(event.target.value)} placeholder="0" /><span>₫</span></div></label>
          {editingBudget && <p className="field-hint">Đã chi {formatCurrency(Number(editingBudget.spent))} trong tháng này.</p>}
          {formError && <div className="form-error" role="alert">{formError}</div>}
        </form>
      </SidePanel>
    </div>
  );
}

function SummaryItem({ icon: Icon, label, value, tone }: { icon: typeof WalletCards; label: string; value: number; tone: "positive" | "negative" }) {
  return <div className="summary-item"><span className={`metric-icon metric-icon--${tone}`}><Icon size={23} /></span><div><small>{label}</small><strong className={`amount--${tone}`}>{formatCurrency(value)}</strong></div></div>;
}

function BudgetRowView({ row, onEdit, onCreate }: { row: BudgetRow; onEdit: (budget: Budget) => void; onCreate: (category: Category) => void }) {
  return (
    <div className={`budget-row budget-row--${row.tone}`}>
      <div className="budget-category"><CategoryAvatar category={row.category} /><strong>{row.category.name}</strong></div>
      <div className="budget-values">{row.budget ? <><span>{formatCurrency(Number(row.budget.spent))} / {formatCurrency(Number(row.budget.limit_amount))}</span><div className="progress-track"><span style={{ width: `${Math.min(row.percent, 100)}%` }} /></div></> : <span>Chưa đặt ngân sách</span>}</div>
      <strong className="budget-percent">{row.budget ? `${row.percent}%` : "—"}</strong>
      {row.budget ? <button className="icon-button" type="button" onClick={() => onEdit(row.budget!)} aria-label={`Chỉnh sửa ngân sách ${row.category.name}`}><MoreHorizontal size={20} /></button> : <button className="button button--outline button--small" type="button" onClick={() => onCreate(row.category)}><Plus size={16} /> Đặt hạn mức</button>}
    </div>
  );
}

function DataLoadError({ title, description, onRetry }: { title: string; description: string; onRetry: () => void }) {
  return (
    <section className="surface data-load-state" role="alert">
      <span><AlertCircle size={25} /></span>
      <h2>{title}</h2>
      <p>{description}</p>
      <button className="button button--primary" type="button" onClick={onRetry}><RefreshCw size={17} /> Thử lại</button>
    </section>
  );
}
