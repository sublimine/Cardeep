import { Button } from '@landing/components/ui/button';
import { Container } from '@landing/components/ui/container';
import { BRAND, PRICING, type Plan } from '@landing/content/site';

/** Order is fixed by the layout: two half-width cards, then the full-width one. */
const [STARTER, SCALE, ENTERPRISE] = PRICING.plans;

/**
 * Badge ink per tone. The pill's surface comes from the glass chip utility, so
 * tone only has to carry colour: `good` reuses the dusty green the page gives to
 * anything affirmative, `quiet` the muted grey.
 */
const BADGE_TONE: Record<Plan['badgeTone'], string> = {
  good: 'text-dusty-green',
  quiet: 'text-muted-foreground',
};

function FeatureItem({ label }: { label: string }) {
  return (
    <div className="text-muted-foreground flex items-center gap-2 text-sm leading-3.5 font-medium">
      <div className="bg-muted-foreground/50 size-2.5 rounded-full" />
      {label}
    </div>
  );
}

type PlanBadgeProps = {
  plan: Plan;
  /** Chip surface for the card the badge sits on: light or dark glass. */
  chip: string;
};

function PlanBadge({ plan, chip }: PlanBadgeProps) {
  return (
    <div
      className={`flex items-center gap-2 rounded-full px-4 py-1.5 ${chip} ${BADGE_TONE[plan.badgeTone]}`}
    >
      {plan.badge}
    </div>
  );
}

type PlanTitleProps = {
  top: string;
  bottom: string;
};

function PlanTitle({ top, bottom }: PlanTitleProps) {
  return (
    <div className="-tracking-xl text-2xl leading-8 font-medium">
      <span>{top}</span>
      <br />
      <span className="text-muted-foreground">{bottom}</span>
    </div>
  );
}

type PlanPriceProps = {
  price: string;
  period: string;
};

/**
 * Spanish puts the currency after the figure, so the euro sign takes the slot the
 * reference gave the leading dollar sign — same three spans, same sizes, mirrored
 * order, with a non-breaking space so figure and symbol never split. Plans priced
 * "A medida" carry neither symbol nor period.
 */
function PlanPrice({ price, period }: PlanPriceProps) {
  const hasCurrency = price.endsWith('€');
  const amount = hasCurrency ? price.slice(0, -1).trim() : price;

  return (
    <div className="-tracking-xs text-3xl leading-9 font-medium">
      <span>{amount}</span>
      {hasCurrency ? <span className="text-2xl">&nbsp;€</span> : null}
      {period ? <span className="text-2xl">{period}</span> : null}
    </div>
  );
}

