import type { Strategy } from "./types";

export const defaultTailCloseStrategy: Strategy = {
  id: "tail-close-default",
  name: "默认尾盘买入法",
  numericConditions: [
    {
      field: "changePercent",
      min: 0,
      max: 6,
      label: "涨幅在 0% 到 6%"
    },
    {
      field: "volumeRatio",
      min: 1.2,
      label: "量比大于 1.2"
    },
    {
      field: "turnoverRate",
      min: 1,
      max: 12,
      label: "换手率适中"
    }
  ],
  booleanExclusions: [
    { field: "isST", label: "排除 ST" },
    { field: "isSuspended", label: "排除停牌" },
    { field: "isDelistingRisk", label: "排除退市风险" }
  ],
  movingAverageCondition: {
    type: "priceAboveAnyMovingAverage",
    label: "价格在均线上方"
  },
  requireLateSessionActive: false
};

export const builtInStrategies: Strategy[] = [defaultTailCloseStrategy];
