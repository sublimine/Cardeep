import { Navbar } from '../components/navbar'
import { Hero } from '../components/hero'
import { LogoWall } from '../components/logo-wall'
import { EngineeringBento } from '../components/engineering-bento'
import { Projects } from '../components/projects'
import { Insights } from '../components/insights'
import { Scaling } from '../components/scaling'
import { Comparison } from '../components/comparison'
import { Pricing } from '../components/pricing'
import { FoundersDesk } from '../components/founders-desk'
import { Feedback } from '../components/feedback'
import { Faq } from '../components/faq'
import { SiteFooter } from '../components/site-footer'

/**
 * Public landing (`/landing`, and `/` for anonymous visitors via `RootRedirect`).
 *
 * This is the 2026-07-25 rebuild (owner-directed: "quiero la nueva, no la
 * vieja") — ported from its standalone Tailwind v4 app (see git history at
 * e86efe8) into this router as the actual Landing route, instead of the
 * earlier 2026-07-23 `.cx-landing` version it replaces. Scoped under
 * `.cx-newlanding` (index.css) so its own font/background don't leak into
 * the app shell (Dashboard, Inteligencia, ...).
 */
export default function Landing() {
  return (
    <div className="cx-newlanding relative font-landing antialiased">
      <div className="aurora" aria-hidden="true" />
      <div className="relative z-10">
        <Navbar />
        <section className="flex max-w-screen flex-col items-center justify-center overflow-x-hidden">
          <Hero />
          <LogoWall />
          <EngineeringBento />
          <Projects />
          <Insights />
          <Scaling />
          <Comparison />
          <Pricing />
          <FoundersDesk />
          <Feedback />
          <Faq />
        </section>
        <SiteFooter />
      </div>
    </div>
  )
}
