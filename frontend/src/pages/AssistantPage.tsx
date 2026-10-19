import {
  AlertCircle,
  AlertTriangle,
  BarChart3,
  Bot,
  CalendarDays,
  CheckCircle2,
  ChevronRight,
  Clock3,
  History,
  MessageCircleQuestion,
  PanelRight,
  Plus,
  RefreshCw,
  Search,
  Send,
  ShieldCheck,
  Target,
  Trash2,
  TrendingUp,
  WalletCards,
  X,
} from "lucide-react";
import type { FormEvent, KeyboardEvent, RefObject } from "react";
import { useEffect, useMemo, useRef, useState } from "react";
import { Link } from "react-router-dom";
import { ThemeToggle } from "../components/ThemeToggle";
import { api } from "../lib/api";
import { formatCurrency } from "../lib/format";
import type {
  AssistantContext,
  AssistantConversation,
  AssistantConversationSummary,
  AssistantEvidence,
} from "../types";

const today = new Date();
const currentPeriod = `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, "0")}`;
const monthOptions = Array.from({ length: 30 }, (_, index) => {
  const date = new Date(today.getFullYear(), today.getMonth() - index, 1);
  const month = date.getMonth() + 1;
  const year = date.getFullYear();
  return { value: `${year}-${String(month).padStart(2, "0")}`, label: `Tháng ${month}, ${year}` };
});

const starters = [
  {
    title: "Phân tích chi tiêu",
    prompt: "Tháng này tôi chi tiêu khác gì tháng trước?",
    detail: "So sánh tổng chi và nhóm chi tiêu thay đổi rõ nhất.",
    icon: BarChart3,
    tone: "coral",
  },
  {
    title: "Phát hiện bất thường",
    prompt: "Có khoản chi nào bất thường trong tháng này không?",
    detail: "Tìm biến động đáng chú ý từ dữ liệu đã tổng hợp.",
    icon: AlertTriangle,
    tone: "amber",
  },
  {
    title: "Dự báo dòng tiền",
    prompt: "Nếu tiếp tục chi như hiện tại, cuối tháng còn bao nhiêu?",
    detail: "Ước tính cuối tháng và nêu rõ độ tin cậy.",
    icon: TrendingUp,
    tone: "violet",
  },
  {
    title: "Lập kế hoạch tài chính",
    prompt: "Tôi nên lập kế hoạch tiết kiệm như thế nào?",
    detail: "Đề xuất bước đi dựa trên ngân sách và mục tiêu hiện có.",
    icon: Target,
    tone: "blue",
  },
] as const;

const followUpPrompts = [
  "Danh mục nào tăng nhiều nhất?",
  "Tôi nên điều chỉnh ngân sách nào?",
  "Giải thích kỹ hơn về dự báo cuối tháng.",
];

function historyGroup(value: string) {
  const updated = new Date(value);
  const startToday = new Date(today.getFullYear(), today.getMonth(), today.getDate());
  const difference = Math.floor((startToday.getTime() - updated.getTime()) / 86_400_000);
  if (difference <= 0) return "Hôm nay";
  if (difference <= 7) return "7 ngày qua";
  return "Cũ hơn";
}

function formatTime(value: string) {
  return new Intl.DateTimeFormat("vi-VN", { hour: "2-digit", minute: "2-digit" }).format(new Date(value));
}

