// 09-trading-terminal F3b: watchlist v1 = localStorage (€0, per carta §6 "localStorage v1,
// como fija el blueprint §3.5") — no backend table, no auth dependency for this feature.
const STORAGE_KEY = 'cardeep.terminal.watchlist.v1'

export function getWatchlist(): string[] {
  try {
    const raw = window.localStorage.getItem(STORAGE_KEY)
    if (!raw) return []
    const parsed = JSON.parse(raw)
    return Array.isArray(parsed) ? parsed.filter((x): x is string => typeof x === 'string') : []
  } catch {
    return []
  }
}

export function isWatched(symbolKey: string): boolean {
  return getWatchlist().includes(symbolKey)
}

export function toggleWatch(symbolKey: string): string[] {
  const current = getWatchlist()
  const next = current.includes(symbolKey)
    ? current.filter(k => k !== symbolKey)
    : [...current, symbolKey]
  try {
    window.localStorage.setItem(STORAGE_KEY, JSON.stringify(next))
  } catch {
    // localStorage unavailable (private mode / quota) — watchlist degrades to session-only,
    // never throws into the render path.
  }
  return next
}
