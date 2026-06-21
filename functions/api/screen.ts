/// <reference types="@cloudflare/workers-types" />

import { jsonResponse } from "../_shared/http";
import { getScreenPayload } from "../_shared/screenService";

export const onRequestGet: PagesFunction = async ({ request }) => {
  const url = new URL(request.url);
  const strategyId = url.searchParams.get("strategyId") ?? "tail-close-default";

  return jsonResponse(await getScreenPayload(strategyId));
};
