import { describe, expect, it } from "vitest";
import { getScreenPayload } from "../_shared/screenService";

describe("getScreenPayload", () => {
  it("returns matching stock results with reasons", async () => {
    const payload = await getScreenPayload("tail-close-default");
    expect(payload.strategy.name).toBe("默认尾盘买入法");
    expect(payload.results.length).toBeGreaterThan(0);
    expect(payload.results[0].reasons.length).toBeGreaterThan(0);
  });
});
