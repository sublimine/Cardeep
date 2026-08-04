import { useRef } from 'react'
import { useGSAP } from '@gsap/react'
import gsap from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'

gsap.registerPlugin(ScrollTrigger, useGSAP)

const DIGITS = Array.from({ length: 10 }, (_, i) => i)

// Per-digit vertical roller — sampled 1:1 from the reference's own featured
// stat ("100+ Companies served"): each digit is its own `w-[1ch]` column,
// `overflow-y-clip`, holding all of 0-9 stacked, translated to reveal the
// target digit. Uses `yPercent` (relative to the stack's own height, which
// scales with font-size) instead of a fixed px offset so this stays correct
// under the parent's fluid `clamp()` font-size — no hardcoded digit height
// to keep in sync.
function DigitColumn({ digit, index }: { digit: number; index: number }) {
  const stackRef = useRef<HTMLDivElement>(null)

  useGSAP(() => {
    const el = stackRef.current
    if (!el) return
    const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches
    const target = -digit * 10

    if (reduce) {
      gsap.set(el, { yPercent: target })
      return
    }

    gsap.fromTo(
      el,
      { yPercent: 0 },
      {
        yPercent: target,
        duration: 1.4,
        delay: index * 0.1,
        ease: 'expo.out',
        scrollTrigger: { trigger: el, start: 'top 85%', once: true },
      }
    )
  }, [digit])

  return (
    <span className="relative inline-block w-[1ch] h-[1em] overflow-x-visible overflow-y-clip align-baseline leading-none tabular-nums">
      <span ref={stackRef} className="absolute inset-x-0 top-0 block leading-none">
        {DIGITS.map((d) => (
          <span key={d} className="block h-[1em] leading-[1em]">
            {d}
          </span>
        ))}
      </span>
    </span>
  )
}

interface OdometerProps {
  value: number
  className?: string
}

/**
 * Only meant for a page's single "hero" stat (matches the reference, which
 * applies this exclusively to its one featured number, not every counter —
 * the smaller supporting stats keep the plain `CountUp` ease-out tween).
 */
export default function Odometer({ value, className }: OdometerProps) {
  const digits = String(Math.max(0, Math.round(value))).split('')

  return (
    <span className={className} style={{ fontVariantNumeric: 'tabular-nums' }}>
      {digits.map((d, i) => (
        <DigitColumn key={i} digit={Number(d)} index={i} />
      ))}
    </span>
  )
}
