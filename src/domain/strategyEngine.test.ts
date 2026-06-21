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
  it("includes a stock that matches defaultTailCloseStrategy", () => {
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
    const results = screenQuotes(
      [{ ...baseQuote, changePercent: 8.1 }],
      defaultTailCloseStrategy
    );

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

  it("excludes quotes without any positive trigger reason", () => {
    const results = screenQuotes(
      [
        {
          code: "600003",
          name: "空行情",
          isST: false,
          isSuspended: false,
          isDelistingRisk: false
        }
      ],
      defaultTailCloseStrategy
    );

    expect(results).toEqual([]);
  });

  it("allows partially missing optional market fields when other positive reasons exist", () => {
    const results = screenQuotes(
      [
        {
          ...baseQuote,
          turnoverRate: undefined,
          movingAverages: undefined
        }
      ],
      defaultTailCloseStrategy
    );

    expect(results).toHaveLength(1);
    expect(results[0].reasons).toContain("涨幅在 0% 到 6%");
    expect(results[0].reasons).toContain("量比大于 1.2");
  });

  it("excludes delisting-risk stocks", () => {
    const results = screenQuotes(
      [{ ...baseQuote, isDelistingRisk: true }],
      defaultTailCloseStrategy
    );

    expect(results).toEqual([]);
  });

  it("requires late-session activity when strategy asks for it", () => {
    const results = screenQuotes(
      [{ ...baseQuote, lateSessionActive: false }],
      { ...defaultTailCloseStrategy, requireLateSessionActive: true }
    );

    expect(results).toEqual([]);
  });

  it("sorts results by score descending", () => {
    const results = screenQuotes(
      [
        { ...baseQuote, code: "600004", volumeRatio: 1.3 },
        { ...baseQuote, code: "600005", volumeRatio: 3.5 }
      ],
      defaultTailCloseStrategy
    );

    expect(results).toHaveLength(2);
    expect(results.map((result) => result.code)).toEqual(["600005", "600004"]);
  });
});
