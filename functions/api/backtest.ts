/// <reference types="@cloudflare/workers-types" />

import { jsonResponse } from "../_shared/http";

export const onRequestPost: PagesFunction = () => {
  return jsonResponse({
    summary: {
      signalCount: 0,
      available: false
    },
    message: "回测接口已预留，接入历史行情后启用。"
  });
};
