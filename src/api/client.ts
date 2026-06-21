import type { ScreenResult, Strategy } from "../domain/types";

export interface StrategyResponse {
  strategies: Strategy[];
}

export interface ScreenResponse {
  refreshedAt: string;
  dataSource: {
    name: string;
    live: boolean;
    note?: string;
  };
  results: ScreenResult[];
}

async function getJson<T>(url: string): Promise<T> {
  const response = await fetch(url);

  if (!response.ok) {
    throw new Error(`Request failed: ${response.status}`);
  }

  return response.json() as Promise<T>;
}

export function fetchStrategies(): Promise<StrategyResponse> {
  return getJson<StrategyResponse>("/api/strategies");
}

export function fetchScreen(strategyId: string): Promise<ScreenResponse> {
  const params = new URLSearchParams({ strategyId });
  return getJson<ScreenResponse>(`/api/screen?${params.toString()}`);
}
