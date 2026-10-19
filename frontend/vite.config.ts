import { defineConfig } from "vitest/config";
import { loadEnv } from "vite";
import react from "@vitejs/plugin-react";
import { VitePWA } from "vite-plugin-pwa";

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), "");

  if (
    mode === "desktop" &&
    !/^https:\/\/.+\/api\/?$/.test(env.VITE_API_BASE_URL ?? "")
  ) {
    throw new Error(
      "Desktop builds require an HTTPS VITE_API_BASE_URL ending in /api.",
    );
  }

  return {
    plugins: [
      react(),
      VitePWA({
        disable: mode === "desktop",
        registerType: "autoUpdate",
        includeAssets: [
          "app-icon.svg",
          "icons/app-icon-192.png",
          "icons/app-icon-512.png",
        ],
        manifest: {
          name: "Sổ Chi Tiêu",
          short_name: "Sổ Chi Tiêu",
          description:
            "Quản lý giao dịch, danh mục và báo cáo thu chi cá nhân.",
          theme_color: "#5556cc",
          background_color: "#f4f5fa",
          display: "standalone",
          orientation: "any",
          start_url: "/",
          scope: "/",
          lang: "vi",
          categories: ["finance", "productivity"],
          icons: [
            {
              src: "/icons/app-icon-192.png",
              sizes: "192x192",
              type: "image/png",
              purpose: "any maskable",
            },
            {
              src: "/icons/app-icon-512.png",
              sizes: "512x512",
              type: "image/png",
              purpose: "any maskable",
            },
          ],
        },
        workbox: {
          globPatterns: ["**/*.{js,css,html,svg,png,woff,woff2}"],
          navigateFallback: "/index.html",
          navigateFallbackDenylist: [/^\/api\//, /^\/uploads\//],
          cleanupOutdatedCaches: true,
        },
        devOptions: {
          enabled: false,
        },
      }),
    ],

    test: {
      environment: "jsdom",
      setupFiles: ["./src/test/setup.ts"],
      coverage: {
        provider: "v8",
        reporter: ["text", "json-summary", "html"],
        reportsDirectory: "./coverage",
        include: ["src/**/*.{ts,tsx}"],
        exclude: [
          "src/main.tsx",
          "src/types.ts",
          "src/test/**",
          "**/*.test.{ts,tsx}",

          // Các trang đã bỏ khỏi ứng dụng web.
          "src/pages/AssistantPage.tsx",
          "src/pages/BudgetsPage.tsx",
          "src/pages/GoalsPage.tsx",
        ],
        thresholds: {
          statements: 60,
          branches: 45,
          functions: 55,
          lines: 65,
        },
      },
    },

    server: {
      port: 5173,
      proxy: {
        "/api": {
          target: "http://127.0.0.1:8000",
          changeOrigin: true,
        },
      },
    },
  };
});
