import { Navbar } from '@landing/components/navbar';
import { Hero } from '@landing/components/hero';
import { LogoWall } from '@landing/components/logo-wall';
import { EngineeringBento } from '@landing/components/engineering-bento';
import { Projects } from '@landing/components/projects';
import { Insights } from '@landing/components/insights';
import { Scaling } from '@landing/components/scaling';
import { Comparison } from '@landing/components/comparison';
import { Pricing } from '@landing/components/pricing';
import { FoundersDesk } from '@landing/components/founders-desk';
import { Feedback } from '@landing/components/feedback';
import { Faq } from '@landing/components/faq';
import { SiteFooter } from '@landing/components/site-footer';

import { useEffect } from 'react';

import './landing.generated.css';

/**
 * Public landing, ported verbatim from the `web/` app (its `src/App.tsx` plus
 * everything under `src/components`, `src/content` and `src/lib`).
 *
 * Two things differ from that app and nothing else does:
 *  - a `#cx-v4` wrapper opts the subtree into the landing's own Tailwind v4
 *    stylesheet. This app is built on Tailwind v3, so the landing's CSS is
 *    compiled separately and scoped under that id — see
 *    tools/build-landing-css.mjs for why re-authoring it in v3 would have
 *    changed how it looks, and why the scope is an id rather than a class.
 *    The wrapper is a separate element on purpose: scoped rules read
 *    `#cx-v4 <selector>`, which does not match the element carrying the scope
 *    itself, so the page root would otherwise fall back to the app's own
 *    `font-sans` and lose Inter.
 *  - imports resolve through the `@landing` alias instead of `@`, which here
 *    already points at this app's own `src`.
 *
 * The app's ambient `.cx-mesh` background sits at `z-index: -1`, so this
 * subtree's opaque `bg-background` covers it without any extra handling.
 */
export default function LandingV4() {
  // Stands the app's slim scrollbar down for as long as the landing is on
  // screen, so the page gets the platform scrollbar the original ships with —
  // and the same usable width. See the rules in src/index.css.
  useEffect(() => {
    document.documentElement.classList.add('on-landing-v4');
    return () => document.documentElement.classList.remove('on-landing-v4');
  }, []);

  return (
    <div id="cx-v4">
      <div className="bg-background relative font-sans antialiased">
        {/* Ambient bloom the glass panels refract; purely decorative. */}
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
    </div>
  );
}
