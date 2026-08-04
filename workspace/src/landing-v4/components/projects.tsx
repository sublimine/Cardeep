import { motion, type Variants } from 'framer-motion';

import { Container } from '@landing/components/ui/container';
import { SURFACES, SURFACES_HEADING, type Surface } from '@landing/content/site';

/**
 * Column spans are asymmetric per card, so the class string travels beside the
 * data instead of inside it — the surfaces themselves know nothing about layout.
 * Index order matches `SURFACES`: índice, precio, cobertura, historial,
 * oportunidades, terminal.
 */
const CARD_CLASSNAMES = [
  'group relative block text-left col-span-14 md:col-span-7 lg:col-span-9',
  'group relative block text-left col-span-14 md:col-span-7 lg:col-span-5',
  'group relative block text-left col-span-14 md:col-span-7 lg:col-span-7',
  // Verbatim from the target markup, duplicated `group` and all.
  'group block text-left group relative col-span-14 md:col-span-7 lg:col-span-7',
  'group relative block text-left col-span-14 md:col-span-7 lg:col-span-5',
  'group relative block text-left col-span-14 md:col-span-7 lg:col-span-9',
] as const;

const CARDS = SURFACES.map((surface, index) => ({
  surface,
  className: CARD_CLASSNAMES[index],
}));

/** Next.js `fill` image geometry, minus the `color: transparent` placeholder rule. */
const FILL_IMAGE_STYLE = {
  position: 'absolute',
  height: '100%',
  width: '100%',
  left: 0,
  top: 0,
  right: 0,
  bottom: 0,
} as const;

const overlayVariants: Variants = {
  rest: { opacity: 0, transition: { duration: 0.25, ease: 'easeOut' } },
  // The two inner blocks trail the overlay so the blur lands before the copy rises.
  hover: {
    opacity: 1,
    transition: { duration: 0.3, ease: 'easeOut', delayChildren: 0.08, staggerChildren: 0.06 },
  },
};

const blockVariants: Variants = {
  rest: { opacity: 0, y: 18, transition: { duration: 0.25, ease: 'easeOut' } },
  hover: { opacity: 1, y: 0, transition: { duration: 0.35, ease: 'easeOut' } },
};

function ArrowRight() {
  return (
    <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path
        d="M3.33374 8H12.6671"
        stroke="white"
        strokeWidth="1.33333"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      <path
        d="M8 3.3335L12.6667 8.00016L8 12.6668"
        stroke="white"
        strokeWidth="1.33333"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}

function ProjectCard({ surface, className }: { surface: Surface; className: string }) {
  return (
    <motion.a
      data-slot="card"
      className={className}
      href={surface.href}
      initial="rest"
      animate="rest"
      whileHover="hover"
    >
      <img
        alt={`Cardeep · ${surface.title}`}
        decoding="async"
        className="rounded-3xl object-cover object-center"
        style={FILL_IMAGE_STYLE}
        src={surface.image}
      />
      <motion.div
        className="glass-dark absolute inset-0 flex flex-col justify-between rounded-3xl p-6 md:p-8"
        variants={overlayVariants}
      >
        <motion.div className="space-y-2" variants={blockVariants}>
          <div className="text-natural-white -tracking-sm text-2xl leading-8 font-medium">
            {surface.title}
          </div>
          <p className="text-natural-white/80 text-base leading-6 font-medium">{surface.body}</p>
        </motion.div>
        <motion.div
          className="flex w-full items-end justify-between gap-4"
          variants={blockVariants}
        >
          <div className="flex items-center gap-1">
            <span className="text-natural-white tracking-xs text-sm leading-3.5 font-medium">
              Ver
            </span>
            <ArrowRight />
          </div>
          <span className="-tracking-xs text-natural-white/80 text-right text-sm leading-3.5 font-medium">
            {surface.tags}
          </span>
        </motion.div>
      </motion.div>
    </motion.a>
  );
}

export function Projects() {
  return (
    <section className="w-full">
      <Container className="relative flex w-full flex-col gap-20 overflow-hidden pt-40 pb-20 md:pt-65 md:pb-30 lg:pt-80 lg:pb-30">
        <div>
          <h2 className="absolute top-20 overflow-hidden opacity-25 md:top-30 lg:top-50 -tracking-xl text-page-header font-medium md:text-page-header-md lg:text-page-header-lg bg-linear-180 from-[#8C8879] to-transparent bg-clip-text text-transparent">
            {SURFACES_HEADING}
          </h2>
        </div>
        <div className="z-10 grid grid-cols-14 gap-6 [--card-height:440px] *:data-[slot='card']:max-h-(--card-height) *:data-[slot='card']:min-h-(--card-height) *:data-[slot='card']:overflow-hidden *:data-[slot='card']:rounded-3xl">
          {CARDS.map(({ surface, className }) => (
            <ProjectCard key={surface.id} surface={surface} className={className} />
          ))}
        </div>
      </Container>
    </section>
  );
}
