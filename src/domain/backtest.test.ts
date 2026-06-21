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
