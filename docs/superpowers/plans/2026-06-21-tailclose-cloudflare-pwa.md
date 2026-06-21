# Tailclose Cloudflare PWA Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the first deployable iPhone-friendly tail-close stock screening PWA for Cloudflare Pages.

**Architecture:** Use a Vite React frontend for the mobile UI and Cloudflare Pages Functions for API endpoints. Keep strategy logic in shared TypeScript modules so frontend, API handlers, and tests use the same behavior. Use deterministic sample market data first, with the data provider isolated for later replacement by a real行情 source.

**Tech Stack:** Vite, React, TypeScript, Vitest, Testing Library, Cloudflare Pages Functions.

---

## File Structure

- `package.json`: npm scripts and dependencies.
- `package-lock.json`: locked dependency versions after `npm install`.
- `index.html`: Vite HTML entry.
- `vite.config.ts`: Vite and Vitest configuration.
- `tsconfig.json`: TypeScript project settings.
- `tsconfig.node.json`: TypeScript config for Vite config files.
- `public/manifest.webmanifest`: iOS/PWA install metadata.
- `public/icons/icon.svg`: simple app icon.
- `src/main.tsx`: React entry.
- `src/App.tsx`: mobile app shell and state flow.
- `src/styles.css`: mobile-first UI styles.
- `src/domain/types.ts`: quote, strategy, screen, and backtest types.
- `src/domain/strategies.ts`: built-in strategies and custom condition evaluator.
- `src/domain/strategyEngine.ts`: stock screening logic.
- `src/domain/backtest.ts`: compact backtest summary logic.
- `src/data/sampleMarket.ts`: deterministic sample current and historical data.
- `src/api/client.ts`: browser API client.
- `src/test/setup.ts`: Testing Library setup.
- `src/domain/*.test.ts`: unit tests for strategy and backtest logic.
- `src/App.test.tsx`: UI state tests.
- `functions/api/strategies.ts`: Cloudflare Pages Function for strategies.
- `functions/api/screen.ts`: Cloudflare Pages Function for screening.
- `functions/api/backtest.ts`: Cloudflare Pages Function for backtesting.
- `functions/_shared/http.ts`: shared JSON response helpers.
- `functions/_shared/provider.ts`: data-provider abstraction backed by sample data.
- `functions/_shared/screenService.ts`: API composition around strategy engine.
- `functions/**/*.test.ts`: API handler tests.
- `wrangler.toml`: Cloudflare project metadata.
- `README.md`: setup, local run, and Cloudflare deployment instructions.

## Task 1: Scaffold The Vite App

**Files:**
- Create: `package.json`
- Create: `index.html`
- Create: `vite.config.ts`
- Create: `tsconfig.json`
- Create: `tsconfig.node.json`
- Create: `public/manifest.webmanifest`
- Create: `public/icons/icon.svg`
- Create: `src/main.tsx`
- Create: `src/App.tsx`
- Create: `src/styles.css`
- Create: `src/test/setup.ts`

- [ ] **Step 1: Create npm project files**

Create `package.json`:

```json
{
  "name": "tailclose-screener",
  "version": "0.1.0",
  "private": true,
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "tsc -b && vite build",
    "preview": "vite preview",
    "test": "vitest run --passWithNoTests",
    "test:watch": "vitest",
    "cf:dev": "wrangler pages dev dist --compatibility-date=2026-06-21"
  },
  "dependencies": {
    "@vitejs/plugin-react": "^4.3.4",
    "vite": "^6.0.7",
    "typescript": "^5.7.2",
    "react": "^19.0.0",
    "react-dom": "^19.0.0",
    "lucide-react": "^0.468.0"
  },
  "devDependencies": {
    "@cloudflare/workers-types": "^4.20241218.0",
    "@testing-library/jest-dom": "^6.6.3",
    "@testing-library/react": "^16.1.0",
    "@testing-library/user-event": "^14.5.2",
    "@types/react": "^19.0.2",
    "@types/react-dom": "^19.0.2",
    "jsdom": "^25.0.1",
    "vitest": "^2.1.8",
    "wrangler": "^3.99.0"
  }
}
```

- [ ] **Step 2: Install dependencies**

Run:

```bash
npm install
```

Expected: `package-lock.json` is created and npm exits with code 0.

- [ ] **Step 3: Add Vite and TypeScript config**

Create `vite.config.ts`:

