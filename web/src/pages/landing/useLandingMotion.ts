import { useEffect } from 'react'
import gsap from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'
import Lenis from 'lenis'

gsap.registerPlugin(ScrollTrigger)

/**
 * Mounts Lenis + wires it to GSAP's ticker/ScrollTrigger, scoped to the
 * lifetime of the Landing page only — the rest of the app (Dashboard, etc.)
 * keeps native scroll. Cleans up fully on unmount so navigating away doesn't
 * leave a second scroll engine running underneath the app shell.
 */
export function useLandingMotion() {
  useEffect(() => {
    const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches
    if (reduce) return

    const lenis = new Lenis({ duration: 1.1, smoothWheel: true })
    const onTick = (time: number) => lenis.raf(time * 1000)
    gsap.ticker.add(onTick)
    gsap.ticker.lagSmoothing(0)
    lenis.on('scroll', ScrollTrigger.update)

    return () => {
      lenis.destroy()
      gsap.ticker.remove(onTick)
      ScrollTrigger.getAll().forEach((t) => t.kill())
    }
  }, [])
}