export function AssistantPage() {
  const [period, setPeriod] = useState(currentPeriod);
  const [context, setContext] = useState<AssistantContext | null>(null);
  const [conversations, setConversations] = useState<AssistantConversationSummary[]>([]);
  const [activeConversation, setActiveConversation] = useState<AssistantConversation | null>(null);
  const [question, setQuestion] = useState("");
  const [search, setSearch] = useState("");
  const [contextLoading, setContextLoading] = useState(true);
  const [historyLoading, setHistoryLoading] = useState(true);
  const [conversationLoading, setConversationLoading] = useState(false);
  const [sending, setSending] = useState(false);
  const [error, setError] = useState("");
  const [reloadKey, setReloadKey] = useState(0);
  const [historyReloadKey, setHistoryReloadKey] = useState(0);
  const [failedQuestion, setFailedQuestion] = useState("");
  const [deleteId, setDeleteId] = useState<string | null>(null);
  const [historyOpen, setHistoryOpen] = useState(false);
  const [scopeOpen, setScopeOpen] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const messageEndRef = useRef<HTMLDivElement>(null);
  const historyButtonRef = useRef<HTMLButtonElement>(null);
  const scopeButtonRef = useRef<HTMLButtonElement>(null);
  const historyRailRef = useRef<HTMLElement>(null);
  const scopeRailRef = useRef<HTMLElement>(null);
  const [year, month] = period.split("-").map(Number);

  useEffect(() => {
    const controller = new AbortController();
    setContextLoading(true);
    setError("");
    api.getAssistantContext(month, year, controller.signal)
      .then(setContext)
      .catch((cause: unknown) => {
        if (cause instanceof DOMException && cause.name === "AbortError") return;
        setError(cause instanceof Error ? cause.message : "Không thể tải phạm vi dữ liệu.");
        setFailedQuestion("");
      })
      .finally(() => {
        if (!controller.signal.aborted) setContextLoading(false);
      });
    return () => controller.abort();
  }, [month, reloadKey, year]);

  useEffect(() => {
    const controller = new AbortController();
    setHistoryLoading(true);
    api.listAssistantConversations(controller.signal)
      .then(setConversations)
      .catch((cause: unknown) => {
        if (cause instanceof DOMException && cause.name === "AbortError") return;
        setError(cause instanceof Error ? cause.message : "Không thể tải lịch sử hội thoại.");
        setFailedQuestion("");
      })
      .finally(() => {
        if (!controller.signal.aborted) setHistoryLoading(false);
      });
    return () => controller.abort();
  }, [historyReloadKey]);

  useEffect(() => {
    const openRail = historyOpen ? historyRailRef.current : scopeOpen ? scopeRailRef.current : null;
    if (!openRail) return;
    const opener = historyOpen ? historyButtonRef.current : scopeButtonRef.current;
    const inertTargets = [
      document.querySelector<HTMLElement>(".sidebar"),
      document.querySelector<HTMLElement>(".assistant-header"),
      document.querySelector<HTMLElement>(".assistant-conversation"),
    ].filter((target): target is HTMLElement => Boolean(target));
    inertTargets.forEach((target) => target.setAttribute("inert", ""));
    const focusableSelector = "button:not(:disabled), a[href], input:not(:disabled), select:not(:disabled), textarea:not(:disabled), [tabindex]:not([tabindex='-1'])";
    const focusables = () => Array.from(openRail.querySelectorAll<HTMLElement>(focusableSelector));
    const focusTimer = window.setTimeout(() => focusables()[0]?.focus(), 0);
    const handleKeyDown = (event: globalThis.KeyboardEvent) => {
      if (event.key === "Escape") {
        event.preventDefault();
        closeDrawers();
        requestAnimationFrame(() => opener?.focus());
        return;
      }
      if (event.key !== "Tab") return;
      const items = focusables();
      if (!items.length) return;
      const first = items[0];
      const last = items[items.length - 1];
      if (event.shiftKey && document.activeElement === first) {
        event.preventDefault();
        last.focus();
      } else if (!event.shiftKey && document.activeElement === last) {
        event.preventDefault();
        first.focus();
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => {
      window.clearTimeout(focusTimer);
      inertTargets.forEach((target) => target.removeAttribute("inert"));
      window.removeEventListener("keydown", handleKeyDown);
    };
  }, [historyOpen, scopeOpen]);

  useEffect(() => {
    messageEndRef.current?.scrollIntoView({ block: "nearest" });
  }, [activeConversation?.messages.length, sending]);

  const groupedConversations = useMemo(() => {
    const groups = new Map<string, AssistantConversationSummary[]>();
    conversations
      .filter((item) => `${item.title} ${item.preview}`.toLocaleLowerCase("vi").includes(search.trim().toLocaleLowerCase("vi")))
      .forEach((item) => {
        const group = historyGroup(item.updated_at);
        groups.set(group, [...(groups.get(group) ?? []), item]);
      });
    return groups;
  }, [conversations, search]);

  const startConversation = () => {
    setActiveConversation(null);
    setQuestion("");
    setError("");
    setHistoryOpen(false);
    requestAnimationFrame(() => textareaRef.current?.focus());
  };

  const chooseStarter = (prompt: string) => {
    setQuestion(prompt);
    requestAnimationFrame(() => textareaRef.current?.focus());
  };

  const selectConversation = async (id: string) => {
    setConversationLoading(true);
    setError("");
    try {
      setActiveConversation(await api.getAssistantConversation(id));
      setHistoryOpen(false);
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Không thể mở cuộc trò chuyện.");
    } finally {
      setConversationLoading(false);
    }
  };

  const removeConversation = async (id: string) => {
    try {
      await api.deleteAssistantConversation(id);
      setConversations((items) => items.filter((item) => item.id !== id));
      if (activeConversation?.id === id) setActiveConversation(null);
      setDeleteId(null);
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Không thể xóa cuộc trò chuyện.");
    }
  };

  const sendQuestion = async (trimmed: string) => {
    if (!trimmed || sending) return;
    setSending(true);
    setError("");
    try {
      const reply = await api.askAssistant({
        question: trimmed,
        conversation_id: activeConversation?.id,
        month,
        year,
      });
      setActiveConversation(reply.conversation);
      setQuestion("");
      setFailedQuestion("");
      setConversations((items) => {
        const summary = { ...reply.conversation };
        const withoutCurrent = items.filter((item) => item.id !== summary.id);
        return [summary, ...withoutCurrent];
      });
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Trợ lý chưa thể trả lời lúc này.");
      setFailedQuestion(trimmed);
    } finally {
      setSending(false);
    }
  };

  const submitQuestion = async (event?: FormEvent) => {
    event?.preventDefault();
    await sendQuestion(question.trim());
  };

  const retryLastFailure = () => {
    if (failedQuestion) {
      void sendQuestion(failedQuestion);
      return;
    }
    setReloadKey((value) => value + 1);
    setHistoryReloadKey((value) => value + 1);
  };

  const handleComposerKeyDown = (event: KeyboardEvent<HTMLTextAreaElement>) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      void submitQuestion();
    }
  };

  const closeHistory = () => {
    setHistoryOpen(false);
    window.setTimeout(() => historyButtonRef.current?.focus(), 0);
  };

  const closeScope = () => {
    setScopeOpen(false);
    window.setTimeout(() => scopeButtonRef.current?.focus(), 0);
  };

  const closeDrawers = () => {
    const focusHistoryButton = historyOpen;
    setHistoryOpen(false);
    setScopeOpen(false);
    window.setTimeout(() => (focusHistoryButton ? historyButtonRef.current : scopeButtonRef.current)?.focus(), 0);
  };

  return (
    <div className="page assistant-page">
      <header className="page-header assistant-header">
        <div>
          <h1>Trợ lý AI</h1>
          <p>Hiểu dòng tiền, nhận tư vấn và tự quyết định bước tiếp theo.</p>
        </div>
        <div className="header-actions">
          <button ref={historyButtonRef} className="icon-button assistant-mobile-action" type="button" onClick={() => setHistoryOpen(true)} aria-label="Mở lịch sử hội thoại" aria-expanded={historyOpen} aria-controls="assistant-history-rail"><History size={19} /></button>
          <label className="month-input">
            <CalendarDays size={18} />
            <select value={period} onChange={(event) => setPeriod(event.target.value)} aria-label="Chọn kỳ dữ liệu" disabled={contextLoading}>
              {monthOptions.map((option) => <option key={option.value} value={option.value}>{option.label}</option>)}
            </select>
          </label>
          <button ref={scopeButtonRef} className="icon-button assistant-mobile-action" type="button" onClick={() => setScopeOpen(true)} aria-label="Mở phạm vi dữ liệu" aria-expanded={scopeOpen} aria-controls="assistant-scope-rail"><PanelRight size={19} /></button>
          <ThemeToggle />
        </div>
      </header>

      {error && (
        <div className="assistant-page-error" role="alert">
          <AlertCircle size={18} /><span>{error}</span>
          <button type="button" onClick={retryLastFailure}><RefreshCw size={15} /> Thử lại</button>
        </div>
      )}

      <div className="assistant-workspace">
        <HistoryRail
          railRef={historyRailRef}
          open={historyOpen}
          loading={historyLoading}
          search={search}
          groups={groupedConversations}
          activeId={activeConversation?.id ?? null}
          deleteId={deleteId}
          onSearch={setSearch}
          onNew={startConversation}
          onSelect={selectConversation}
          onAskDelete={setDeleteId}
          onDelete={removeConversation}
          onClose={closeHistory}
        />

        <section className="assistant-conversation surface" aria-label="Cuộc trò chuyện với trợ lý AI">
          <div className="assistant-conversation__topline">
            <span><Bot size={17} /> Gemini</span>
            <span className="assistant-advice-badge"><ShieldCheck size={15} /> Chỉ tư vấn</span>
          </div>
          <div className="assistant-messages" aria-live="polite" aria-busy={conversationLoading || sending}>
            {conversationLoading ? (
              <ConversationSkeleton />
            ) : activeConversation?.messages.length ? (
              activeConversation.messages.map((message) => (
                <article className={`assistant-message assistant-message--${message.role}`} key={message.id}>
                  {message.role === "assistant" && <span className="assistant-avatar"><Bot size={19} /></span>}
                  <div className="assistant-message__content">
                    <div className="assistant-message__meta">
                      <strong>{message.role === "assistant" ? "Trợ lý AI" : "Bạn"}</strong>
                      <time dateTime={message.created_at}>{formatTime(message.created_at)}</time>
                    </div>
                    <p>{message.content}</p>
                    {message.role === "assistant" && message.evidence && <EvidenceBlock evidence={message.evidence} onFollowUp={chooseStarter} />}
                  </div>
                </article>
              ))
            ) : (
              <AssistantWelcome hasData={context?.has_data ?? false} onChoose={chooseStarter} />
            )}
            {sending && (
              <div className="assistant-generating" role="status">
                <span className="assistant-avatar"><Bot size={19} /></span>
                <span><i /><i /><i /></span>
                <p>Gemini đang đối chiếu dữ liệu tổng hợp…</p>
              </div>
            )}
            <div ref={messageEndRef} />
          </div>
          <form className="assistant-composer" onSubmit={submitQuestion}>
            <label className="sr-only" htmlFor="assistant-question">Hỏi trợ lý AI về tài chính của bạn</label>
            <textarea
              id="assistant-question"
              ref={textareaRef}
              value={question}
              onChange={(event) => setQuestion(event.target.value)}
              onKeyDown={handleComposerKeyDown}
              placeholder="Hỏi về chi tiêu, dòng tiền hoặc kế hoạch của bạn…"
              rows={1}
              maxLength={2000}
              disabled={sending}
            />
            <button className="assistant-send" type="submit" disabled={!question.trim() || sending} aria-label="Gửi câu hỏi">
              <Send size={18} />
            </button>
            <small>Enter để gửi · Shift + Enter để xuống dòng</small>
          </form>
        </section>

        <ScopeRail railRef={scopeRailRef} open={scopeOpen} context={context} loading={contextLoading} onClose={closeScope} />
      </div>

      {(historyOpen || scopeOpen) && <button className="assistant-drawer-scrim" type="button" onClick={closeDrawers} aria-label="Đóng bảng phụ" />}
    </div>
  );
}

