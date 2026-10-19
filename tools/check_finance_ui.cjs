// Read-only UI smoke test with isolated API fixtures; no real user data is changed.
const fs = require("node:fs");
const path = require("node:path");
const assert = require("node:assert/strict");
const { chromium } = require(process.env.PLAYWRIGHT_MODULE || "playwright");
const root = path.resolve(__dirname, "..");
const testSource = fs.readFileSync(path.join(root, "frontend/src/App.test.tsx"), "utf8");
const fixture = name => {
  const match = testSource.match(new RegExp("const " + name + " = ([\\s\\S]*?);\\r?\\n"));
  if (!match) throw new Error("Missing fixture: " + name);
  return Function("return (" + match[1].replace(/ as const/g, "") + ")")();
};
async function main() {
  const browser = await chromium.launch({ headless: true, channel: "msedge" });
  try {
    const page = await browser.newPage({ viewport: { width: 1440, height: 1100 } });
    const errors = [];
    page.on("pageerror", error => errors.push(error.message));
    await page.addInitScript(() => localStorage.setItem("access_token", "ui-preview"));
    await page.route("**/api/**", route => {
      const endpoint = new URL(route.request().url()).pathname;
      let data = {};
      if (endpoint.endsWith("/me")) data = fixture("user");
      else if (endpoint.includes("/dashboard")) data = fixture("dashboard");
      else if (endpoint.includes("/categories")) data = fixture("categories");
      else if (endpoint.includes("/transactions")) data = fixture("transactions");
      else if (endpoint.includes("/reports")) data = fixture("report");
      else if (endpoint.includes("/health")) data = { status: "ok" };
      return route.fulfill({ json: data });
    });
    const output = path.join(root, ".tmp", "finance-ui");
    fs.mkdirSync(output, { recursive: true });
    for (const width of [1440, 390]) {
      await page.setViewportSize({ width, height: 1100 });
      for (const [url, heading] of [["dashboard","Tổng quan"],["transactions","Giao dịch"],["categories","Danh mục"],["reports","Báo cáo"]]) {
        await page.goto("http://127.0.0.1:5173/" + url);
        await page.getByRole("heading", { name: heading, level: 1 }).waitFor();
        await page.waitForTimeout(600);
        assert.equal(await page.getByRole("navigation").getByRole("link").count(), 4);
        const overflow = await page.evaluate(() => [...document.querySelectorAll(".finance-topbar, .finance-nav, .finance-content .surface, .finance-content .metric-card")].filter(el => el.getBoundingClientRect().right > innerWidth + 1).map(el => el.className));
        assert.deepEqual(overflow, [], "Overflow at " + width + "/" + url);
        await page.screenshot({ path: path.join(output, url + "-" + width + ".png"), fullPage: true });
      }
    }
    assert.deepEqual(errors, []);
    console.log("PASS: four routes, desktop/mobile layout, no page errors. Screenshots: " + output);
  } finally { await browser.close(); }
}
main().catch(error => { console.error(error); process.exitCode = 1; });