export function Pricing() {
  return (
    <section id="precios" className="w-full">
      <Container className="flex flex-col gap-20 py-20 md:py-30">
        <div className="flex w-full flex-col justify-between gap-4 lg:flex-row">
          <h2 className="text-heading text-left text-4xl font-semibold tracking-tight md:text-5xl">
            {PRICING.heading}
          </h2>
          <div className="-tracking-xs text-base leading-6 font-medium md:text-nowrap">
            {PRICING.note}{' '}
            <a
              className="text-dusty-green underline underline-offset-3"
              href={`mailto:${BRAND.email}`}
            >
              {BRAND.email}
            </a>{' '}
            o{' '}
            <button className="cursor-pointer text-dusty-green underline underline-offset-3">
              {PRICING.noteCta}
            </button>
          </div>
        </div>
        <div className="flex flex-col gap-6">
          <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
            <div className="relative flex flex-col gap-2.5 overflow-hidden rounded-3xl p-3 glass text-natural-black">
              <div className="relative z-10 flex flex-col gap-16 rounded-2xl px-6 pt-4 pb-6 glass-quiet">
                <div className="flex flex-col gap-6">
                  <div className="flex w-fit flex-col gap-3 md:flex-row md:items-center">
                    <span className="-tracking-sm text-lg leading-5">{STARTER.name}</span>
                    <PlanBadge plan={STARTER} chip="glass-chip" />
                  </div>
                  <PlanTitle top={STARTER.title} bottom={STARTER.titleAccent} />
                </div>
                <div className="flex w-full flex-col gap-10 md:flex-row md:items-end md:justify-between md:gap-0">
                  <div className="flex flex-col gap-4">
                    <PlanPrice price={STARTER.price} period={STARTER.period} />
                    <div>
                      <Button avatar="/shots/mark.webp">{STARTER.cta}</Button>
                    </div>
                  </div>
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4.5 px-3 py-6">
                {STARTER.features.map((feature) => (
                  <FeatureItem key={feature} label={feature} />
                ))}
              </div>
            </div>
            {/* The featured card stays opaque black: it is the dark ground the glass
                panel inside it refracts, and white copy needs it to read. */}
            <div className="relative flex flex-col gap-2.5 overflow-hidden rounded-3xl p-3 bg-natural-black text-natural-white">
              <div className="absolute top-0 left-0 h-48 w-44 -translate-x-1/5 -translate-y-1/5">
                <div className="absolute top-0 left-[61.27px] h-48 w-28 rounded-full bg-stone-800 blur-2xl" />
                <div className="absolute top-[45.09px] left-0 size-20 rounded-full bg-white blur-[34.09px]" />
              </div>
              <div className="relative z-10 flex flex-col gap-16 rounded-2xl px-6 pt-4 pb-6 glass-dark">
                <div className="flex flex-col gap-6">
                  <div className="flex w-fit flex-col gap-3 md:flex-row md:items-center">
                    <span className="-tracking-sm text-lg leading-5">{SCALE.name}</span>
                    <PlanBadge plan={SCALE} chip="glass-chip-dark" />
                  </div>
                  <PlanTitle top={SCALE.title} bottom={SCALE.titleAccent} />
                </div>
                <div className="flex w-full flex-col gap-10 md:flex-row md:items-end md:justify-between md:gap-0">
                  <div className="flex flex-col gap-4">
                    <PlanPrice price={SCALE.price} period={SCALE.period} />
                    <div>
                      <Button avatar="/shots/mark.webp">{SCALE.cta}</Button>
                    </div>
                  </div>
                  {/* Slot the reference filled with an invented customer quote. */}
                  <p className="text-muted-foreground -tracking-xs text-sm leading-5 font-medium md:text-right">
                    {PRICING.annualNote}
                  </p>
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4.5 px-3 py-6">
                {SCALE.features.map((feature) => (
                  <FeatureItem key={feature} label={feature} />
                ))}
              </div>
            </div>
          </div>
          <div className="relative grid grid-cols-1 gap-6 overflow-hidden rounded-3xl px-4 py-4 lg:grid-cols-2 lg:gap-2.5 lg:px-5 lg:py-5 glass text-natural-black">
            <div className="flex h-full flex-col justify-between gap-16 lg:pl-4">
              <div className="flex flex-col gap-6">
                <div className="flex w-fit flex-col gap-3 md:flex-row md:items-center">
                  <span className="-tracking-sm text-lg leading-5">{ENTERPRISE.name}</span>
                  <PlanBadge plan={ENTERPRISE} chip="glass-chip" />
                </div>
                <PlanTitle top={ENTERPRISE.title} bottom={ENTERPRISE.titleAccent} />
              </div>
              <div className="flex flex-col gap-4">
                <PlanPrice price={ENTERPRISE.price} period={ENTERPRISE.period} />
                <div>
                  <Button avatar="/shots/mark.webp">{ENTERPRISE.cta}</Button>
                </div>
              </div>
            </div>
            <div className="glass-quiet grid grid-cols-1 gap-4.5 rounded-xl px-8 py-6 md:grid-cols-2">
              {ENTERPRISE.features.map((feature) => (
                <FeatureItem key={feature} label={feature} />
              ))}
            </div>
          </div>
        </div>
      </Container>
    </section>
  );
}