interface HistoryRailProps {
  railRef: RefObject<HTMLElement>;
  open: boolean;
  loading: boolean;
  search: string;
  groups: Map<string, AssistantConversationSummary[]>;
  activeId: string | null;
  deleteId: string | null;
  onSearch: (value: string) => void;
  onNew: () => void;
  onSelect: (id: string) => void;
  onAskDelete: (id: string | null) => void;
  onDelete: (id: string) => void;
  onClose: () => void;
}

function HistoryRail({ railRef, open, loading, search, groups, activeId, deleteId, onSearch, onNew, onSelect, onAskDelete, onDelete, onClose }: HistoryRailProps) {
  return (
    <aside ref={railRef} id="assistant-history-rail" className={`assistant-history surface${open ? " is-open" : ""}`} aria-label="Lịch sử hội thoại" role={open ? "dialog" : undefined} aria-modal={open ? "true" : undefined}>
      <div className="assistant-rail-title"><div><History size={18} /><strong>Lịch sử</strong></div><button className="icon-button assistant-rail-close" type="button" onClick={onClose} aria-label="Đóng lịch sử"><X size={18} /></button></div>
      <button className="button button--outline assistant-new-chat" type="button" onClick={onNew}><Plus size={17} /> Cuộc trò chuyện mới</button>
      <label className="assistant-history-search"><Search size={16} /><input value={search} onChange={(event) => onSearch(event.target.value)} placeholder="Tìm cuộc trò chuyện" aria-label="Tìm cuộc trò chuyện" /></label>
      <div className="assistant-history-list">
        {loading ? <HistorySkeleton /> : groups.size === 0 ? (
          <div className="assistant-history-empty"><MessageCircleQuestion size={24} /><strong>{search ? "Không tìm thấy" : "Chưa có lịch sử"}</strong><p>{search ? "Thử một từ khóa khác." : "Cuộc trò chuyện đầu tiên sẽ xuất hiện tại đây."}</p></div>
        ) : Array.from(groups.entries()).map(([group, items]) => (
          <section className="assistant-history-group" key={group}>
            <h2>{group}</h2>
            {items.map((item) => (
              <div className={`assistant-history-item${item.id === activeId ? " is-active" : ""}`} key={item.id}>
                <button type="button" onClick={() => onSelect(item.id)}>
                  <strong>{item.title}</strong><span>{item.preview}</span>
                </button>
                {deleteId === item.id ? (
                  <span className="assistant-history-confirm"><button type="button" onClick={() => onDelete(item.id)}>Xóa</button><button type="button" onClick={() => onAskDelete(null)}>Hủy</button></span>
                ) : (
                  <button className="assistant-history-delete" type="button" onClick={() => onAskDelete(item.id)} aria-label={`Xóa ${item.title}`}><Trash2 size={14} /></button>
                )}
              </div>
            ))}
          </section>
        ))}
      </div>
    </aside>
  );
}

