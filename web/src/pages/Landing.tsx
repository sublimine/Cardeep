import { useLandingStats } from '../api/useCardeepStats'
import { useLandingMotion } from './landing/useLandingMotion'
import './landing/cinematic.css'
import LandingHero from './landing/LandingHero'
import TrustStrip from './landing/TrustStrip'
import Bento from './landing/Bento'
import StatsBand from './landing/StatsBand'
import ComparisonBand from './landing/ComparisonBand'
import FAQ from './landing/FAQ'
import CTAFooter from './landing/CTAFooter'

/**
 * Public landing (`/landing`, and `/` for anonymous visitors via `RootRedirect`).
 *
 * v3 (owner-directed 2026-07-23): structure, motion quality-bar and flat-card
 * visual language replicated from the real reference
 * (productized-agency-template-acetern.vercel.app, confirmed live via
 * Playwright), content 100% real CARDEEP data (census stats, real indexed
 * sources, real pricing plans — see tests/test_web_no_fabricated_data.py).
 * Section order mirrors the reference: dark hero → source trust wall →
 * capability bento → stats → comparison → FAQ → dark CTA + footer.
 * Scoped entirely under `.cx-landing` (see `cinematic.css`) so none of this
 * leaks into the light glassmorphism app shell (Dashboard, Inteligencia, ...).
 */
export default function Landing() {
  const { stats, coverage } = useLandingStats()
  useLandingMotion()

  return (
    <div className="cx-landing min-h-screen">
      <LandingHero />
      <TrustStrip />
      <Bento stats={stats} />
      <StatsBand stats={stats} coverage={coverage} />
      <ComparisonBand coverage={coverage} />
      <FAQ />
      <CTAFooter />
    </div>
  )
}
