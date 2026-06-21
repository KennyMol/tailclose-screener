import type { StockQuote } from "../domain/types";

export const sampleCurrentQuotes: StockQuote[] = [
  {
    code: "600000",
    name: "浦发银行",
    latestPrice: 8.6,
    changePercent: 2.1,
    volumeRatio: 1.8,
    turnoverRate: 3.2,
    movingAverages: {
      ma5: 8.2,
      ma10: 8.1,
      ma20: 7.9
    },
    lateSessionActive: true
  },
  {
    code: "000001",
    name: "平安银行",
    latestPrice: 11.2,
    changePercent: 1.4,
    volumeRatio: 1.5,
    turnoverRate: 2.6,
    movingAverages: {
      ma5: 10.9,
      ma10: 10.7,
      ma20: 10.5
    },
    lateSessionActive: false
  },
  {
    code: "300000",
    name: "示例股票",
    latestPrice: 19.8,
    changePercent: 8.2,
    volumeRatio: 2.4,
    turnoverRate: 4.1,
    movingAverages: {
      ma5: 19.2,
      ma10: 18.8,
      ma20: 18.3
    },
    lateSessionActive: true
  }
];
