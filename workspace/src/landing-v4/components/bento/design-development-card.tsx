import { useEffect, useRef } from 'react';
import { motion } from 'framer-motion';

import { Button } from '@landing/components/ui/button';
import { BENTO } from '@landing/content/site';

/**
 * Dot-matrix backdrop drawn on the card's bottom-right canvas.
 *
 * Measured off the reference render at DPR 1: 4px white squares on an 8px
 * pitch, each square at its own random alpha. The three `mask-*` utilities on
 * the wrapper do the fading, so the canvas itself paints edge to edge.
 */
const DOT_SIZE = 4;
const DOT_PITCH = 8;
const DOT_MIN_ALPHA = 0.05;
const DOT_ALPHA_RANGE = 0.5;

function DotMatrixCanvas() {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const context = canvas.getContext('2d');
    if (!context) return;

    // Redraw only on a real size change, otherwise every observer tick would
    // reshuffle the random alphas and make the field flicker.
    let lastKey = '';

    const draw = () => {
      const { width, height } = canvas.getBoundingClientRect();
      const ratio = window.devicePixelRatio || 1;
      const key = `${width}x${height}x${ratio}`;
      if (width === 0 || height === 0 || key === lastKey) return;
      lastKey = key;

      canvas.width = Math.round(width * ratio);
      canvas.height = Math.round(height * ratio);
      context.setTransform(ratio, 0, 0, ratio, 0, 0);
      context.clearRect(0, 0, width, height);

      for (let y = 0; y < height; y += DOT_PITCH) {
        for (let x = 0; x < width; x += DOT_PITCH) {
          const alpha = DOT_MIN_ALPHA + Math.random() * DOT_ALPHA_RANGE;
          context.fillStyle = `rgba(255, 255, 255, ${alpha})`;
          context.fillRect(x, y, DOT_SIZE, DOT_SIZE);
        }
      }
    };

    draw();
    const observer = new ResizeObserver(draw);
    observer.observe(canvas);
    return () => observer.disconnect();
  }, []);

  return <canvas ref={canvasRef} className="block h-full w-full" />;
}

/**
 * Entrance offsets in seconds. The mockup assembles outside-in — shell first,
 * then chrome, then the skeleton content — so the card reads as a UI being
 * built rather than a picture fading in.
 */
const DELAY = {
  panel: 0,
  glow: 0.1,
  window: 0.1,
  trafficLights: 0.25,
  urlBar: 0.3,
  dotField: 0.3,
  viewport: 0.35,
  titleBar: 0.45,
  subtitleBar: 0.5,
  chips: 0.55,
  avatars: 0.6,
  imageTile: 0.65,
} as const;

/** Resting opacity of the masked dot layer, captured from the settled target. */
const DOT_FIELD_OPACITY = 0.2;

/** Skeleton bar widths the two placeholder rows animate out to. */
const TITLE_BAR_WIDTH = 128;
const SUBTITLE_BAR_WIDTH = 96;

const EASE = 'easeOut';
const DURATION = 0.5;

