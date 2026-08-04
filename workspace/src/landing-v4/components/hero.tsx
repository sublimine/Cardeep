import { useLandingStats } from '../../api/useCardeepStats';
import { HeroBackdrop } from './hero/HeroBackdrop';
import { HeroCopy } from './hero/HeroCopy';
import { MarketStrip } from './hero/MarketStrip';
import { SearchPanel } from './hero/SearchPanel';

/**
 * The cover: one photograph, and the index reading it.
 *
 * A deliberate contrast, not a decorative one. The picture carries why anyone
 * buys a car at all; the glass carries what Cardeep knows about it.
 *
 *   claim (left, over the darkened car body) · search panel (right, over sky)
 *   ── opportunity ticker, left half only ──
 *
 * The rail used to be full-width, 300px-tall product tiles hanging past the fold.
 * It is now a compact ticker under the text column and nothing else: at 74px it
 * sits ENTIRELY above the fold, because the old trick of clipping the strip
 * mid-card only works when the card is tall enough to survive losing its bottom
 * 40px. Cutting one of these would eat the price, and a price the reader cannot
 * see teases nothing. Capping it at ~54% keeps the floor of the cover from
 * becoming a second surface competing with the headline.
 *
 * `100dvh`, never `100svh` or `h-screen`: the dynamic unit is the one that does
 * not jump when mobile browser chrome collapses.
 */
export function Hero() {
  const { stats } = useLandingStats();

  return (
    <section className="relative isolate min-h-[100dvh] w-full overflow-hidden" aria-labelledby="hero-heading">
      <HeroBackdrop />

      <div className="max-w-container relative z-10 mx-auto flex min-h-[100dvh] w-full flex-col justify-center px-4 pb-[210px] pt-28 sm:px-6 lg:px-8 lg:pb-[180px] lg:pt-24">
        <div className="flex w-full flex-col items-start gap-10 lg:flex-row lg:items-center lg:gap-14">
          <div id="hero-heading" className="w-full lg:flex-1">
            <HeroCopy stats={stats} />
          </div>
          <div className="w-full lg:w-auto">
            <SearchPanel stats={stats} />
          </div>
        </div>
      </div>

      <div className="max-w-container absolute inset-x-0 bottom-10 z-10 mx-auto w-full">
        <MarketStrip />
      </div>
    </section>
  );
}
