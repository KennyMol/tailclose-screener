export type Signal = {
  date: string;
  code: string;
  name: string;
};

export type BacktestSummary = {
  signalCount: number;
  available: false;
  message: string;
};

const UNAVAILABLE_MESSAGE = "历史行情不足，暂不能计算胜率、平均收益和最大回撤。";

export function summarizeSignals(signals: Signal[]): BacktestSummary {
  return {
    signalCount: signals.length,
    available: false,
    message: UNAVAILABLE_MESSAGE
  };
}