export function DesignDevelopmentCard() {
  return (
    <motion.div
      className="bg-natural-black relative col-span-19 grid overflow-hidden rounded-2xl p-4 lg:col-span-6"
      initial="hidden"
      whileInView="visible"
      viewport={{ once: true, amount: 0.2 }}
    >
      <div className="h-full w-full grid grid-cols-1 md:grid-cols-2 lg:grid-cols-1">
        <div className="w-full flex-1 h-85">
          <motion.svg
            className="absolute bottom-0 -left-40 z-40 rotate-45 fill-white/80 blur-3xl"
            width="100%"
            height="100%"
            variants={{ hidden: { opacity: 0 }, visible: { opacity: 1 } }}
            transition={{ duration: 0.8, delay: DELAY.glow, ease: EASE }}
          >
            <ellipse cx="50%" cy="50%" rx="100" ry="60" />
          </motion.svg>

          {/* Bezel behind the product window. It is the one surface here with
              nothing legible on it, so it can go translucent: the blurred glow
              above blooms through it while the window itself stays opaque. */}
          <motion.div
            className="glass-dark relative z-40 h-full overflow-hidden rounded-lg"
            variants={{ hidden: { opacity: 0, y: 20 }, visible: { opacity: 1, y: 0 } }}
            transition={{ duration: DURATION, delay: DELAY.panel, ease: EASE }}
          >
            <motion.div
              className="absolute inset-x-0 -bottom-4 mx-auto flex h-full w-[90%] flex-col rounded-lg bg-[#E6E6E6] p-2"
              variants={{ hidden: { y: 30 }, visible: { y: 0 } }}
              transition={{ duration: DURATION, delay: DELAY.window, ease: EASE }}
            >
              <div className="relative flex">
                <motion.div
                  className="flex items-center gap-1.5"
                  variants={{ hidden: { opacity: 0, scale: 0.8 }, visible: { opacity: 1, scale: 1 } }}
                  transition={{ duration: 0.35, delay: DELAY.trafficLights, ease: EASE }}
                >
                  <div className="size-1.5 rounded-full bg-[#FF5F57]" />
                  <div className="size-1.5 rounded-full bg-[#FFBD2E]" />
                  <div className="size-1.5 rounded-full bg-[#28C840]" />
                </motion.div>
                <motion.div
                  className="absolute inset-x-0 mx-auto h-2 w-32 rounded-full bg-white"
                  variants={{ hidden: { opacity: 0, scaleX: 0 }, visible: { opacity: 1, scaleX: 1 } }}
                  transition={{ duration: 0.4, delay: DELAY.urlBar, ease: EASE }}
                />
              </div>

              <motion.div
                className="mt-3 flex w-full flex-1 flex-col rounded-lg bg-white"
                variants={{ hidden: { opacity: 0 }, visible: { opacity: 1 } }}
                transition={{ duration: 0.4, delay: DELAY.viewport, ease: EASE }}
              >
                <div className="flex">
                  <div className="flex w-full items-center justify-between px-1.5 py-1">
                    <div className="size-2 rounded-full bg-[#D9D9D9]" />
                    <div className="flex items-center gap-1">
                      <div className="h-1 w-3 rounded-full bg-[#E6E6E6]" />
                      <div className="h-1 w-3 rounded-full bg-[#E6E6E6]" />
                      <div className="h-1 w-3 rounded-full bg-[#E6E6E6]" />
                      <div className="ml-1 h-1.5 w-4 rounded-sm bg-[#D9D9D9]" />
                    </div>
                  </div>
                </div>

                <div className="flex flex-1 flex-col items-center justify-center px-2 py-3">
                  <motion.div
                    className="h-2 rounded-full bg-[#D9D9D9]"
                    variants={{
                      hidden: { opacity: 0, width: 0 },
                      visible: { opacity: 1, width: TITLE_BAR_WIDTH },
                    }}
                    transition={{ duration: DURATION, delay: DELAY.titleBar, ease: EASE }}
                  />
                  <motion.div
                    className="mt-1.5 h-1 rounded-full bg-[#E6E6E6]"
                    variants={{
                      hidden: { opacity: 0, width: 0 },
                      visible: { opacity: 1, width: SUBTITLE_BAR_WIDTH },
                    }}
                    transition={{ duration: DURATION, delay: DELAY.subtitleBar, ease: EASE }}
                  />
                  <motion.div
                    className="mt-2 flex items-center gap-1"
                    variants={{ hidden: { opacity: 0, y: 5 }, visible: { opacity: 1, y: 0 } }}
                    transition={{ duration: 0.4, delay: DELAY.chips, ease: EASE }}
                  >
                    <div className="h-2 w-8 rounded-sm bg-[#D9D9D9]" />
                    <div className="h-2 w-8 rounded-sm bg-[#E6E6E6]" />
                  </motion.div>
                  <motion.div
                    className="mt-2 flex items-center gap-1"
                    variants={{ hidden: { opacity: 0 }, visible: { opacity: 1 } }}
                    transition={{ duration: 0.4, delay: DELAY.avatars, ease: EASE }}
                  >
                    <div className="size-3 rounded-full bg-[#E6E6E6]" />
                    <div className="size-3 rounded-full bg-[#E6E6E6]" />
                    <div className="size-3 rounded-full bg-[#E6E6E6]" />
                    <div className="size-3 rounded-full bg-[#E6E6E6]" />
                  </motion.div>
                  <motion.div
                    className="mt-3 flex h-full w-3/4 items-center justify-center rounded-sm bg-gray-100"
                    variants={{ hidden: { opacity: 0, scale: 0.9 }, visible: { opacity: 1, scale: 1 } }}
                    transition={{ duration: 0.45, delay: DELAY.imageTile, ease: EASE }}
                  >
                    {/* Inlined rather than imported: the installed @tabler/icons-react ships
                        newer corner paths (M3 7…) than the reference build (M4 8…). */}
                    <svg
                      xmlns="http://www.w3.org/2000/svg"
                      width="24"
                      height="24"
                      viewBox="0 0 24 24"
                      fill="none"
                      stroke="currentColor"
                      strokeWidth="2"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      className="tabler-icon tabler-icon-photo-scan size-6 text-neutral-400"
                    >
                      <path d="M15 8h.01" />
                      <path d="M6 13l2.644 -2.644a1.21 1.21 0 0 1 1.712 0l3.644 3.644" />
                      <path d="M13 13l1.644 -1.644a1.21 1.21 0 0 1 1.712 0l1.644 1.644" />
                      <path d="M4 8v-2a2 2 0 0 1 2 -2h2" />
                      <path d="M4 16v2a2 2 0 0 0 2 2h2" />
                      <path d="M16 4h2a2 2 0 0 1 2 2v2" />
                      <path d="M16 20h2a2 2 0 0 0 2 -2v-2" />
                    </svg>
                  </motion.div>
                </div>
              </motion.div>
            </motion.div>
          </motion.div>

          <motion.div
            className="absolute right-0 bottom-0 h-80 w-full mask-t-from-20% mask-b-from-90% mask-l-from-50%"
            variants={{ hidden: { opacity: 0 }, visible: { opacity: DOT_FIELD_OPACITY } }}
            transition={{ duration: 0.8, delay: DELAY.dotField, ease: EASE }}
          >
            <div className="pointer-events-none select-none absolute inset-0 w-full">
              <DotMatrixCanvas />
            </div>
          </motion.div>
        </div>

        <div className="mt-4 flex flex-col gap-6 px-4 py-4 z-10">
          <div className="relative">
            <h2 className="text-base font-medium text-white">{BENTO.feature.title}</h2>
            <p className="mt-4 text-base text-neutral-400">{BENTO.feature.body}</p>
          </div>
          <div>
            <Button className="my-4">{BENTO.feature.cta}</Button>
          </div>
        </div>
      </div>
    </motion.div>
  );
}
