import type {
  MovingAverages,
  NumericCondition,
  ScreenResult,
  StockQuote,
  Strategy
} from "./types";

function passesNumericCondition(
  quote: StockQuote,
  condition: NumericCondition
): boolean {
  const value = quote[condition.field];

  if (value === undefined) {
    return true;
  }

  if (condition.min !== undefined && value < condition.min) {
    return false;
  }

  if (condition.max !== undefined && value > condition.max) {
    return false;
  }

  return true;
}

function hasAnyMovingAverage(movingAverages: MovingAverages): boolean {
  return ["ma5", "ma10", "ma20"].some((key) => {
    const value = movingAverages[key as keyof MovingAverages];
    return value !== undefined;
  });
}

function priceAboveAnyMovingAverage(quote: StockQuote): boolean {
  if (
    quote.latestPrice === undefined ||
    quote.movingAverages === undefined ||
    !hasAnyMovingAverage(quote.movingAverages)
  ) {
    return true;
  }

  return ["ma5", "ma10", "ma20"].some((key) => {
    const value = quote.movingAverages?.[key as keyof MovingAverages];
    return value !== undefined && quote.latestPrice !== undefined
      ? quote.latestPrice >= value
      : false;
  });
}

function canEvaluateMovingAverage(quote: StockQuote): boolean {
  return (
    quote.latestPrice !== undefined &&
    quote.movingAverages !== undefined &&
    hasAnyMovingAverage(quote.movingAverages)
  );
}

function calculateScore(quote: StockQuote, reasons: string[]): number {
  return reasons.length * 10 + (quote.volumeRatio ?? 0);
}

export function screenQuotes(
  quotes: StockQuote[],
  strategy: Strategy
): ScreenResult[] {
  const results = quotes.flatMap((quote) => {
    const hasExcludedFlag = strategy.booleanExclusions.some(
      (exclusion) => quote[exclusion.field] === true
    );

    if (hasExcludedFlag) {
      return [];
    }

    const reasons: string[] = [];

    for (const condition of strategy.numericConditions) {
      if (!passesNumericCondition(quote, condition)) {
        return [];
      }

      if (quote[condition.field] !== undefined) {
        reasons.push(condition.label);
      }
    }

    if (strategy.movingAverageCondition) {
      if (!priceAboveAnyMovingAverage(quote)) {
        return [];
      }

      if (canEvaluateMovingAverage(quote)) {
        reasons.push(strategy.movingAverageCondition.label);
      }
    }

    if (strategy.requireLateSessionActive && !quote.lateSessionActive) {
      return [];
    }

    if (quote.lateSessionActive) {
      reasons.push("尾盘成交活跃");
    }

    return [
      {
        code: quote.code,
        name: quote.name,
        latestPrice: quote.latestPrice,
        changePercent: quote.changePercent,
        volumeRatio: quote.volumeRatio,
        reasons,
        score: calculateScore(quote, reasons)
      }
    ];
  });

  return results.sort((left, right) => right.score - left.score);
}
