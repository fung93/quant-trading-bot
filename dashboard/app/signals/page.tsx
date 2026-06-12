import EquityCurve from "@/components/EquityCurve";
import {
  KILL_SWITCH_DD,
  MYR_PER_USD,
  fmtMYT,
  getClosedTrades,
  getEngineState,
  getLatestClose,
  getOpenTrades,
  getPaperEquity,
  getSignals,
  netReturn,
  INITIAL_CAPITAL_USD,
} from "@/lib/paper";

export const dynamic = "force-dynamic";

export default async function SignalsPage() {
  let signals, openTrades, closedEth, state, equity, ethPrice;
  try {
    [signals, openTrades, closedEth, state, equity, ethPrice] = await Promise.all([
      getSignals(50),
      getOpenTrades(),
      getClosedTrades("ETHUSDT"),
      getEngineState(),
      getPaperEquity(),
      getLatestClose("ETHUSDT"),
    ]);
  } catch {
    return (
      <main className="mx-auto w-full max-w-4xl p-4">
        <p className="rounded-lg border border-amber-500/40 bg-amber-500/10 p-3 text-sm text-amber-300">
          Paper-trading tables not ready - run db/migrations/003_paper_trading.sql
          in the Supabase SQL editor, then refresh.
        </p>
      </main>
    );
  }

  const peak = Math.max(
    Number((state["equity_peak"] as { peak?: number })?.peak ?? INITIAL_CAPITAL_USD),
    equity.equity
  );
  const dd = peak > 0 ? (peak - equity.equity) / peak : 0;
  const kill = Boolean((state["kill_switch"] as { active?: boolean })?.active);

  // Equity curve points from closed ETH trades (chronological).
  let running = INITIAL_CAPITAL_USD;
  const curve = closedEth
    .filter((t) => t.closed_at)
    .map((t) => {
      running += t.pnl_usd ?? 0;
      return { time: Math.floor(new Date(t.closed_at as string).getTime() / 1000), value: running };
    });

  return (
    <main className="mx-auto w-full max-w-4xl space-y-4 p-4">
      <h1 className="text-lg font-semibold tracking-tight">Signals & paper book</h1>

      {kill && (
        <div className="rounded-lg border border-red-500/50 bg-red-500/10 p-3 text-sm text-red-300">
          Kill switch ACTIVE - new entries halted. Manual reset only (see README).
        </div>
      )}

      <section className="grid grid-cols-1 gap-3 sm:grid-cols-3">
        <div className="rounded-lg border border-white/10 bg-white/[0.02] p-3">
          <div className="text-xs text-gray-500">Paper equity (ETH book)</div>
          <div className="mt-1 font-mono text-xl">${equity.equity.toFixed(2)}</div>
          <div className="text-xs text-gray-500">
            ~RM{(equity.equity * MYR_PER_USD).toFixed(0)} · closed {equity.closedPnl >= 0 ? "+" : ""}
            ${equity.closedPnl.toFixed(2)} · open MTM {equity.openMtm >= 0 ? "+" : ""}
            ${equity.openMtm.toFixed(2)}
          </div>
        </div>
        <div className="rounded-lg border border-white/10 bg-white/[0.02] p-3">
          <div className="text-xs text-gray-500">Peak / drawdown</div>
          <div className="mt-1 font-mono text-xl">${peak.toFixed(2)}</div>
          <div className={`text-xs ${dd >= KILL_SWITCH_DD * 0.7 ? "text-amber-400" : "text-gray-500"}`}>
            drawdown {(dd * 100).toFixed(1)}% of {(KILL_SWITCH_DD * 100).toFixed(0)}% kill line
          </div>
        </div>
        <div className="rounded-lg border border-white/10 bg-white/[0.02] p-3">
          <div className="text-xs text-gray-500">Closed ETH trades</div>
          <div className="mt-1 font-mono text-xl">{closedEth.length}</div>
          <div className="text-xs text-gray-500">target: 20-30 for Phase 3 review</div>
        </div>
      </section>

      <section className="rounded-lg border border-white/10 bg-white/[0.02] p-3">
        <h2 className="mb-2 text-sm font-medium text-gray-300">Open positions</h2>
        {openTrades.length === 0 && <p className="text-sm text-gray-500">None.</p>}
        {openTrades.map((t) => {
          const cur = t.symbol === "ETHUSDT" ? ethPrice : null;
          const upnl =
            cur && t.entry_actual && t.size_usd
              ? t.size_usd * netReturn(t.entry_actual, cur)
              : null;
          return (
            <div key={t.id} className="flex flex-wrap items-baseline gap-x-4 gap-y-1 border-t border-white/5 py-2 text-sm first:border-t-0">
              <span className="font-mono">{t.symbol}</span>
              <span className="text-gray-400">entry {t.entry_actual}</span>
              <span className="text-gray-400">stop {Number(t.stop_loss).toFixed(2)}</span>
              <span className="text-gray-400">${Number(t.size_usd).toFixed(2)}</span>
              {upnl !== null && (
                <span className={upnl >= 0 ? "text-emerald-400" : "text-red-400"}>
                  {upnl >= 0 ? "+" : ""}${upnl.toFixed(2)} unrealized
                </span>
              )}
              {t.notes === "observational" && (
                <span className="rounded bg-sky-500/20 px-1.5 py-0.5 text-xs text-sky-300">observational</span>
              )}
            </div>
          );
        })}
      </section>

      {curve.length >= 2 ? (
        <section className="rounded-lg border border-white/10 bg-white/[0.02] p-3">
          <h2 className="mb-2 text-sm font-medium text-gray-300">Paper equity curve (closed ETH trades)</h2>
          <EquityCurve points={curve} />
        </section>
      ) : (
        <p className="text-xs text-gray-500">
          Equity curve appears after 2 closed trades ({curve.length} so far).
        </p>
      )}

      <section className="rounded-lg border border-white/10 bg-white/[0.02] p-3">
        <h2 className="mb-2 text-sm font-medium text-gray-300">Signals (latest 50)</h2>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="text-gray-500">
              <tr>
                <th className="py-1 pr-3">Time (MYT)</th>
                <th className="py-1 pr-3">Symbol</th>
                <th className="py-1 pr-3">Type</th>
                <th className="py-1 pr-3">Ref price</th>
                <th className="py-1 pr-3">Stop</th>
                <th className="py-1 pr-3">Size</th>
                <th className="py-1 pr-3">Status</th>
              </tr>
            </thead>
            <tbody>
              {signals.length === 0 && (
                <tr><td colSpan={7} className="py-3 text-gray-500">No signals yet - the engine writes one per momentum cross.</td></tr>
              )}
              {signals.map((s) => (
                <tr key={s.id} className="border-t border-white/5 align-top">
                  <td className="py-1.5 pr-3 whitespace-nowrap text-gray-400">{fmtMYT(s.bar_open_time ?? s.created_at)}</td>
                  <td className="py-1.5 pr-3 font-mono">{s.symbol.replace("USDT", "")}</td>
                  <td className={`py-1.5 pr-3 ${s.signal_type === "entry" ? "text-emerald-400" : "text-red-400"}`}>{s.signal_type}</td>
                  <td className="py-1.5 pr-3 font-mono">{s.entry_price ?? "-"}</td>
                  <td className="py-1.5 pr-3 font-mono">{s.stop_loss ? Number(s.stop_loss).toFixed(2) : "-"}</td>
                  <td className="py-1.5 pr-3 font-mono">{s.size_usd ? `$${Number(s.size_usd).toFixed(2)}` : "-"}</td>
                  <td className="py-1.5 pr-3">
                    {s.symbol === "BTCUSDT" ? (
                      <span className="text-sky-400">observational</span>
                    ) : s.status === "pending" ? (
                      <span className="text-amber-400">awaiting log</span>
                    ) : (
                      <span className="text-gray-400">{s.status}</span>
                    )}
                    {s.reasoning && (
                      <details className="mt-1">
                        <summary className="cursor-pointer text-gray-500">reasoning</summary>
                        <p className="mt-1 max-w-md whitespace-pre-wrap text-gray-400">{s.reasoning}</p>
                      </details>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </main>
  );
}
