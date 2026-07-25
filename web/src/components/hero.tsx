import { useEffect, useMemo, useRef, useState } from 'react';
import { motion } from 'motion/react';
import { Button } from '@/components/ui/button';
import { Container } from '@/components/ui/container';

/** Side of one square cell in the tiled background grid, in SVG user units. */
const GRID_CELL = 70;

/**
 * Horizon arc geometry. The same four ellipses are re-stroked at increasing blur
 * radii to build the glow, so each path is declared once and referenced by the
 * layer table below.
 */
const ARC_PATH_A =
  'M975.5 255C1402.88 255 1749 569.029 1749 956C1749 1342.97 1402.88 1657 975.5 1657C548.119 1657 202 1342.97 202 956C202 569.029 548.119 255 975.5 255Z';
const ARC_PATH_B =
  'M975.5 253.5C1403.57 253.5 1750.5 568.065 1750.5 956C1750.5 1343.93 1403.57 1658.5 975.5 1658.5C547.432 1658.5 200.5 1343.93 200.5 956C200.5 568.065 547.432 253.5 975.5 253.5Z';
const ARC_PATH_C =
  'M975.5 255C1398.3 255 1739 565.452 1739 946C1739 1326.55 1398.3 1637 975.5 1637C552.695 1637 212 1326.55 212 946C212 565.452 552.695 255 975.5 255Z';
const ARC_PATH_D =
  'M975.5 212C1398.3 212 1739 522.452 1739 903C1739 1283.55 1398.3 1594 975.5 1594C552.695 1594 212 1283.55 212 903C212 522.452 552.695 212 975.5 212Z';

/** The six `opacity=0.4` blurred glow strokes, outermost blur last. */
const ARC_GLOW_LAYERS = [
  { gradient: 'paint3_linear_2693_2731', path: ARC_PATH_C, blur: 30 },
  { gradient: 'paint4_linear_2693_2731', path: ARC_PATH_C, blur: 30 },
  { gradient: 'paint5_linear_2693_2731', path: ARC_PATH_C, blur: 40 },
  { gradient: 'paint6_linear_2693_2731', path: ARC_PATH_C, blur: 50 },
  { gradient: 'paint7_linear_2693_2731', path: ARC_PATH_D, blur: 50 },
  { gradient: 'paint8_linear_2693_2731', path: ARC_PATH_D, blur: 100 },
] as const;

/** Every arc gradient fades its colour to fully transparent at offset 1. */
const ARC_GRADIENTS = [
  { id: 'paint0_linear_2693_2731', x1: '976', y1: '108.5', x2: '976', y2: '313.5', color: '#FA9A63' },
  { id: 'paint1_linear_2693_2731', x1: '976', y1: '108.5', x2: '976', y2: '582', color: '#FA9A63' },
  { id: 'paint2_linear_2693_2731', x1: '975.5', y1: '253', x2: '976', y2: '392', color: '#FA9A63' },
  { id: 'paint3_linear_2693_2731', x1: '975.5', y1: '243', x2: '976', y2: '468.5', color: '#FA9A63' },
  { id: 'paint4_linear_2693_2731', x1: '975.5', y1: '243', x2: '976', y2: '328.5', color: '#FA9A63' },
  { id: 'paint5_linear_2693_2731', x1: '975.5', y1: '243', x2: '976', y2: '334', color: '#CDA63C' },
  { id: 'paint6_linear_2693_2731', x1: '975.5', y1: '243', x2: '976', y2: '361', color: '#CDA63C' },
  { id: 'paint7_linear_2693_2731', x1: '975.5', y1: '200', x2: '976', y2: '336.5', color: '#CDA63C' },
  { id: 'paint8_linear_2693_2731', x1: '975.5', y1: '200', x2: '976', y2: '780.5', color: 'white' },
] as const;

