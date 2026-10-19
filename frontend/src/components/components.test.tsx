import { fireEvent, render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import { CategoryAvatar } from "./CategoryAvatar";
import { SidePanel } from "./SidePanel";
import { ThemeToggle } from "./ThemeToggle";
import { AuthNotice, PasswordField } from "./auth/AuthFormControls";
import { categoryIconOptions, getCategoryIcon } from "../lib/categoryIcons";
import { formatCompactCurrency, formatCurrency } from "../lib/format";

describe("format and category icon helpers", () => {
  it("formats full and compact Vietnamese currency", () => {
    expect(formatCurrency(1234)).toContain("1.234");
    expect(formatCurrency(1234).endsWith(" ₫")).toBe(true);
    expect(formatCompactCurrency(1_200_000).endsWith(" ₫")).toBe(true);
  });

  it("resolves registered icons and falls back by category type", () => {
    expect(categoryIconOptions).toHaveLength(24);
    expect(getCategoryIcon("utensils", "expense")).toBe(
      categoryIconOptions.find((item) => item.key === "utensils")?.icon,
    );
    expect(getCategoryIcon("unknown", "income")).toBe(
      categoryIconOptions.find((item) => item.key === "banknote")?.icon,
    );
    expect(getCategoryIcon(null, "expense")).toBe(
      categoryIconOptions.find((item) => item.key === "wallet")?.icon,
    );
  });

  it("renders a category avatar with its size and color", () => {
    const { container } = render(<CategoryAvatar category={{
      id: "c", name: "Food", type: "expense", color: "#123456", icon: "utensils",
    }} size="lg" />);
    const avatar = container.querySelector(".category-avatar") as HTMLElement;
    expect(avatar).toHaveClass("category-avatar--lg");
    expect(avatar.style.getPropertyValue("--category-color")).toBe("#123456");
  });
});

describe("ThemeToggle", () => {
  it("uses stored theme and allows switching", async () => {
    localStorage.setItem("theme", "dark");
    render(<ThemeToggle />);
    expect(screen.getByRole("button", { name: "Dùng giao diện tối" })).toHaveAttribute("aria-pressed", "true");
    await userEvent.click(screen.getByRole("button", { name: "Dùng giao diện sáng" }));
    expect(document.documentElement.dataset.theme).toBe("light");
    expect(localStorage.getItem("theme")).toBe("light");
  });

  it("uses the system preference when no theme is saved", () => {
    vi.mocked(window.matchMedia).mockReturnValueOnce({ matches: true } as MediaQueryList);
    render(<ThemeToggle />);
    expect(screen.getByRole("button", { name: "Dùng giao diện tối" })).toHaveAttribute("aria-pressed", "true");
  });
});

describe("SidePanel", () => {
  it("renders nothing when closed", () => {
    const { container } = render(<SidePanel open={false} title="Title" onClose={vi.fn()}>Body</SidePanel>);
    expect(container).toBeEmptyDOMElement();
  });

  it("sets modal semantics, closes and traps keyboard focus", async () => {
    const appRoot = document.createElement("div");
    appRoot.id = "root";
    document.body.appendChild(appRoot);
    const outside = document.createElement("button");
    document.body.appendChild(outside);
    outside.focus();
    const onClose = vi.fn();
    const { unmount } = render(
      <SidePanel
        open
        title="Edit"
        description="Description"
        footer={<button>Save</button>}
        onClose={onClose}
      >
        <input aria-label="Name" data-panel-initial-focus />
      </SidePanel>,
    );
    expect(screen.getByRole("dialog")).toHaveAttribute("aria-describedby", "panel-description");
    expect(appRoot).toHaveAttribute("inert");
    await new Promise((resolve) => window.setTimeout(resolve, 0));
    expect(screen.getByLabelText("Name")).toHaveFocus();

    fireEvent.keyDown(window, { key: "Escape" });
    expect(onClose).toHaveBeenCalledOnce();
    await userEvent.click(screen.getByRole("button", { name: "Đóng bảng thao tác" }));
    await userEvent.click(screen.getByRole("button", { name: "Đóng" }));
    expect(onClose).toHaveBeenCalledTimes(3);

    const first = screen.getByRole("button", { name: "Đóng" });
    const last = screen.getByRole("button", { name: "Save" });
    last.focus();
    fireEvent.keyDown(window, { key: "Tab" });
    expect(first).toHaveFocus();
    first.focus();
    fireEvent.keyDown(window, { key: "Tab", shiftKey: true });
    expect(last).toHaveFocus();

    unmount();
    expect(appRoot).not.toHaveAttribute("inert");
    expect(outside).toHaveFocus();
    appRoot.remove();
    outside.remove();
  });
});

describe("auth form controls", () => {
  it("renders password visibility, hint and action", async () => {
    const onToggle = vi.fn();
    const onChange = vi.fn();
    const { rerender } = render(<PasswordField
      id="password"
      label="Mật khẩu"
      value="secret"
      onChange={onChange}
      visible={false}
      onToggle={onToggle}
      autoComplete="current-password"
      hint="At least six"
      labelAction={<a href="/forgot">Forgot</a>}
    />);
    expect(screen.getByLabelText("Mật khẩu")).toHaveAttribute("type", "password");
    expect(screen.getByLabelText("Mật khẩu")).toHaveAttribute("aria-describedby", "password-hint");
    await userEvent.click(screen.getByRole("button", { name: "Hiện mật khẩu" }));
    expect(onToggle).toHaveBeenCalledOnce();

    rerender(<PasswordField
      id="password" label="Mật khẩu" value="secret" onChange={onChange}
      visible onToggle={onToggle} autoComplete="current-password" disabled
    />);
    expect(screen.getByLabelText("Mật khẩu")).toHaveAttribute("type", "text");
    expect(screen.getByRole("button", { name: "Ẩn mật khẩu" })).toBeDisabled();
  });

  it("renders success and error notices with correct live roles", () => {
    const { rerender } = render(<AuthNotice>Saved</AuthNotice>);
    expect(screen.getByRole("status")).toHaveTextContent("Saved");
    rerender(<AuthNotice tone="error">Failed</AuthNotice>);
    expect(screen.getByRole("alert")).toHaveTextContent("Failed");
  });
});