function AssistantWelcome({ hasData, onChoose }: { hasData: boolean; onChoose: (prompt: string) => void }) {
  return (
    <div className="assistant-welcome">
      <span className="assistant-welcome__mark"><Bot size={28} /></span>
      <h2>Bạn muốn hiểu điều gì về dòng tiền?</h2>
      <p>{hasData ? "Chọn một hướng phân tích hoặc đặt câu hỏi theo cách của bạn." : "Kỳ này chưa có dữ liệu giao dịch. Bạn vẫn có thể hỏi cách bắt đầu lập kế hoạch tài chính."}</p>
      <div className="assistant-starters">
        {starters.map(({ title, prompt, detail, icon: Icon, tone }) => (
          <button className={`assistant-starter assistant-starter--${tone}`} type="button" key={title} onClick={() => onChoose(prompt)}>
            <span><Icon size={19} /></span>
            <div><strong>{title}</strong><small>{detail}</small></div>
            <ChevronRight size={17} />
          </button>
        ))}
      </div>
      <div className="assistant-follow-up-chips" aria-label="Gợi ý câu hỏi khác">
        {followUpPrompts.map((prompt) => <button type="button" key={prompt} onClick={() => onChoose(prompt)}>{prompt}</button>)}
      </div>
    </div>
  );
}