/** Fixed star positions of the 822x158 starfield, as `[cx, cy, r]`. */
const STARS = [
  [1, 12, 1],
  [122, 113, 1],
  [108, 57, 1],
  [510, 96, 1],
  [700, 93, 1],
  [625, 126, 1],
  [821, 32, 1],
  [203.5, 157.5, 0.5],
  [167.5, 94.5, 0.5],
  [76.5, 81.5, 0.5],
  [157.5, 8.5, 0.5],
  [240.5, 80.5, 0.5],
  [256.5, 64.5, 0.5],
  [273.5, 84.5, 0.5],
  [285.5, 57.5, 0.5],
  [227.5, 114.5, 0.5],
  [202.5, 55.5, 0.5],
  [156.5, 65.5, 0.5],
  [330.5, 88.5, 0.5],
  [363.5, 102.5, 0.5],
  [476.5, 80.5, 0.5],
  [438.5, 107.5, 0.5],
  [422.5, 77.5, 0.5],
  [455.5, 56.5, 0.5],
  [488.5, 35.5, 0.5],
  [313.5, 66.5, 0.5],
  [231.5, 0.5, 0.5],
  [270.5, 108.5, 0.5],
  [573, 103, 0.5],
  [501.5, 150.5, 0.5],
  [456.5, 156.5, 0.5],
  [659.5, 77.5, 0.5],
  [746, 52, 0.5],
  [591.5, 1.5, 0.5],
  [389, 123, 1],
  [40, 72, 1],
] as const;

type Size = { width: number; height: number };

/**
 * Layer 1 — the tiled grid. Rendered only after the container has been measured,
 * because the cell count is derived from the live box size rather than baked in.
 */
function GridLayer({ size }: { size: Size }) {
  const cells = useMemo(() => {
    if (size.width <= 0 || size.height <= 0) return [];
    const columns = Math.ceil(size.width / GRID_CELL);
    const rows = Math.ceil(size.height / GRID_CELL);
    const result: { x: number; y: number }[] = [];
    for (let row = 0; row < rows; row++) {
      for (let column = 0; column < columns; column++) {
        result.push({ x: column * GRID_CELL, y: row * GRID_CELL });
      }
    }
    return result;
  }, [size.width, size.height]);

  return (
    <motion.div
      className="h-1/2 w-full mask-[linear-gradient(to_bottom,transparent_0%,black_50%,transparent_100%)]"
      initial={{ opacity: 0 }}
      whileInView={{ opacity: 0.2 }}
      viewport={{ once: true }}
      transition={{ duration: 1.2, ease: 'easeOut' }}
    >
      <svg width="100%" height="100%">
        <defs>
          <linearGradient id="goldGradient" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="var(--color-primary)" stopOpacity="0.5" />
            <stop offset="100%" stopColor="var(--color-primary)" stopOpacity="0" />
          </linearGradient>
        </defs>
        {cells.map((cell) => (
          <rect
            key={`${cell.x}-${cell.y}`}
            x={cell.x}
            y={cell.y}
            width={GRID_CELL}
            height={GRID_CELL}
            fill="transparent"
            stroke="rgba(255,255,255,0.08)"
          />
        ))}
      </svg>
    </motion.div>
  );
}

/** Layer 2 — the amber horizon ellipse and its stacked glow strokes. */
function HorizonArc() {
  return (
    <motion.div
      className="absolute -bottom-75 left-1/2 flex h-full w-full -translate-x-1/2 justify-center"
      initial={{ opacity: 0 }}
      whileInView={{ opacity: 1 }}
      viewport={{ once: true }}
      transition={{ duration: 1.4, ease: 'easeOut' }}
    >
      <div className="w-fit">
        <motion.svg
          width="1951"
          height="1806"
          viewBox="0 0 1951 1806"
          fill="none"
          overflow="visible"
          xmlns="http://www.w3.org/2000/svg"
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          transition={{ duration: 1.4, ease: 'easeOut' }}
        >
          <path d={ARC_PATH_A} stroke="url(#paint0_linear_2693_2731)" strokeWidth="4" />
          <path opacity="0.4" d={ARC_PATH_B} stroke="url(#paint1_linear_2693_2731)" />
          <g style={{ filter: 'blur(12px)', mixBlendMode: 'plus-lighter' }}>
            <path d={ARC_PATH_A} stroke="url(#paint2_linear_2693_2731)" strokeWidth="4" />
          </g>
          {ARC_GLOW_LAYERS.map((layer) => (
            <g
              key={layer.gradient}
              opacity="0.4"
              style={{ filter: `blur(${layer.blur}px)`, mixBlendMode: 'plus-lighter' }}
            >
              <path d={layer.path} stroke={`url(#${layer.gradient})`} strokeWidth="24" />
            </g>
          ))}
          <defs>
            {ARC_GRADIENTS.map((gradient) => (
              <linearGradient
                key={gradient.id}
                id={gradient.id}
                x1={gradient.x1}
                y1={gradient.y1}
                x2={gradient.x2}
                y2={gradient.y2}
                gradientUnits="userSpaceOnUse"
              >
                <stop stopColor={gradient.color} />
                <stop offset="1" stopColor={gradient.color} stopOpacity="0" />
              </linearGradient>
            ))}
          </defs>
        </motion.svg>
      </div>
    </motion.div>
  );
}

