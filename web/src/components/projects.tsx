import { motion, type Variants } from 'motion/react';

import { Container } from '@/components/ui/container';

const PROJECTS = [
  {
    alt: 'Project 1',
    src: '/assets/project-1.webp',
    // Column spans are asymmetric per card, so the class string travels with the data.
    className: 'group relative block text-left col-span-14 md:col-span-7 lg:col-span-9',
    title: 'AI search landing page',
    description:
      'A conversion-focused landing page designed to explain a complex AI product in under 10 seconds.',
    tags: 'Figma Design, Next.js Development',
  },
  {
    alt: 'Project 2',
    src: '/assets/project-2.webp',
    className: 'group relative block text-left col-span-14 md:col-span-7 lg:col-span-5',
    title: 'SaaS homepage refresh',
    description:
      'A tighter homepage structure that helps visitors understand product value without reading a wall of text.',
    tags: 'Strategy, Design System, Frontend Build',
  },
  {
    alt: 'Project 3',
    src: '/assets/project-3.webp',
    className: 'group relative block text-left col-span-14 md:col-span-7 lg:col-span-7',
    title: 'Agency portfolio upgrade',
    description:
      'A premium portfolio layout that feels editorial while still being easy to scan for leads.',
    tags: 'Brand Refresh, Web Design',
  },
  {
    alt: 'Project 4',
    src: '/assets/project-4.webp',
    // Verbatim from the target markup, duplicated `group` and all.
    className: 'group block text-left group relative col-span-14 md:col-span-7 lg:col-span-7',
    title: 'Funding launch page',
    description:
      'A narrative-led launch page built to support credibility, conversions, and investor attention.',
    tags: 'Figma Design, Next.js Development',
  },
  {
    alt: 'Project 5',
    src: '/assets/project-5.webp',
    className: 'group relative block text-left col-span-14 md:col-span-7 lg:col-span-5',
    title: 'Conversion page redesign',
    description:
      'A cleaner layout that guides the user from awareness to action with fewer distractions.',
    tags: 'UX Strategy, UI Design',
  },
  {
    alt: 'Project 6',
    src: '/assets/project-6.webp',
    className: 'group relative block text-left col-span-14 md:col-span-7 lg:col-span-9',
    title: 'Productized service homepage',
    description:
      'A homepage that positions a service like a product, making the offer easier to buy.',
    tags: 'Positioning, Design, Development',
  },
] as const;

type Project = (typeof PROJECTS)[number];

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

function ProjectCard({ project }: { project: Project }) {
  return (
    <motion.a
      data-slot="card"
      className={project.className}
      href="#"
      initial="rest"
      animate="rest"
      whileHover="hover"
    >
      <img
        alt={project.alt}
        decoding="async"
        className="rounded-3xl object-cover object-center"
        style={FILL_IMAGE_STYLE}
        src={project.src}
      />
      <motion.div
        className="bg-natural-black/50 absolute inset-0 flex flex-col justify-between rounded-3xl p-6 backdrop-blur-md md:p-8"
        variants={overlayVariants}
      >
        <motion.div className="space-y-2" variants={blockVariants}>
          <div className="text-natural-white -tracking-sm text-2xl leading-8 font-medium">
            {project.title}
          </div>
          <p className="text-natural-white/80 text-base leading-6 font-medium">
            {project.description}
          </p>
        </motion.div>
        <motion.div
          className="flex w-full items-end justify-between gap-4"
          variants={blockVariants}
        >
          <div className="flex items-center gap-1">
            <span className="text-natural-white tracking-xs text-sm leading-3.5 font-medium">
              View Project
            </span>
            <ArrowRight />
          </div>
          <span className="-tracking-xs text-natural-white/80 text-right text-sm leading-3.5 font-medium">
            {project.tags}
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
            Projects
          </h2>
        </div>
        <div className="z-10 grid grid-cols-14 gap-6 [--card-height:440px] *:data-[slot='card']:max-h-(--card-height) *:data-[slot='card']:min-h-(--card-height) *:data-[slot='card']:overflow-hidden *:data-[slot='card']:rounded-3xl">
          {PROJECTS.map((project) => (
            <ProjectCard key={project.alt} project={project} />
          ))}
        </div>
      </Container>
    </section>
  );
}
