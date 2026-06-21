export interface MovingAverages {
  ma5?: number;
  ma10?: number;
  ma20?: number;
}

export interface StockQuote {
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
}

export type NumericConditionField =
  | "changePercent"
  | "volumeRatio"
  | "turnoverRate";

export interface NumericCondition {
  field: NumericConditionField;
  min?: number;
  max?: number;
  label: string;
}

export type BooleanExclusionField =
  | "isST"
  | "isSuspended"
  | "isDelistingRisk";

export interface BooleanExclusion {
  field: BooleanExclusionField;
  label: string;
}

export interface MovingAverageCondition {
  type: "priceAboveAnyMovingAverage";
  label: string;
}

export interface Strategy {
  id: string;
  name: string;
  numericConditions: NumericCondition[];
  booleanExclusions: BooleanExclusion[];
  movingAverageCondition?: MovingAverageCondition;
  requireLateSessionActive: boolean;
}

export interface ScreenResult {
  code: string;
  name: string;
  latestPrice?: number;
  changePercent?: number;
  volumeRatio?: number;
  reasons: string[];
  score: number;
}
