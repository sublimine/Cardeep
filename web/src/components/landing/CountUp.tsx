import { useEffect, useState } from 'react'

const fmt = (n: number) => n.toLocaleString('es-ES')

interface CountUpProps {
  value: number
  className?: string
}

/**
 * Animates from 0 to `value` on mount. Ports the cubic ease-out counter from
 * the validated portal mirror, but — unlike that version and an earlier draft
 * of this component — does NOT gate the animation behind an IntersectionObserver.
 * Verified via a real Puppeteer render that every KPI cell here sits at or just
 * below the fold: gating on 60%-visibility left them stuck showing a literal
 * "0" (indistinguishable from a real zero) whenever nothing had scrolled them
 * into view yet. Animating on mount is correct regardless of scroll position —
 * on-screen visitors see it count up, others just see the final number.
 *
 * Callers must only mount this once `value` is a real, known number (e.g. after
 * `useLandingStats` resolves) — it has no concept of "loading", by design: a
 * counter animating up to a guessed figure would be exactly the kind of
 * invented number this page must not show. Render a skeleton/placeholder in
 * the parent while data is pending, then mount `<CountUp>` in its place.
 */
export default function CountUp({ value, className }: CountUpProps) {
  const [display, setDisplay] = useState<string>('0')

  useEffect(() => {
    const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches
    if (reduce) {
      setDisplay(fmt(value))
      return
    }
    let raf = 0
    const duration = 1500
    const t0 = performance.now()
    const step = (now: number) => {
      const k = Math.min(1, (now - t0) / duration)
      setDisplay(fmt(Math.round(value * (1 - Math.pow(1 - k, 3)))))
      if (k < 1) raf = requestAnimationFrame(step)
    }
    raf = requestAnimationFrame(step)
    return () => cancelAnimationFrame(raf)
  }, [value])

  return (
    <span className={className} style={{ fontVariantNumeric: 'tabular-nums' }}>
      {display}
    </span>
  )
}