```ts
import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

export default defineConfig({
  plugins: [react()],
  test: {
    environment: "jsdom",
    setupFiles: ["./src/test/setup.ts"],
    globals: true
  }
});
```

Create `tsconfig.json`:

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "lib": ["DOM", "DOM.Iterable", "ES2020"],
    "allowJs": false,
    "skipLibCheck": true,
    "esModuleInterop": true,
    "allowSyntheticDefaultImports": true,
    "strict": true,
    "forceConsistentCasingInFileNames": true,
    "module": "ESNext",
    "moduleResolution": "Bundler",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx",
    "types": ["vitest/globals", "@testing-library/jest-dom"]
  },
  "include": ["src", "functions"],
  "references": [{ "path": "./tsconfig.node.json" }]
}
```

Create `tsconfig.node.json`:

```json
{
  "compilerOptions": {
    "composite": true,
    "skipLibCheck": true,
    "module": "ESNext",
    "moduleResolution": "Bundler",
    "allowSyntheticDefaultImports": true,
    "strict": true
  },
  "include": ["vite.config.ts"]
}
```

- [ ] **Step 4: Add minimal app entry**

Create `index.html`:

```html
<!doctype html>
<html lang="zh-CN">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover" />
    <meta name="theme-color" content="#f7f7f2" />
    <link rel="manifest" href="/manifest.webmanifest" />
    <title>尾盘买入法</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
```

Create `src/test/setup.ts`:

```ts
import "@testing-library/jest-dom/vitest";
```

Create `src/main.tsx`:

```tsx
import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { App } from "./App";
import "./styles.css";

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <App />
  </StrictMode>
);
```

Create `src/App.tsx`:

```tsx
export function App() {
  return (
    <main className="app-shell">
      <header className="topbar">
        <div>
          <p className="eyebrow">Tailclose Screener</p>
          <h1>尾盘买入法</h1>
        </div>
      </header>
      <section className="empty-state">正在准备策略筛选器</section>
    </main>
  );
}
```

Create `src/styles.css`:

```css
:root {
  color: #1f2933;
  background: #f7f7f2;
  font-family: Inter, "PingFang SC", "Microsoft YaHei", system-ui, sans-serif;
  font-synthesis: none;
  text-rendering: optimizeLegibility;
}

* {
  box-sizing: border-box;
}

body {
  margin: 0;
  min-width: 320px;
  min-height: 100vh;
}

button,
select,
input {
  font: inherit;
}

.app-shell {
  min-height: 100vh;
  max-width: 560px;
  margin: 0 auto;
  padding: 18px 16px calc(24px + env(safe-area-inset-bottom));
}

.topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 18px;
}

.eyebrow {
  margin: 0 0 4px;
  color: #60707f;
  font-size: 12px;
}

h1 {
  margin: 0;
  font-size: 24px;
  line-height: 1.2;
}

.empty-state {
  border: 1px solid #d8ded6;
  border-radius: 8px;
  background: #ffffff;
  padding: 18px;
  color: #526170;
}
```

- [ ] **Step 5: Add PWA metadata**

Create `public/manifest.webmanifest`:

```json
{
  "name": "尾盘买入法",
  "short_name": "尾盘",
  "start_url": "/",
  "display": "standalone",
  "background_color": "#f7f7f2",
  "theme_color": "#f7f7f2",
  "icons": [
    {
      "src": "/icons/icon.svg",
      "sizes": "any",
      "type": "image/svg+xml"
    }
  ]
}
```

Create `public/icons/icon.svg`:

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 128 128">
  <rect width="128" height="128" rx="24" fill="#1f2933"/>
  <path d="M28 84h72" stroke="#f7f7f2" stroke-width="8" stroke-linecap="round"/>
  <path d="M34 74l20-20 14 14 28-32" fill="none" stroke="#7cc6a4" stroke-width="8" stroke-linecap="round" stroke-linejoin="round"/>
</svg>
```

- [ ] **Step 6: Verify scaffold builds**

Run:

```bash
npm test
npm run build
```

Expected: test command exits 0 with no tests found; build command exits 0 and creates `dist/`.

- [ ] **Step 7: Commit scaffold**

Run:

```bash
git add package.json package-lock.json index.html vite.config.ts tsconfig.json tsconfig.node.json public src
git commit -m "chore: scaffold cloudflare pwa"
```

## Task 2: Implement Strategy Domain With TDD

