import { sampleCurrentQuotes } from "../../src/data/sampleMarket";
import type { StockQuote } from "../../src/domain/types";

export interface MarketProvider {
  getCurrentQuotes(): Promise<StockQuote[]>;
}

export const sampleMarketProvider: MarketProvider = {
  async getCurrentQuotes() {
    return sampleCurrentQuotes;
  }
};
