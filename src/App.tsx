import { RefreshCw, SlidersHorizontal } from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import {
  fetchScreen,
  fetchStrategies,
  type ScreenResponse,
} from "./api/client";
import type { Strategy } from "./domain/types";

const defaultStrategyId = "tail-close-default";

function formatPercent(value?: number) {
  if (value === undefined) {
    return "--";
  }

  const prefix = value > 0 ? "+" : "";
  return `${prefix}${value.toFixed(1)}%`;
}

function formatNumber(value?: number) {
  return value === undefined ? "--" : value.toFixed(1);
}

function formatRefreshTime(refreshedAt?: string) {
  if (!refreshedAt) {
    return "未刷新";
  }

  return new Intl.DateTimeFormat("zh-CN", {
    hour: "2-digit",
    minute: "2-digit",
    hour12: false,
  }).format(new Date(refreshedAt));
}

export function App() {
  const [strategies, setStrategies] = useState<Strategy[]>([]);
  const [strategyId, setStrategyId] = useState(defaultStrategyId);
  const [screen, setScreen] = useState<ScreenResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(false);

  useEffect(() => {
    let active = true;

    fetchStrategies()
      .then(({ strategies }) => {
        if (!active) {
          return;
        }

        setStrategies(strategies);
        if (
          strategies.length > 0 &&
          !strategies.some((strategy) => strategy.id === defaultStrategyId)
        ) {
          setStrategyId(strategies[0].id);
        }
      })
      .catch(() => {
        if (active) {
          setError(true);
        }
      });

    return () => {
      active = false;
    };
  }, []);

  const selectedStrategyName = useMemo(() => {
    return (
      strategies.find((strategy) => strategy.id === strategyId)?.name ??
      "默认尾盘买入法"
    );
  }, [strategies, strategyId]);

  const refresh = async () => {
    setLoading(true);
    setError(false);

    try {
      setScreen(await fetchScreen(strategyId));
    } catch {
      setError(true);
    } finally {
      setLoading(false);
    }
  };

  const showSampleNote =
    screen?.dataSource.live === false && screen.dataSource.note
      ? screen.dataSource.note
      : null;

  return (
    <main className="app-shell">
      <header className="topbar">
        <div>
          <p className="eyebrow">Tailclose Screener</p>
          <h1>尾盘买入法</h1>
        </div>
        <button className="icon-button" type="button" aria-label="设置">
          <SlidersHorizontal size={20} aria-hidden="true" />
        </button>
      </header>

      <section className="controls" aria-label="筛选控制">
        <label className="strategy-picker">
          <span>策略</span>
          <select
            value={strategyId}
            onChange={(event) => setStrategyId(event.target.value)}
          >
            {strategies.length === 0 ? (
              <option value={strategyId}>{selectedStrategyName}</option>
            ) : (
              strategies.map((strategy) => (
                <option key={strategy.id} value={strategy.id}>
                  {strategy.name}
                </option>
              ))
            )}
          </select>
        </label>
        <button
          className="refresh-button"
          type="button"
          onClick={refresh}
          disabled={loading}
        >
          <RefreshCw size={18} aria-hidden="true" />
          刷新
        </button>
      </section>

      <section className="status-line" aria-live="polite">
        <span>{formatRefreshTime(screen?.refreshedAt)}</span>
        {showSampleNote ? <span>{showSampleNote}</span> : null}
      </section>

      {loading ? <section className="message">正在刷新...</section> : null}
      {error ? <section className="message error">刷新失败，请稍后再试</section> : null}

      {!loading && !error && screen?.results.length === 0 ? (
        <section className="message">当前没有符合策略的股票</section>
      ) : null}

      {screen && screen.results.length > 0 ? (
        <section className="result-list" aria-label="筛选结果">
          {screen.results.map((result) => (
            <article className="result-card" key={result.code}>
              <div className="result-head">
                <div>
                  <div className="stock-code">{result.code}</div>
                  <h2>{result.name}</h2>
                </div>
                <div className="change">{formatPercent(result.changePercent)}</div>
              </div>
              <div className="metrics">
                <span>最新 {result.latestPrice?.toFixed(2) ?? "--"}</span>
                <span>量比 {formatNumber(result.volumeRatio)}</span>
                <span>评分 {result.score}</span>
              </div>
              <p className="reasons">{result.reasons.join(" / ")}</p>
            </article>
          ))}
        </section>
      ) : null}

      <footer className="risk-note">
        仅供策略筛选和观察，不构成投资建议。
      </footer>
    </main>
  );
}