function EvidenceBlock({ evidence, onFollowUp }: { evidence: AssistantEvidence; onFollowUp: (prompt: string) => void }) {
  const period = `${evidence.current_period.year}-${String(evidence.current_period.month).padStart(2, "0")}`;
  const change = evidence.expense_change_percentage;
  return (
    <details className="assistant-evidence" open>
      <summary><span><BarChart3 size={17} /> Dữ liệu dùng cho câu trả lời</span><small>Tháng {evidence.current_period.month}/{evidence.current_period.year}</small></summary>
      <div className="assistant-evidence__body">
        <div className="assistant-evidence__totals">
          <div><small>Chi kỳ này</small><strong className="amount--negative">{formatCurrency(evidence.current.expense)}</strong></div>
          <div><small>Chi kỳ trước</small><strong>{formatCurrency(evidence.previous.expense)}</strong></div>
          <div><small>Chênh lệch</small><strong className={evidence.expense_difference > 0 ? "amount--negative" : "amount--positive"}>{evidence.expense_difference > 0 ? "+" : ""}{formatCurrency(evidence.expense_difference)}</strong></div>
        </div>
        {evidence.categories.length > 0 && (
          <div className="assistant-evidence__table-wrap">
            <table className="assistant-evidence__table">
              <caption>So sánh nhóm chi tiêu của kỳ được phân tích</caption>
              <thead><tr><th>Nhóm chi</th><th>Kỳ này</th><th>Kỳ trước</th><th>Chênh lệch</th></tr></thead>
              <tbody>{evidence.categories.slice(0, 4).map((category) => (
                <tr key={category.icon}>
                  <th scope="row"><span>{category.label}</span><small>{category.current_transaction_count} giao dịch</small></th>
                  <td>{formatCurrency(category.current_amount)}</td>
                  <td>{formatCurrency(category.previous_amount)}</td>
                  <td className={category.difference > 0 ? "amount--negative" : category.difference < 0 ? "amount--positive" : ""}>{category.difference > 0 ? "+" : ""}{formatCurrency(category.difference)}</td>
                </tr>
              ))}</tbody>
            </table>
          </div>
        )}
        <div className="assistant-evidence__confidence">
          <AlertCircle size={15} />
          <span><strong>Độ tin cậy {evidence.forecast.confidence === "medium" ? "trung bình" : "thấp"}</strong><small>Dự báo giả định nhịp chi trung bình trong {evidence.forecast.elapsed_days} ngày đã qua tiếp tục đến hết tháng.</small></span>
        </div>
        <div className="assistant-evidence__links">
          <Link to="/reports">Mở báo cáo <ChevronRight size={15} /></Link>
          <Link to={`/transactions?period=${period}`}>Xem giao dịch <ChevronRight size={15} /></Link>
        </div>
        <div className="assistant-evidence__follow-ups">
          <strong>Hỏi tiếp</strong>
          {followUpPrompts.slice(0, 2).map((prompt) => <button type="button" key={prompt} onClick={() => onFollowUp(prompt)}>{prompt}<ChevronRight size={14} /></button>)}
        </div>
      </div>
    </details>
  );
}