/**
 * Layer 3 — the starfield. Each star gets its own randomised period so the
 * twinkle never falls into a visible collective rhythm.
 */
function Starfield() {
  const twinkles = useMemo(
    () =>
      STARS.map(() => ({
        peak: 0.2 + Math.random() * 0.8,
        duration: 1.6 + Math.random() * 2.8,
        delay: Math.random() * 3,
      })),
    [],
  );

  return (
    <motion.div
      className="absolute -bottom-10 left-1/2 z-0 flex h-full w-full -translate-x-1/2 justify-center"
      initial={{ opacity: 0 }}
      whileInView={{ opacity: 1 }}
      viewport={{ once: true }}
      transition={{ duration: 1.2, ease: 'easeOut', delay: 0.2 }}
    >
      <div className="w-fit">
        <motion.svg
          width="822"
          height="158"
          viewBox="0 0 822 158"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          transition={{ duration: 1.2, ease: 'easeOut', delay: 0.2 }}
        >
          {STARS.map(([cx, cy, r], index) => (
            <motion.circle
              key={`${cx}-${cy}`}
              cx={cx}
              cy={cy}
              r={r}
              fill="white"
              initial={{ opacity: 0.2 }}
              animate={{ opacity: [0.2, twinkles[index].peak, 0.2] }}
              transition={{
                duration: twinkles[index].duration,
                delay: twinkles[index].delay,
                repeat: Infinity,
                ease: 'easeInOut',
              }}
            />
          ))}
        </motion.svg>
      </div>
    </motion.div>
  );
}

/** Layer 4 — the wide light beam falling from above the horizon. */
function LightBeam() {
  return (
    <motion.div
      className="absolute bottom-0 left-1/2 z-5 flex h-full w-full -translate-x-1/2 justify-center"
      initial={{ opacity: 0 }}
      whileInView={{ opacity: 0.4 }}
      viewport={{ once: true }}
      transition={{ duration: 1.6, ease: 'easeOut', delay: 0.1 }}
    >
      <div className="w-fit">
        <svg
          width="1424"
          height="651"
          viewBox="0 0 1424 651"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
        >
          <g filter="url(#filter0_f_2693_2600)" style={{ mixBlendMode: 'plus-lighter' }}>
            <path d="M611.5 51L495 -188H959L849.5 51H611.5Z" fill="#FA9A63" fillOpacity="0.1" />
          </g>
          <g filter="url(#filter1_f_2693_2600)" style={{ mixBlendMode: 'plus-lighter' }}>
            <path d="M611.5 219L495 -188H959L849.5 219H611.5Z" fill="#FFD99F" />
          </g>
          <g filter="url(#filter2_f_2693_2600)" style={{ mixBlendMode: 'plus-lighter' }}>
            <path d="M656.49 43L568 -219H829L768.219 43H656.49Z" fill="#F6B253" fillOpacity="0.8" />
          </g>
          <defs>
            <filter
              id="filter0_f_2693_2600"
              x="-105"
              y="-788"
              width="1664"
              height="1439"
              filterUnits="userSpaceOnUse"
              colorInterpolationFilters="sRGB"
            >
              <feFlood floodOpacity="0" result="BackgroundImageFix" />
              <feBlend
                mode="normal"
                in="SourceGraphic"
                in2="BackgroundImageFix"
                result="shape"
              />
              <feGaussianBlur stdDeviation="300" result="effect1_foregroundBlur_2693_2600" />
            </filter>
            <filter
              id="filter1_f_2693_2600"
              x="95"
              y="-588"
              width="1264"
              height="1207"
              filterUnits="userSpaceOnUse"
              colorInterpolationFilters="sRGB"
            >
              <feFlood floodOpacity="0" result="BackgroundImageFix" />
              <feBlend
                mode="normal"
                in="SourceGraphic"
                in2="BackgroundImageFix"
                result="shape"
              />
              <feGaussianBlur stdDeviation="200" result="effect1_foregroundBlur_2693_2600" />
            </filter>
            <filter
              id="filter2_f_2693_2600"
              x="408"
              y="-379"
              width="581"
              height="582"
              filterUnits="userSpaceOnUse"
              colorInterpolationFilters="sRGB"
            >
              <feFlood floodOpacity="0" result="BackgroundImageFix" />
              <feBlend
                mode="normal"
                in="SourceGraphic"
                in2="BackgroundImageFix"
                result="shape"
              />
              <feGaussianBlur stdDeviation="80" result="effect1_foregroundBlur_2693_2600" />
            </filter>
          </defs>
        </svg>
      </div>
    </motion.div>
  );
}

