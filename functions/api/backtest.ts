/// <reference types="@cloudflare/workers-types" />

import { summarizeSignals } from "../../src/domain/backtest";
import { jsonResponse } from "../_shared/http";

export const onRequestPost: PagesFunction = () => {
  return jsonResponse({
    summary: summarizeSignals([]),
    signals: []
  });
};