function ScopeRail({ railRef, open, context, loading, onClose }: { railRef: RefObject<HTMLElement>; open: boolean; context: AssistantContext | null; loading: boolean; onClose: () => void }) {
  return (
    <aside ref={railRef} id="assistant-scope-rail" className={`assistant-scope${open ? " is-open" : ""}`} aria-label="Phạm vi dữ liệu AI" role={open ? "dialog" : undefined} aria-modal={open ? "true" : undefined}>
      <section className="surface assistant-scope-card">
        <div className="assistant-rail-title"><div><ShieldCheck size={18} /><strong>Dữ liệu được sử dụng</strong></div><button className="icon-button assistant-rail-close" type="button" onClick={onClose} aria-label="Đóng phạm vi dữ liệu"><X size={18} /></button></div>
        {loading ? <ScopeSkeleton /> : context ? (
          <>
            <p>Chỉ các con số tổng hợp của tháng {context.evidence.current_period.month}/{context.evidence.current_period.year} được gửi để phân tích.</p>
            <ul className="assistant-scope-list">
              <li><WalletCards size={16} /><span><strong>Thu, chi và số dư</strong><small>Tổng tiền theo kỳ</small></span><CheckCircle2 size={16} /></li>
              <li><BarChart3 size={16} /><span><strong>Nhóm chi tiêu</strong><small>Số tiền và tỷ trọng</small></span><CheckCircle2 size={16} /></li>
              <li><Target size={16} /><span><strong>Ngân sách, mục tiêu</strong><small>Chỉ tổng số và tiến độ</small></span><CheckCircle2 size={16} /></li>
            </ul>
            <div className="assistant-data-freshness"><Clock3 size={16} /><span><strong>{context.evidence.current.transaction_count} giao dịch trong kỳ</strong><small>Dữ liệu được lấy lại khi đổi tháng</small></span></div>
          </>
        ) : null}
      </section>
      <section className="surface assistant-privacy-card">
        <div className="assistant-privacy-card__title"><ShieldCheck size={18} /><strong>Quyền riêng tư</strong></div>
        <ul>
          {(context?.privacy_notes ?? ["Không gửi tên hoặc email", "Không gửi ghi chú giao dịch", "AI không thể sửa dữ liệu"]).map((note) => <li key={note}><CheckCircle2 size={15} />{note}</li>)}
        </ul>
        <p><Bot size={15} /> Gemini phân tích theo từng câu hỏi. Hội thoại được lưu trong ứng dụng để bạn xem lại.</p>
      </section>
    </aside>
  );
}

function ConversationSkeleton() {
  return <div className="assistant-conversation-skeleton" aria-label="Đang tải cuộc trò chuyện"><span /><span /><span /></div>;
}

function HistorySkeleton() {
  return <div className="assistant-history-skeleton" aria-label="Đang tải lịch sử"><span /><span /><span /></div>;
}

function ScopeSkeleton() {
  return <div className="assistant-scope-skeleton" aria-label="Đang tải phạm vi dữ liệu"><span /><span /><span /></div>;
}
