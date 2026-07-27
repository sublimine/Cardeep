/**
 * CARDEEP chart-engine — shared bar/point types.
 *
 * Extracted from `web/src/pages/terminal/market.ts` during the 09-trading-terminal Fase 0
 * demolition (plans/cardeep-omni/09-trading-terminal.md) — that file's synthetic instrument
 * universe and seeded RNG price generator were quarantined (`web/_quarantine/terminal-market-defi/`),
 * but its two type shapes are genuinely reusable and carry no mock-data baggage: any real
 * `market_bucket_daily` row (Fase 1) maps onto `Bar` directly.
 */
export interface Bar { time: string; open: number; high: number; low: number; close: number; volume: number }
export type PD = { time: string; value: number }