**Files:**
- Create: `src/domain/types.ts`
- Create: `src/domain/strategies.ts`
- Create: `src/domain/strategyEngine.ts`
- Create: `src/domain/strategyEngine.test.ts`

- [ ] **Step 1: Write failing strategy tests**

Create `src/domain/strategyEngine.test.ts`:

```ts
import { describe, expect, it } from "vitest";
import { defaultTailCloseStrategy } from "./strategies";
import { screenQuotes } from "./strategyEngine";
import type { StockQuote } from "./types";

const baseQuote: StockQuote = {
  code: "600000",
  name: "浦发银行",
  latestPrice: 10.2,
  changePercent: 2.1,
  volumeRatio: 1.8,
  turnoverRate: 3.2,
  isST: false,
  isSuspended: false,
  isDelistingRisk: false,
  movingAverages: { ma5: 10, ma10: 9.9, ma20: 9.7 },
  lateSessionActive: true
};

describe("screenQuotes", () => {
  it("includes a stock that matches the default tail-close strategy", () => {
    const results = screenQuotes([baseQuote], defaultTailCloseStrategy);
    expect(results).toHaveLength(1);
    expect(results[0]).toMatchObject({
      code: "600000",
      name: "浦发银行",
      changePercent: 2.1,
      volumeRatio: 1.8
    });
    expect(results[0].reasons).toContain("涨幅在 0% 到 6%");
    expect(results[0].reasons).toContain("量比大于 1.2");
  });

  it("excludes stocks with out-of-range percentage change", () => {
    const results = screenQuotes([{ ...baseQuote, code: "000001", changePercent: 8.1 }], defaultTailCloseStrategy);
    expect(results).toEqual([]);
  });

  it("excludes ST and suspended stocks when flags exist", () => {
    const results = screenQuotes(
      [
        { ...baseQuote, code: "600001", isST: true },
        { ...baseQuote, code: "600002", isSuspended: true }
      ],
      defaultTailCloseStrategy
    );
    expect(results).toEqual([]);
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```bash
npm test -- src/domain/strategyEngine.test.ts
```

Expected: FAIL because `./strategies`, `./strategyEngine`, and `./types` do not exist.

- [ ] **Step 3: Implement minimal domain types**

Create `src/domain/types.ts`:

```ts
export type MovingAverages = {
  ma5?: number;
  ma10?: number;
  ma20?: number;
};

export type StockQuote = {
  code: string;
  name: string;
  latestPrice?: number;
  changePercent?: number;
  volumeRatio?: number;
  turnoverRate?: number;
  isST?: boolean;
  isSuspended?: boolean;
  isDelistingRisk?: boolean;
  movingAverages?: MovingAverages;
  lateSessionActive?: boolean;
};

export type NumericCondition = {
  field: "changePercent" | "volumeRatio" | "turnoverRate";
  label: string;
  min?: number;
  max?: number;
};

export type BooleanExclusion = {
  field: "isST" | "isSuspended" | "isDelistingRisk";
  label: string;
};

export type MovingAverageCondition = {
  type: "priceAboveAnyMovingAverage";
  labels: string[];
};

export type Strategy = {
  id: string;
  name: string;
  numericConditions: NumericCondition[];
  booleanExclusions: BooleanExclusion[];
  movingAverageCondition?: MovingAverageCondition;
  requireLateSessionActive?: boolean;
};

export type ScreenResult = {
  code: string;
  name: string;
  latestPrice?: number;
  changePercent?: number;
  volumeRatio?: number;
  reasons: string[];
  score: number;
};
```

- [ ] **Step 4: Implement default strategy and screen engine**

Create `src/domain/strategies.ts`:

```ts
import type { Strategy } from "./types";

export const defaultTailCloseStrategy: Strategy = {
  id: "tail-close-default",
  name: "默认尾盘买入法",
  numericConditions: [
    { field: "changePercent", label: "涨幅在 0% 到 6%", min: 0, max: 6 },
    { field: "volumeRatio", label: "量比大于 1.2", min: 1.2 },
    { field: "turnoverRate", label: "换手率适中", min: 1, max: 12 }
  ],
  booleanExclusions: [
    { field: "isST", label: "排除 ST" },
    { field: "isSuspended", label: "排除停牌" },
    { field: "isDelistingRisk", label: "排除退市风险" }
  ],
  movingAverageCondition: {
    type: "priceAboveAnyMovingAverage",
    labels: ["价格在均线上方"]
  },
  requireLateSessionActive: false
};

