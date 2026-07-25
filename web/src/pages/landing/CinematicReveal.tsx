import { useRef, type CSSProperties, type ReactNode } from 'react'
import { useGSAP } from '@gsap/react'
import gsap from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'

gsap.registerPlugin(ScrollTrigger, useGSAP)

interface CinematicRevealProps {
  children: ReactNode
  className?: string
  style?: CSSProperties
  /** Stagger the direct children of the wrapper instead of animating it as one block. */
  stagger?: boolean
  y?: number
  delay?: number
}

/**
 * Real GSAP ScrollTrigger reveal — confident, slow easing (`expo.out`), not the
 * plain opacity/translateY CSS transition the previous pass shipped. Blur +
 * y-offset + stagger on request, matching the "reveal choreography" bar the
 * rest of the product's cinematic direction doc calls for.
 */
export default function CinematicReveal({ children, className, style, stagger, y = 32, delay = 0 }: CinematicRevealProps) {
  const ref = useRef<HTMLDivElement>(null)

  useGSAP(
    () => {
      const el = ref.current
      if (!el) return
      const targets = stagger ? Array.from(el.children) : el
      gsap.set(targets, { opacity: 0, y, filter: 'blur(6px)' })
      gsap.to(targets, {
        opacity: 1,
        y: 0,
        filter: 'blur(0px)',
        duration: 1.1,
        delay,
        ease: 'expo.out',
        stagger: stagger ? 0.09 : 0,
        scrollTrigger: { trigger: el, start: 'top 85%', once: true },
      })
    },
    { scope: ref }
  )

  return (
    <div ref={ref} className={className} style={style}>
      {children}
    </div>
  )
}
