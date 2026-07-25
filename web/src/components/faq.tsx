import { Fragment } from 'react';
import * as Accordion from '@radix-ui/react-accordion';
import { ChevronDown, ChevronUp } from 'lucide-react';

import { Button } from '@/components/ui/button';
import { Container } from '@/components/ui/container';

/**
 * The eight questions, in order. Four of them are deliberate repeats — the
 * reference ships the list exactly like this, and every item resolves to the
 * same answer body.
 */
const FAQ_QUESTIONS = [
  'What exactly does this platform do?',
  'Do I need to be technical to use this tool?',
  'What’s a typical use case of an AI agentic workflow?',
  'Can I connect this with my existing stack?',
  'How does AI model selection work?',
  'Can I connect this with my existing stack?',
  'Do I need to be technical to use this tool?',
  'How does AI model selection work?',
] as const;

const FAQ_ANSWER =
  'Our platform lets you design, deploy, and manage AI-powered agentic workflows that can combine both automated (AI) and manual steps. These workflows connect to your existing tools (like Slack, Notion, or Google Sheets) and use AI agents to complete tasks.';

const TRIGGER_CLASSNAME =
  'group/accordion-trigger relative flex flex-1 items-start justify-between rounded-lg border border-transparent py-2.5 text-left transition-all outline-none focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50 focus-visible:after:border-ring aria-disabled:pointer-events-none aria-disabled:opacity-50 **:data-[slot=accordion-trigger-icon]:ml-auto **:data-[slot=accordion-trigger-icon]:size-6 **:data-[slot=accordion-trigger-icon]:text-muted-foreground -tracking-xs text-base leading-6 font-medium';

/**
 * FAQ split: copy plus the hiring card on the left, the accordion on the right.
 *
 * No entrance animation here — the only motion is the panel height tween and
 * the chevron swap, both driven by the trigger's aria-expanded / data-state.
 * Item values carry their index because the question strings repeat.
 */
export function Faq() {
  return (
    <section className="w-full">
      <Container className="grid grid-cols-1 gap-15 py-20 md:py-30 lg:grid-cols-2">
        <div className="flex flex-col gap-15 pt-8">
          <div className="flex flex-col gap-4">
            <h2 className="text-heading text-left text-4xl font-semibold tracking-tight md:text-5xl">
              Frequently Asked Questions
            </h2>
            <div className="-tracking-xs text-base leading-6 font-medium md:text-nowrap">
              Have more doubts? Reach out to us at{' '}
              <a
                className="text-dusty-green underline underline-offset-3"
                href="mailto:contact@aceternity.com"
              >
                contact@aceternity.com
              </a>
            </div>
          </div>
          <div className="bg-natural-white flex flex-col gap-8 rounded-3xl px-6 py-8 shadow-card-md w-full lg:max-w-lg">
            <div className="flex flex-col gap-3">
              <span className="font-medium text-2xl leading-8 -tracking-sm">
                Need a fast moving team of engineers for your startup?
              </span>
              <span className="font-medium text-muted-foreground text-base -tracking-xs leading-6">
                Aceternity is your best bet, we have designers, engineers and managers to
                take your project from 0-1.
              </span>
            </div>
            <div>
              <Button avatar="/manu.webp">Chat with Alex</Button>
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
            {FAQ_QUESTIONS.map((question, index) => {
              const value = `${question}-${index}`;

              return (
                <Fragment key={value}>
                  <Accordion.Item
                    data-slot="accordion-item"
                    className="py-8"
                    value={value}
                  >
                    <Accordion.Header className="flex">
                      <Accordion.Trigger
                        data-slot="accordion-trigger"
                        className={TRIGGER_CLASSNAME}
                      >
                        {question}
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
                        {FAQ_ANSWER}
                      </div>
                    </Accordion.Content>
                  </Accordion.Item>
                  {index < FAQ_QUESTIONS.length - 1 && (
                    <div className="bg-natural-black/15 h-px w-full" />
                  )}
                </Fragment>
              );
            })}
          </Accordion.Root>
        </div>
      </Container>
    </section>
  );
}