export const builtInStrategies: Strategy[] = [defaultTailCloseStrategy];
```

Create `src/domain/strategyEngine.ts`:

```ts
import type { ScreenResult, StockQuote, Strategy } from "./types";

function passesNumeric(value: number | undefined, min?: number, max?: number) {
  if (value === undefined) return true;
  if (min !== undefined && value < min) return false;
  if (max !== undefined && value > max) return false;
  return true;
}

function isAboveAnyMovingAverage(quote: StockQuote) {
  if (quote.latestPrice === undefined || !quote.movingAverages) return true;
  const values = Object.values(quote.movingAverages).filter((value): value is number => typeof value === "number");
  if (values.length === 0) return true;
  return values.some((average) => quote.latestPrice! >= average);
}

export function screenQuotes(quotes: StockQuote[], strategy: Strategy): ScreenResult[] {
  return quotes
    .flatMap((quote): ScreenResult[] => {
      if (strategy.booleanExclusions.some((condition) => quote[condition.field])) {
        return [];
      }

      const reasons: string[] = [];
      for (const condition of strategy.numericConditions) {
        if (!passesNumeric(quote[condition.field], condition.min, condition.max)) {
          return [];
        }
        if (quote[condition.field] !== undefined) reasons.push(condition.label);
      }

      if (strategy.movingAverageCondition && !isAboveAnyMovingAverage(quote)) {
        return [];
      }
      if (strategy.movingAverageCondition && quote.latestPrice !== undefined && quote.movingAverages) {
        reasons.push(strategy.movingAverageCondition.labels[0]);
      }

      if (strategy.requireLateSessionActive && !quote.lateSessionActive) {
        return [];
      }
      if (quote.lateSessionActive) reasons.push("尾盘成交活跃");

      return [
        {
          code: quote.code,
          name: quote.name,
          latestPrice: quote.latestPrice,
          changePercent: quote.changePercent,
          volumeRatio: quote.volumeRatio,
          reasons,
          score: Math.min(99, reasons.length * 18 + Math.round((quote.volumeRatio ?? 1) * 8))
        }
      ];
    })
    .sort((a, b) => b.score - a.score);
}
```

- [ ] **Step 5: Run tests to verify green**

Run:

```bash
npm test -- src/domain/strategyEngine.test.ts
```

Expected: PASS.

- [ ] **Step 6: Commit domain logic**

Run:

```bash
git add src/domain
git commit -m "feat: add tail-close strategy engine"
```

## Task 3: Add Sample Data And API Services

**Files:**
- Create: `src/data/sampleMarket.ts`
- Create: `functions/_shared/http.ts`
- Create: `functions/_shared/provider.ts`
- Create: `functions/_shared/screenService.ts`
- Create: `functions/api/strategies.ts`
- Create: `functions/api/screen.ts`
- Create: `functions/api/backtest.ts`
- Create: `functions/api/screen.test.ts`

- [ ] **Step 1: Write failing API test**

Create `functions/api/screen.test.ts`:

```ts
import { describe, expect, it } from "vitest";
import { getScreenPayload } from "../_shared/screenService";

