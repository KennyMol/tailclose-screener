/// <reference types="@cloudflare/workers-types" />

import { builtInStrategies } from "../../src/domain/strategies";
import { jsonResponse } from "../_shared/http";

export const onRequestGet: PagesFunction = () => {
  return jsonResponse({ strategies: builtInStrategies });
};
