import { builtInStrategies } from "../../src/domain/strategies";
import { screenQuotes } from "../../src/domain/strategyEngine";
import { sampleMarketProvider } from "./provider";

export async function getScreenPayload(strategyId: string) {
  const strategy =
    builtInStrategies.find((candidate) => candidate.id === strategyId) ??
    builtInStrategies[0];
  const quotes = await sampleMarketProvider.getCurrentQuotes();

  return {
    strategy,
    refreshedAt: new Date().toISOString(),
    results: screenQuotes(quotes, strategy),
    dataSource: {
      name: "sample",
      live: false,
      note: "当前为示例数据，后续可替换为实时行情接口。"
    }
  };
}
