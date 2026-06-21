import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, expect, test, vi } from "vitest";
import { App } from "./App";

const originalFetch = globalThis.fetch;

beforeEach(() => {
  globalThis.fetch = vi.fn(async (input: RequestInfo | URL) => {
    const url = input.toString();

    if (url.includes("/api/strategies")) {
      return Response.json({
        strategies: [{ id: "tail-close-default", name: "默认尾盘买入法" }],
      });
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
          score: 82,
        },
      ],
    });
  });
});

afterEach(() => {
  globalThis.fetch = originalFetch;
  vi.restoreAllMocks();
});

test("loads strategies and refreshes mobile screening results", async () => {
  const user = userEvent.setup();

  render(<App />);

  await screen.findByText("默认尾盘买入法");

  await user.click(screen.getByRole("button", { name: "刷新" }));

  await screen.findByText("600000");
  expect(screen.getByText("浦发银行")).toBeInTheDocument();
  expect(screen.getByText("+2.1%")).toBeInTheDocument();
  expect(screen.queryByText(/评分/)).not.toBeInTheDocument();
});
