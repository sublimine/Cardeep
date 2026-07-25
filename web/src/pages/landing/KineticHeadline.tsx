import { useRef } from 'react'
import { useGSAP } from '@gsap/react'
import gsap from 'gsap'
import { SplitText } from 'gsap/SplitText'

gsap.registerPlugin(SplitText, useGSAP)

interface KineticHeadlineProps {
  children: string
  className?: string
  as?: 'h1' | 'h2'
  delay?: number
}

/**
 * Line-mask kinetic reveal (GSAP SplitText) — the same technique GTA VI /
 * motionsites use for hero headlines: each line masks in on its own clip-path
 * track, staggered, slow confident easing. Real character-level motion,
 * not a CSS opacity fade.
 */
export default function KineticHeadline({ children, className, as = 'h1', delay = 0 }: KineticHeadlineProps) {
  const ref = useRef<HTMLHeadingElement>(null)
  const Tag = as

  useGSAP(
    () => {
      const el = ref.current
      if (!el) return
      const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches

      document.fonts.ready.then(() => {
        const split = new SplitText(el, { type: 'lines', linesClass: 'cx-line' })
        split.lines.forEach((line) => {
          const wrapper = document.createElement('span')
          wrapper.style.display = 'block'
          wrapper.style.overflow = 'hidden'
          line.parentNode?.insertBefore(wrapper, line)
          wrapper.appendChild(line)
        })

        if (reduce) {
          gsap.set(split.lines, { opacity: 1, yPercent: 0 })
          return
        }

        gsap.fromTo(
          split.lines,
          { yPercent: 110, opacity: 0 },
          { yPercent: 0, opacity: 1, duration: 1.1, delay, ease: 'expo.out', stagger: 0.1 }
        )
      })

      return () => undefined
    },
    { scope: ref }
  )

  return (
    <Tag ref={ref} className={className}>
      {children}
    </Tag>
  )
}
