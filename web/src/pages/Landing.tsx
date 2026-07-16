import { useLandingStats } from '../api/useCardeepStats'
import { useLandingMotion } from './landing/useLandingMotion'
import './landing/cinematic.css'
import LandingHero from './landing/LandingHero'
import TrustStrip from './landing/TrustStrip'
import IntelligenceTeaser from './landing/IntelligenceTeaser'
import Bento from './landing/Bento'
import ComparisonBand from './landing/ComparisonBand'
import CTAFooter from './landing/CTAFooter'

/**
 * Public landing (`/landing`, and `/` for anonymous visitors via `RootRedirect`).
 *
 * Deliberately dark/cinematic — a distinct visual identity from the light app
 * shell (Dashboard, Inteligencia, ...), scoped entirely under `.cx-landing`
 * (see `cinematic.css`). This is the owner's explicit, twice-stated reference
 * standard (`docs/frontend/03-MOTIONSITES-AUDIT.md`: "así quiero que sea mi
 * frontend", reaffirmed live 2026-07-16): motionsites.io-grade execution — real
 * GSAP/ScrollTrigger/SplitText choreography, not CSS fade-ins. Same brand
 * cobalt (#3B82F6) as the light app, so it still reads as one product.
 *
 * No 3D map of Spain in the hero (explicit, forceful owner directive this
 * session — that idiom stays exclusive to `/explore` and `/cobertura`).
 */
export default function Landing() {
  const { stats, coverage } = useLandingStats()
  useLandingMotion()

  return (
    <div className="cx-landing min-h-screen">
      <LandingHero stats={stats} />
      <TrustStrip stats={stats} coverage={coverage} />
      <IntelligenceTeaser />
      <Bento stats={stats} />
      <ComparisonBand coverage={coverage} />
      <CTAFooter />
    </div>
  )
}