export function Hero() {
  const layersRef = useRef<HTMLDivElement>(null);
  const [size, setSize] = useState<Size>({ width: 0, height: 0 });

  useEffect(() => {
    const node = layersRef.current;
    if (!node) return;
    const measure = () => {
      const { width, height } = node.getBoundingClientRect();
      setSize({ width, height });
    };
    measure();
    const observer = new ResizeObserver(measure);
    observer.observe(node);
    return () => observer.disconnect();
  }, []);

  return (
    <div className="h-[60vh] w-full p-2 md:h-screen">
      <div className="text-natural-white relative m-0 h-full w-full overflow-hidden rounded-3xl bg-black">
        <div ref={layersRef} className="absolute inset-0 h-full w-full">
          <GridLayer size={size} />
          <HorizonArc />
          <Starfield />
          <LightBeam />
        </div>
        <Container className="relative z-10 flex h-full flex-col justify-between">
          <div className="pt-32 md:pt-42 lg:pt-75">
            <a
              target="_blank"
              className="flex w-fit rounded-full bg-neutral-900 p-1 shadow-lg shadow-black"
              href="https://ui.aceternity.com/"
            >
              <div className="flex items-center gap-1 sm:gap-2">
                <div className="rounded-full bg-neutral-950 px-2 py-1 text-[10px] sm:text-xs">
                  Aceternity UI
                </div>
                <div className="text-natural-white rounded-full pr-2 text-[10px] sm:text-xs">
                  New components every week
                </div>
              </div>
            </a>
            <div className="mt-6 flex flex-col items-start gap-6 md:mt-10 lg:flex-row lg:gap-10">
              <h1 className="text-natural-white -tracking-xl text-3xl font-semibold text-balance sm:text-4xl md:text-5xl lg:text-7xl">
                The best design and development agency in the world.
              </h1>
              <div className="lg:max-w-md">
                <h2 className="text-sm font-medium text-balance text-neutral-300 sm:text-base lg:text-lg">
                  We design and build websites that drive results and help your business grow. No
                  Calls. No BS. Just Results.
                </h2>
                <Button className="mt-6 md:mt-8" avatar="/manu.webp">
                  Chat with Alex
                </Button>
              </div>
            </div>
          </div>
          <div className="relative h-18 sm:h-48 md:h-72">
            <p className="from-natural-white/10 -tracking-xl to-heading/0 bg-linear-to-r bg-clip-text text-transparent absolute -top-10 left-1/2 -translate-x-1/2 text-center text-[100px] font-semibold sm:text-[6rem] md:-top-6 md:mt-10 md:text-[160px] lg:-top-18 lg:text-[300px]">
              Aceternity
            </p>
          </div>
        </Container>
      </div>
    </div>
  );
}