describe("getScreenPayload", () => {
  it("returns matching stock results with reasons", async () => {
    const payload = await getScreenPayload("tail-close-default");
    expect(payload.strategy.name).toBe("默认尾盘买入法");
    expect(payload.results.length).toBeGreaterThan(0);
    expect(payload.results[0].reasons.length).toBeGreaterThan(0);
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```bash
npm test -- functions/api/screen.test.ts
```

Expected: FAIL because `_shared/screenService` does not exist.

- [ ] **Step 3: Add deterministic market data**

Create `src/data/sampleMarket.ts`:

```ts
import type { StockQuote } from "../domain/types";

export const sampleCurrentQuotes: StockQuote[] = [
  {
    code: "600000",
    name: "浦发银行",
    latestPrice: 10.21,
    changePercent: 2.1,
    volumeRatio: 1.8,
    turnoverRate: 3.2,
    isST: false,
    isSuspended: false,
    isDelistingRisk: false,
    movingAverages: { ma5: 10.0, ma10: 9.9, ma20: 9.7 },
    lateSessionActive: true
  },
  {
    code: "000001",
    name: "平安银行",
    latestPrice: 12.44,
    changePercent: 1.4,
    volumeRatio: 1.5,
    turnoverRate: 2.6,
    isST: false,
    isSuspended: false,
    isDelistingRisk: false,
    movingAverages: { ma5: 12.2, ma10: 12.1, ma20: 11.8 },
    lateSessionActive: false
  },
  {
    code: "300000",
    name: "示例股票",
    latestPrice: 18.7,
    changePercent: 8.2,
    volumeRatio: 2.2,
    turnoverRate: 7.1,
    isST: false,
    isSuspended: false,
    isDelistingRisk: false,
    movingAverages: { ma5: 18.1, ma10: 17.8, ma20: 17.2 },
    lateSessionActive: true
  }
];
```

- [ ] **Step 4: Add shared API helpers and services**

Create `functions/_shared/http.ts`:

```ts
export function jsonResponse(data: unknown, init: ResponseInit = {}) {
  return new Response(JSON.stringify(data), {
    ...init,
    headers: {
      "content-type": "application/json; charset=utf-8",
      "cache-control": "no-store",
      ...init.headers
    }
  });
}
```

Create `functions/_shared/provider.ts`:

```ts
import { sampleCurrentQuotes } from "../../src/data/sampleMarket";
import type { StockQuote } from "../../src/domain/types";

export type MarketProvider = {
  getCurrentQuotes(): Promise<StockQuote[]>;
};

export const sampleMarketProvider: MarketProvider = {
  async getCurrentQuotes() {
    return sampleCurrentQuotes;
  }
};
```

Create `functions/_shared/screenService.ts`:

```ts
import { builtInStrategies } from "../../src/domain/strategies";
import { screenQuotes } from "../../src/domain/strategyEngine";
import { sampleMarketProvider } from "./provider";

export async function getScreenPayload(strategyId: string) {
  const strategy = builtInStrategies.find((item) => item.id === strategyId) ?? builtInStrategies[0];
  const quotes = await sampleMarketProvider.getCurrentQuotes();
  return {
    strategy,
    refreshedAt: new Date().toISOString(),
    results: screenQuotes(quotes, strategy),
    dataSource: {
      name: "sample",
      live: false,
      note: "当前为示例数据，后续可替换为实时行情接口。"
    }
  };
}
```

- [ ] **Step 5: Add Cloudflare function handlers**

Create `functions/api/strategies.ts`:

```ts
import { builtInStrategies } from "../../src/domain/strategies";
import { jsonResponse } from "../_shared/http";

export const onRequestGet: PagesFunction = async () => {
  return jsonResponse({ strategies: builtInStrategies });
};
```

Create `functions/api/screen.ts`:

```ts
import { jsonResponse } from "../_shared/http";
import { getScreenPayload } from "../_shared/screenService";

export const onRequestGet: PagesFunction = async ({ request }) => {
  const url = new URL(request.url);
  const strategyId = url.searchParams.get("strategyId") ?? "tail-close-default";
  return jsonResponse(await getScreenPayload(strategyId));
};
```

Create `functions/api/backtest.ts`:

```ts
import { jsonResponse } from "../_shared/http";

export const onRequestPost: PagesFunction = async () => {
  return jsonResponse({
    summary: {
      signalCount: 0,
      available: false
    },
    message: "回测接口已预留，接入历史行情后启用。"
  });
};
```

- [ ] **Step 6: Run API test to verify green**

Run:

```bash
npm test -- functions/api/screen.test.ts
```

Expected: PASS.

- [ ] **Step 7: Commit API services**

Run:

```bash
git add src/data functions
git commit -m "feat: add sample screening api"
```

## Task 4: Build The Mobile Main Screen

**Files:**
- Create: `src/api/client.ts`
- Replace: `src/App.tsx`
- Replace: `src/styles.css`
- Create: `src/App.test.tsx`

- [ ] **Step 1: Write failing UI tests**

Create `src/App.test.tsx`:

```tsx
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { App } from "./App";

describe("App", () => {
  it("loads strategies and refreshes matching stocks", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(async (url: string) => {
        if (url.includes("/api/strategies")) {
          return Response.json({ strategies: [{ id: "tail-close-default", name: "默认尾盘买入法" }] });
        }
        return Response.json({
          refreshedAt: "2026-06-21T06:55:00.000Z",
          dataSource: { name: "sample", live: false, note: "示例数据" },
          results: [
            {
              code: "600000",
              name: "浦发银行",
              latestPrice: 10.21,
              changePercent: 2.1,
              volumeRatio: 1.8,
              reasons: ["尾盘成交活跃"],
              score: 82
            }
          ]
        });
      })
    );

    render(<App />);
    await screen.findByText("默认尾盘买入法");
    await userEvent.click(screen.getByRole("button", { name: "刷新" }));
    await waitFor(() => expect(screen.getByText("600000")).toBeInTheDocument());
    expect(screen.getByText("浦发银行")).toBeInTheDocument();
    expect(screen.getByText("+2.1%")).toBeInTheDocument();
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```bash
npm test -- src/App.test.tsx
```

Expected: FAIL because current `App` does not load strategies or refresh results.

- [ ] **Step 3: Add API client**

Create `src/api/client.ts`:

```ts
import type { ScreenResult, Strategy } from "../domain/types";

export type StrategyResponse = {
  strategies: Strategy[];
};

export type ScreenResponse = {
  strategy?: Strategy;
  refreshedAt: string;
  results: ScreenResult[];
  dataSource: {
    name: string;
    live: boolean;
    note?: string;
  };
};

async function getJson<T>(url: string): Promise<T> {
  const response = await fetch(url);
  if (!response.ok) throw new Error(`Request failed: ${response.status}`);
  return response.json() as Promise<T>;
}

export function fetchStrategies() {
  return getJson<StrategyResponse>("/api/strategies");
}

export function fetchScreen(strategyId: string) {
  return getJson<ScreenResponse>(`/api/screen?strategyId=${encodeURIComponent(strategyId)}`);
}
```

- [ ] **Step 4: Replace app with mobile screen**

Replace `src/App.tsx`:

```tsx
import { RefreshCw, SlidersHorizontal } from "lucide-react";
import { useEffect, useState } from "react";
import { fetchScreen, fetchStrategies, type ScreenResponse } from "./api/client";
import type { Strategy } from "./domain/types";

type LoadState = "idle" | "loading" | "error";

function formatPercent(value?: number) {
  if (value === undefined) return "--";
  return `${value > 0 ? "+" : ""}${value.toFixed(1)}%`;
}

function formatTime(iso?: string) {
  if (!iso) return "未刷新";
  return new Intl.DateTimeFormat("zh-CN", {
    hour: "2-digit",
    minute: "2-digit",
    hour12: false
  }).format(new Date(iso));
}

export function App() {
  const [strategies, setStrategies] = useState<Strategy[]>([]);
  const [strategyId, setStrategyId] = useState("tail-close-default");
  const [screenData, setScreenData] = useState<ScreenResponse | null>(null);
  const [state, setState] = useState<LoadState>("idle");
  const [error, setError] = useState("");

  useEffect(() => {
    fetchStrategies()
      .then((payload) => {
        setStrategies(payload.strategies);
        if (payload.strategies[0]) setStrategyId(payload.strategies[0].id);
      })
      .catch(() => setError("策略加载失败"));
  }, []);

  async function refresh() {
    setState("loading");
    setError("");
    try {
      const payload = await fetchScreen(strategyId);
      setScreenData(payload);
      setState("idle");
    } catch {
      setError("刷新失败，请稍后再试");
      setState("error");
    }
  }

  return (
    <main className="app-shell">
      <header className="topbar">
        <div>
          <p className="eyebrow">Tailclose Screener</p>
          <h1>尾盘买入法</h1>
        </div>
        <button className="icon-button" aria-label="设置">
          <SlidersHorizontal size={19} />
        </button>
      </header>

      <section className="control-row" aria-label="筛选控制">
        <select value={strategyId} onChange={(event) => setStrategyId(event.target.value)}>
          {strategies.length === 0 ? <option value="tail-close-default">默认尾盘买入法</option> : null}
          {strategies.map((strategy) => (
            <option key={strategy.id} value={strategy.id}>
              {strategy.name}
            </option>
          ))}
        </select>
        <button className="refresh-button" onClick={refresh} disabled={state === "loading"}>
          <RefreshCw size={17} />
          刷新
        </button>
      </section>

      <div className="status-line">
        <span>{formatTime(screenData?.refreshedAt)}</span>
        {screenData?.dataSource.live === false ? <span>{screenData.dataSource.note}</span> : null}
      </div>

      {error ? <div className="notice error">{error}</div> : null}
      {state === "loading" ? <div className="notice">正在刷新...</div> : null}
      {screenData && screenData.results.length === 0 ? <div className="notice">当前没有符合策略的股票</div> : null}

      <section className="result-list" aria-label="筛选结果">
        {screenData?.results.map((result) => (
          <article className="stock-row" key={result.code}>
            <div className="stock-main">
              <div>
                <strong>{result.code}</strong>
                <span>{result.name}</span>
              </div>
              <b>{formatPercent(result.changePercent)}</b>
            </div>
            <div className="stock-meta">
              <span>量比 {result.volumeRatio?.toFixed(1) ?? "--"}</span>
              <span>{result.reasons.join("，")}</span>
            </div>
          </article>
        ))}
      </section>

      <p className="disclaimer">仅供策略筛选和观察，不构成投资建议。</p>
    </main>
  );
}
```

- [ ] **Step 5: Replace CSS with polished mobile styles**

Replace `src/styles.css`:

```css
:root {
  color: #1f2933;
  background: #f7f7f2;
  font-family: Inter, "PingFang SC", "Microsoft YaHei", system-ui, sans-serif;
  font-synthesis: none;
  text-rendering: optimizeLegibility;
}

* {
  box-sizing: border-box;
}

body {
  margin: 0;
  min-width: 320px;
  min-height: 100vh;
}

button,
select {
  font: inherit;
}

button {
  border: 0;
}

.app-shell {
  min-height: 100vh;
  max-width: 560px;
  margin: 0 auto;
  padding: 18px 16px calc(24px + env(safe-area-inset-bottom));
}

.topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 16px;
}

.eyebrow {
  margin: 0 0 4px;
  color: #60707f;
  font-size: 12px;
}

h1 {
  margin: 0;
  font-size: 24px;
  line-height: 1.2;
}

.icon-button {
  display: grid;
  width: 42px;
  height: 42px;
  place-items: center;
  border-radius: 8px;
  color: #26323d;
  background: #ffffff;
  box-shadow: inset 0 0 0 1px #d8ded6;
}

.control-row {
  display: grid;
  grid-template-columns: 1fr auto;
  gap: 10px;
  margin-bottom: 10px;
}

.control-row select {
  min-width: 0;
  height: 46px;
  border: 1px solid #d8ded6;
  border-radius: 8px;
  background: #ffffff;
  color: #1f2933;
  padding: 0 12px;
}

.refresh-button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 7px;
  min-width: 84px;
  height: 46px;
  border-radius: 8px;
  color: #ffffff;
  background: #1f6f5b;
}

.refresh-button:disabled {
  opacity: 0.62;
}

.status-line {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  gap: 8px;
  margin: 0 0 12px;
  color: #60707f;
  font-size: 12px;
  line-height: 1.5;
}

.notice {
  border: 1px solid #d8ded6;
  border-radius: 8px;
  background: #ffffff;
  padding: 12px;
  color: #526170;
  margin-bottom: 10px;
}

.notice.error {
  border-color: #f0b8ad;
  background: #fff7f5;
  color: #9c3328;
}

.result-list {
  display: grid;
  gap: 10px;
}

.stock-row {
  border: 1px solid #d8ded6;
  border-radius: 8px;
  background: #ffffff;
  padding: 13px;
}

.stock-main {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
}

.stock-main div {
  display: grid;
  gap: 3px;
}

.stock-main strong {
  font-size: 15px;
}

.stock-main span,
.stock-meta {
  color: #60707f;
}

.stock-main b {
  color: #b42318;
  font-size: 16px;
}

.stock-meta {
  display: grid;
  gap: 5px;
  margin-top: 10px;
  font-size: 13px;
  line-height: 1.45;
}

.disclaimer {
  margin: 18px 0 0;
  color: #7b8794;
  font-size: 12px;
  line-height: 1.5;
}
```

- [ ] **Step 6: Run UI test**

Run:

```bash
npm test -- src/App.test.tsx
```

Expected: PASS.

- [ ] **Step 7: Commit UI**

Run:

```bash
git add src/api src/App.tsx src/App.test.tsx src/styles.css
git commit -m "feat: add mobile screening interface"
```

## Task 5: Add Minimal Backtest Domain And Endpoint

**Files:**
- Create: `src/domain/backtest.ts`
- Create: `src/domain/backtest.test.ts`
- Replace: `functions/api/backtest.ts`

- [ ] **Step 1: Write failing backtest test**

Create `src/domain/backtest.test.ts`:

```ts
import { describe, expect, it } from "vitest";
import { summarizeSignals } from "./backtest";

describe("summarizeSignals", () => {
  it("returns a compact unavailable summary when historical exits are missing", () => {
    const summary = summarizeSignals([{ date: "2026-06-20", code: "600000", name: "浦发银行" }]);
    expect(summary).toEqual({
      signalCount: 1,
      available: false,
      message: "历史行情不足，暂不能计算胜率、平均收益和最大回撤。"
    });
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```bash
npm test -- src/domain/backtest.test.ts
```

Expected: FAIL because `backtest.ts` does not exist.

- [ ] **Step 3: Implement minimal backtest summary**

Create `src/domain/backtest.ts`:

```ts
export type Signal = {
  date: string;
  code: string;
  name: string;
};

export type BacktestSummary = {
  signalCount: number;
  available: boolean;
  message: string;
};

export function summarizeSignals(signals: Signal[]): BacktestSummary {
  return {
    signalCount: signals.length,
    available: false,
    message: "历史行情不足，暂不能计算胜率、平均收益和最大回撤。"
  };
}
```

- [ ] **Step 4: Replace backtest endpoint**

Replace `functions/api/backtest.ts`:

```ts
import { summarizeSignals } from "../../src/domain/backtest";
import { jsonResponse } from "../_shared/http";

export const onRequestPost: PagesFunction = async () => {
  return jsonResponse({
    summary: summarizeSignals([]),
    signals: []
  });
};
```

- [ ] **Step 5: Run tests**

Run:

```bash
npm test -- src/domain/backtest.test.ts
```

Expected: PASS.

- [ ] **Step 6: Commit backtest shell**

Run:

```bash
git add src/domain/backtest.ts src/domain/backtest.test.ts functions/api/backtest.ts
git commit -m "feat: add backtest summary shell"
```

## Task 6: Add Cloudflare Deployment Configuration And Docs

**Files:**
- Create: `wrangler.toml`
- Modify: `README.md`

- [ ] **Step 1: Add Wrangler config**

Create `wrangler.toml`:

```toml
name = "tailclose-screener"
compatibility_date = "2026-06-21"
pages_build_output_dir = "dist"
```

- [ ] **Step 2: Update README**

Add sections to `README.md`:

```md
## Local Development

```bash
npm install
npm run dev
```

## Build

```bash
npm test
npm run build
```

## Cloudflare Pages

Use these settings in Cloudflare Pages:

- Framework preset: Vite
- Build command: `npm run build`
- Build output directory: `dist`
- Root directory: `/`

The app currently uses sample market data. Replace the provider in `functions/_shared/provider.ts` when a stable行情 API is selected.
```

- [ ] **Step 3: Run full verification**

Run:

```bash
npm test
npm run build
git status --short
```

Expected: tests pass, build exits 0, and only intended files are modified.

- [ ] **Step 4: Commit deployment docs**

Run:

```bash
git add wrangler.toml README.md
git commit -m "docs: add cloudflare deployment instructions"
```

## Task 7: Final Verification And Push

**Files:**
- No new files.

- [ ] **Step 1: Run full verification**

Run:

```bash
npm test
npm run build
```

Expected: both commands exit 0.

- [ ] **Step 2: Review git state**

Run:

```bash
git status --short --branch
git log --oneline --decorate -5
```

Expected: branch is ahead of `origin/main` by the implementation commits and has no uncommitted changes.

- [ ] **Step 3: Push to GitHub**

Run:

```bash
git push origin main
```

Expected: push succeeds.

- [ ] **Step 4: Cloudflare dashboard deployment**

In Cloudflare Pages:

```text
Project name: tailclose-screener
Repository: KennyMol/tailclose-screener
Framework preset: Vite
Build command: npm run build
Build output directory: dist
Root directory: /
```

Expected: Cloudflare creates a `*.pages.dev` URL that opens the mobile app.

## Self-Review Notes

- Spec coverage: main mobile UI, strategy refresh, backend screening endpoint, PWA metadata, Cloudflare deployment config, and unavailable backtest summary shell are covered.
- Known limitation: real A-share market data is deliberately isolated behind `functions/_shared/provider.ts` and not implemented in this first deployable version.
- Safety: no brokerage trading, no Excel export, no arbitrary user code execution.
