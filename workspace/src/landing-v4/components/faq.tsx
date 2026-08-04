import { Fragment } from 'react';
import * as Accordion from '@radix-ui/react-accordion';
import { ChevronDown, ChevronUp } from 'lucide-react';

import { Button } from '@landing/components/ui/button';
import { Container } from '@landing/components/ui/container';
import { BRAND, FAQ } from '@landing/content/site';

const TRIGGER_CLASSNAME =
  'group/accordion-trigger relative flex flex-1 items-start justify-between rounded-lg border border-transparent py-2.5 text-left transition-all outline-none focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50 focus-visible:after:border-ring aria-disabled:pointer-events-none aria-disabled:opacity-50 **:data-[slot=accordion-trigger-icon]:ml-auto **:data-[slot=accordion-trigger-icon]:size-6 **:data-[slot=accordion-trigger-icon]:text-muted-foreground -tracking-xs text-base leading-6 font-medium';

/**
 * FAQ split: copy plus the demo card on the left, the accordion on the right.
 *
 * No entrance animation here — the only motion is the panel height tween and
 * the chevron swap, both driven by the trigger's aria-expanded / data-state.
 * Every question is distinct, so the question itself is the item value.
 */
export function Faq() {
  return (
    <section id="faq" className="w-full">
      <Container className="grid grid-cols-1 gap-15 py-20 md:py-30 lg:grid-cols-2">
        <div className="flex flex-col gap-15 pt-8">
          <div className="flex flex-col gap-4">
            <h2 className="text-heading text-left text-4xl font-semibold tracking-tight md:text-5xl">
              {FAQ.heading}
            </h2>
            <div className="-tracking-xs text-base leading-6 font-medium md:text-nowrap">
              {FAQ.note}{' '}
              <a
                className="text-dusty-green underline underline-offset-3"
                href={`mailto:${BRAND.email}`}
              >
                {BRAND.email}
              </a>
            </div>
          </div>
          <div className="glass flex flex-col gap-8 rounded-3xl px-6 py-8 w-full lg:max-w-lg">
            <div className="flex flex-col gap-3">
              <span className="font-medium text-2xl leading-8 -tracking-sm">
                {FAQ.cardTitle}
              </span>
              <span className="font-medium text-muted-foreground text-base -tracking-xs leading-6">
                {FAQ.cardBody}
              </span>
            </div>
            <div>
              <Button avatar="/shots/mark.webp">{FAQ.cardCta}</Button>
            </div>
          </div>
        </div>
        <div className="h-full w-full">
          <Accordion.Root
            type="single"
            collapsible
            dir="ltr"
            role="region"
            data-slot="accordion"
            className="flex w-full flex-col"
          >
            {FAQ.items.map((item, index) => (
              <Fragment key={item.q}>
                <Accordion.Item
                  data-slot="accordion-item"
                  className="py-8"
                  value={item.q}
                >
                  <Accordion.Header className="flex">
                    <Accordion.Trigger
                      data-slot="accordion-trigger"
                      className={TRIGGER_CLASSNAME}
                    >
                      {item.q}
                      <ChevronDown
                        className="pointer-events-none shrink-0 group-aria-expanded/accordion-trigger:hidden"
                        data-slot="accordion-trigger-icon"
                      />
                      <ChevronUp
                        className="pointer-events-none hidden shrink-0 group-aria-expanded/accordion-trigger:inline"
                        data-slot="accordion-trigger-icon"
                      />
                    </Accordion.Trigger>
                  </Accordion.Header>
                  <Accordion.Content
                    data-slot="accordion-content"
                    className="overflow-hidden text-sm data-[state=open]:animate-accordion-down data-[state=closed]:animate-accordion-up"
                  >
                    <div className="h-(--accordion-panel-height) pt-0 pb-2.5 data-ending-style:h-0 data-starting-style:h-0 [&_a]:hover:text-foreground [&_p:not(:last-child)]:mb-4">
                      {item.a}
                    </div>
                  </Accordion.Content>
                </Accordion.Item>
                {index < FAQ.items.length - 1 && (
                  <div className="bg-natural-black/15 h-px w-full" />
                )}
              </Fragment>
            ))}
          </Accordion.Root>
        </div>
      </Container>
    </section>
  );
}
