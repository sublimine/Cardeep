import { useCallback, useEffect, useMemo, useRef, useState, type ReactNode } from 'react';
import { useReducedMotion } from 'framer-motion';

import { cn } from '@landing/lib/utils';

/* -------------------------------------------------------------------------- */
/*                                  Geometry                                  */
/* -------------------------------------------------------------------------- */

/**
 * The golden angle, 2*pi*(1 - 1/phi) radians.
 *
 * Advancing longitude by this much per point is what makes a Fibonacci lattice
 * look scattered rather than striped. Any rational fraction of a turn closes back
 * on itself after a few steps and the eye instantly reads the seam as a row; the
 * golden angle is the "most irrational" number available, so it never closes and
 * no two neighbours ever line up.
 */
const GOLDEN_ANGLE = Math.PI * (3 - Math.sqrt(5));

/**
 * Camera distance, in sphere radii.
 *
 * This is the only number that decides how strongly the sphere reads as a sphere.
 * At 5 radii the perspective divisor runs 1.25 at the near pole down to 0.833 at
 * the far one — a 1.5x size difference from depth alone, before the extra dimming
 * below. Push it lower and the near marks balloon over their neighbours (at 4 the
 * nearest chip rendered half again as wide as the ones beside it and collided with
 * them); push it higher and the projection flattens into a ring, which is exactly
 * the failure the flat CSS radar this replaces was guilty of.
 */
const CAMERA = 5;

/**
 * Sphere radius as a fraction of the (square) box.
 *
 * Not 0.5: a mark sitting on the limb is centred on the radius and sticks out by
 * half its own width, so the sphere has to leave that half-width of margin or the
 * marks at three and nine o'clock get clipped by the card.
 *
 * This is therefore a contract with the caller — the 11% left over per side has to
 * be at least half the widest item. The current consumer sizes its chips against
 * this number; see `CHIP_W` in the bento feature card.
 */
const RADIUS_RATIO = 0.39;

/* --------------------------------- motion --------------------------------- */

/** Idle drift, rad/s. One revolution takes about 35s — an instrument, not a spinner. */
const IDLE_YAW = 0.18;

/** Drag gearing, radians per pixel. ~0.011 puts a half-turn in one sphere-width of travel. */
const DRAG_YAW = 0.011;
const DRAG_PITCH = 0.008;

/** Pitch is clamped so the lattice never tips far enough to read as upside down. */
const MAX_PITCH = 0.6;

/** Ceiling on fling speed, rad/s, so a fast flick cannot turn the marks into a smear. */
const MAX_SPIN = 7;

/**
 * Time constant of the release. Angular velocity relaxes TOWARD the idle rate
 * rather than toward zero, so a fling bleeds off into the ambient drift instead of
 * stopping dead and then suspiciously starting again.
 */
const RELAX_TAU = 0.85;

/** A much harder brake, used while a mark is hovered so it stops under the cursor. */
const HOVER_BRAKE_TAU = 0.25;

/** Below this angular speed (rad/s) nothing perceptible is happening. */
const REST_EPSILON = 0.002;

/* ---------------------------------- depth --------------------------------- */

/** Extra shrink applied at the far pole, on top of perspective. */
const FAR_SCALE = 0.82;
/** Opacity at the far pole. Low enough that the back never competes for reading. */
const FAR_OPACITY = 0.13;
/** Gamma on the opacity ramp: <1 keeps the limb readable instead of half-faded. */
const OPACITY_GAMMA = 0.85;
/** Lift given to the mark under the cursor. */
const HOVER_SCALE = 1.12;

/**
 * Paint order. Items span 1..201 by depth, so the core at 101 sits exactly on the
 * z = 0 plane: near marks pass in front of it, far marks behind. That single
 * detail is most of why the thing reads as solid.
 */
const DEPTH_LAYERS = 200;
const CORE_Z = 1 + DEPTH_LAYERS / 2;

/**
 * How many turns the backdrop makes per turn of the sphere.
 *
 * The backdrop is geared UP rather than run on its own animation, and that is a
 * deliberate design decision: two things moving independently read as two
 * unrelated animations, whereas a backdrop driven by the same yaw reads as one
 * instrument answering one hand. Flinging the sphere visibly spins up the sweep.
 */
const BACKDROP_GEAR = 4;

type Point = { x: number; y: number; z: number };

/**
 * Evenly distributed points on the unit sphere.
 *
 * Latitude is stepped linearly in y (equal-area bands, which is what keeps the
 * poles from bunching) while longitude advances by the golden angle.
 */
function fibonacciLattice(count: number): Point[] {
  return Array.from({ length: count }, (_, i) => {
    const y = 1 - (2 * i + 1) / count;
    const ring = Math.sqrt(Math.max(0, 1 - y * y));
    const theta = i * GOLDEN_ANGLE;
    return { x: Math.cos(theta) * ring, y, z: Math.sin(theta) * ring };
  });
}

function clamp(value: number, min: number, max: number) {
  return value < min ? min : value > max ? max : value;
}

/* -------------------------------------------------------------------------- */
/*                                   Sphere                                   */
/* -------------------------------------------------------------------------- */

export type SphereItem = {
  /** Stable React key. Repeated marks need distinct keys, so this is the slot id. */
  key: string;
  /** Surfaced through `onHoverChange` when this mark is pointed at. */
  name: string;
  node: ReactNode;
};

type LogoSphereProps = {
  items: readonly SphereItem[];
  /**
   * Painted behind the marks and yawed with them (see `BACKDROP_GEAR`). Chrome
   * that belongs to the instrument goes here; anything static can go around it.
   */
  backdrop?: ReactNode;
  /** Painted at the centre, on the z = 0 plane, so the sphere occludes it correctly. */
  core?: ReactNode;
  /** Fired with the hovered mark's name, or null when the pointer leaves or a drag starts. */
  onHoverChange?: (name: string | null) => void;
  /** Required: the marks themselves are aria-hidden, so this is the only description. */
  label: string;
  className?: string;
};

/**
 * A draggable sphere of DOM nodes.
 *
 * WHY THIS IS NOT THREE.JS, and the repo does ship @react-three/fiber and drei so
 * it was a genuine choice:
 *
 *  1. The marks are SVG wordmarks. In WebGL they would have to become textures,
 *     and rasterising an SVG to a texture is exactly where these particular files
 *     fall apart — motor-es.svg declares `width="100%"`, which gives an image
 *     loader no intrinsic size to rasterise at. As DOM `<img>` they stay vector
 *     and stay crisp at every scale the sphere puts them through.
 *  2. It is one tile of a bento grid. three + drei is several hundred kilobytes
 *     and a live WebGL context for a surface a visitor may never scroll to.
 *  3. Projecting by hand gives per-mark control of opacity, scale and paint order
 *     as direct functions of depth. That is the depth cue, and in WebGL it would
 *     have to be fought back out of the material system.
 *
 * So: the 3D maths runs in JS, the result is written as 2D transforms. No
 * `preserve-3d` either — that would billboard the marks edge-on as the container
 * turned, and it interacts badly with filters and stacking. Positions are computed,
 * projected, and written straight to `style.transform`.
 *
 * Nothing here re-renders React per frame. The loop writes to nodes it holds by
 * ref; the only React state is the hovered name (lifted to the parent) and the
 * measured radius.
 */
export function LogoSphere({
  items,
  backdrop,
  core,
  onHoverChange,
  label,
  className,
}: LogoSphereProps) {
  const prefersReduced = useReducedMotion();
  /** `useReducedMotion` is `boolean | null` until it has read the media query. */
  const still = prefersReduced === true;

  const boxRef = useRef<HTMLDivElement>(null);
  const backdropRef = useRef<HTMLDivElement>(null);
  const nodeRefs = useRef<(HTMLDivElement | null)[]>([]);
  const zCache = useRef<number[]>([]);

  /** Which slot is under the cursor, as a ref so the paint loop can read it for free. */
  const hoverRef = useRef(-1);
  const pointerRef = useRef({ x: 0, y: 0, t: 0 });
  /** Lets the pointer handlers restart a parked animation loop. */
  const wakeRef = useRef<() => void>(() => {});

  /**
   * Opening attitude. A little yaw so no mark starts dead centre, and a little
   * pitch so the sphere is seen slightly from above — an object on a table rather
   * than a diagram drawn face on.
   */
  const motionRef = useRef({ yaw: 0.6, pitch: 0.22, yawVel: 0, pitchVel: 0, dragging: false });

  const [radius, setRadius] = useState(0);
  const [grabbing, setGrabbing] = useState(false);

  const lattice = useMemo(() => fibonacciLattice(items.length), [items.length]);

  /**
   * One frame of projection.
   *
   * Rotate each lattice point by yaw about Y then pitch about X, divide by depth
   * for perspective, and write the result. Screen Y is negated because the lattice
   * counts y upward and the viewport counts it downward.
   */
  const paint = useCallback(() => {
    const { yaw, pitch } = motionRef.current;
    const cosY = Math.cos(yaw);
    const sinY = Math.sin(yaw);
    const cosP = Math.cos(pitch);
    const sinP = Math.sin(pitch);
    const hovered = hoverRef.current;

    for (let i = 0; i < lattice.length; i += 1) {
      const node = nodeRefs.current[i];
      if (!node) continue;

      const p = lattice[i];
      const x1 = p.x * cosY + p.z * sinY;
      const z1 = p.z * cosY - p.x * sinY;
      const y2 = p.y * cosP - z1 * sinP;
      const z2 = p.y * sinP + z1 * cosP;

      const perspective = CAMERA / (CAMERA - z2);
      /** Depth as 0 (far pole) to 1 (near pole). */
      const t = (z2 + 1) / 2;
      const lit = i === hovered;

      const scale = perspective * (FAR_SCALE + (1 - FAR_SCALE) * t) * (lit ? HOVER_SCALE : 1);
      const x = x1 * radius * perspective;
      const y = -y2 * radius * perspective;

      node.style.transform = `translate3d(${x.toFixed(2)}px, ${y.toFixed(2)}px, 0) translate(-50%, -50%) scale(${scale.toFixed(3)})`;
      node.style.opacity = lit
        ? '1'
        : (FAR_OPACITY + (1 - FAR_OPACITY) * Math.pow(t, OPACITY_GAMMA)).toFixed(3);

      /* z-index churn forces a stacking recalculation, so only write it when the
       * integer actually moved. */
      const depth = 1 + Math.round(t * DEPTH_LAYERS);
      if (zCache.current[i] !== depth) {
        zCache.current[i] = depth;
        node.style.zIndex = String(depth);
      }
    }

    const plate = backdropRef.current;
    if (plate) plate.style.transform = `rotate(${(yaw * BACKDROP_GEAR).toFixed(4)}rad)`;
  }, [lattice, radius]);

  /** Measure the box so the radius follows the card instead of a hardcoded width. */
  useEffect(() => {
    const box = boxRef.current;
    if (!box) return;
    const observer = new ResizeObserver(([entry]) => {
      setRadius(entry.contentRect.width * RADIUS_RATIO);
    });
    observer.observe(box);
    return () => observer.disconnect();
  }, []);

  /**
   * The animation loop.
   *
   * It parks itself whenever there is provably nothing to do — off screen, or at
   * rest with no idle drift (which is the reduced-motion case) — and the pointer
   * and keyboard handlers wake it through `wakeRef`. A landing page should not
   * hold a rAF open for a tile nobody is looking at.
   */
  useEffect(() => {
    const box = boxRef.current;
    if (!box || radius === 0) return;

    const idle = still ? 0 : IDLE_YAW;
    let frameId = 0;
    let parked = false;
    let visible = true;
    let last = performance.now();

    const frame = (now: number) => {
      /* Clamped at BOTH ends.
       *
       * The ceiling stops a backgrounded tab resuming with a delta of several
       * seconds and teleporting the sphere through a full turn on its first frame
       * back. The floor matters for a subtler reason: `last` is seeded from
       * `performance.now()`, while `now` is the frame's own start timestamp, and a
       * frame that began fractionally BEFORE that call yields a negative delta.
       * Unclamped that integrates backwards, so the sphere would twitch the wrong
       * way on the first frame after every wake. */
      const dt = Math.min(Math.max((now - last) / 1000, 0), 0.05);
      last = now;

      const m = motionRef.current;
      const hovering = hoverRef.current >= 0;

      if (!m.dragging) {
        const target = hovering ? 0 : idle;
        const tau = hovering ? HOVER_BRAKE_TAU : RELAX_TAU;
        /* Exponential relaxation on dt, not a per-frame multiplier: the same
         * gesture must decay identically at 60Hz and at 144Hz. */
        const k = still ? 1 : 1 - Math.exp(-dt / tau);
        m.yawVel += (target - m.yawVel) * k;
        m.pitchVel += (0 - m.pitchVel) * k;
        m.yaw += m.yawVel * dt;

        const nextPitch = clamp(m.pitch + m.pitchVel * dt, -MAX_PITCH, MAX_PITCH);
        if (nextPitch === m.pitch) m.pitchVel = 0;
        m.pitch = nextPitch;
      }

      paint();

      const settled =
        !m.dragging &&
        Math.abs(m.yawVel) < REST_EPSILON &&
        Math.abs(m.pitchVel) < REST_EPSILON &&
        (idle === 0 || hovering);

      if (!visible || settled) {
        parked = true;
        return;
      }
      frameId = requestAnimationFrame(frame);
    };

    const wake = () => {
      if (!parked) return;
      parked = false;
      last = performance.now();
      frameId = requestAnimationFrame(frame);
    };
    wakeRef.current = wake;

    const observer = new IntersectionObserver(
      ([entry]) => {
        visible = entry.isIntersecting;
        if (visible) wake();
      },
      { threshold: 0 },
    );
    observer.observe(box);

    frameId = requestAnimationFrame(frame);
    return () => {
      cancelAnimationFrame(frameId);
      observer.disconnect();
      wakeRef.current = () => {};
    };
  }, [radius, still, paint]);

  const setHover = useCallback(
    (index: number, name: string | null) => {
      hoverRef.current = index;
      onHoverChange?.(name);
      /* Paint once directly: under reduced motion the loop is parked, and the
       * hover lift has to land anyway. */
      paint();
      wakeRef.current();
    },
    [onHoverChange, paint],
  );

  const handlePointerDown = (event: React.PointerEvent<HTMLDivElement>) => {
    const box = boxRef.current;
    if (!box) return;
    box.setPointerCapture(event.pointerId);

    const m = motionRef.current;
    m.dragging = true;
    m.yawVel = 0;
    m.pitchVel = 0;
    pointerRef.current = { x: event.clientX, y: event.clientY, t: performance.now() };

    /* Grabbing is not inspecting: drop the readout back to its hint. Pointer
     * capture also stops the marks' enter/leave firing for the whole drag, which
     * is the behaviour we want and gets it for free. */
    setHover(-1, null);
    setGrabbing(true);
    wakeRef.current();
  };

  const handlePointerMove = (event: React.PointerEvent<HTMLDivElement>) => {
    const m = motionRef.current;
    if (!m.dragging) return;

    const previous = pointerRef.current;
    const now = performance.now();
    /* Floor the interval: coalesced pointer events can arrive with dt = 0, and
     * dividing by that launches the sphere to infinity on release. */
    const dt = Math.max((now - previous.t) / 1000, 1 / 240);
    const dYaw = (event.clientX - previous.x) * DRAG_YAW;
    const dPitch = (event.clientY - previous.y) * DRAG_PITCH;

    m.yaw += dYaw;
    const nextPitch = clamp(m.pitch + dPitch, -MAX_PITCH, MAX_PITCH);
    const clamped = nextPitch !== m.pitch + dPitch;
    m.pitch = nextPitch;

    /* Velocity is smoothed, so one jittery sample at the moment of release cannot
     * decide how the whole fling feels. */
    m.yawVel = m.yawVel * 0.72 + clamp(dYaw / dt, -MAX_SPIN, MAX_SPIN) * 0.28;
    m.pitchVel = clamped
      ? 0
      : m.pitchVel * 0.72 + clamp(dPitch / dt, -MAX_SPIN, MAX_SPIN) * 0.28;

    pointerRef.current = { x: event.clientX, y: event.clientY, t: now };
  };

  const endDrag = (event: React.PointerEvent<HTMLDivElement>) => {
    const m = motionRef.current;
    if (!m.dragging) return;
    m.dragging = false;
    /* Reduced motion keeps the drag but refuses the coast: the sphere stops where
     * the hand left it. */
    if (still) {
      m.yawVel = 0;
      m.pitchVel = 0;
    }
    const box = boxRef.current;
    if (box?.hasPointerCapture(event.pointerId)) box.releasePointerCapture(event.pointerId);
    setGrabbing(false);
    wakeRef.current();
  };

  /** Arrow keys are the keyboard equivalent of the drag; Shift coarsens the step. */
  const handleKeyDown = (event: React.KeyboardEvent<HTMLDivElement>) => {
    const step = event.shiftKey ? 0.35 : 0.14;
    const m = motionRef.current;

    switch (event.key) {
      case 'ArrowLeft':
        m.yaw -= step;
        break;
      case 'ArrowRight':
        m.yaw += step;
        break;
      case 'ArrowUp':
        m.pitch = clamp(m.pitch - step, -MAX_PITCH, MAX_PITCH);
        break;
      case 'ArrowDown':
        m.pitch = clamp(m.pitch + step, -MAX_PITCH, MAX_PITCH);
        break;
      default:
        return;
    }

    event.preventDefault();
    paint();
    wakeRef.current();
  };

  return (
    <div
      ref={boxRef}
      role="group"
      aria-label={label}
      tabIndex={0}
      className={cn(
        'relative aspect-square w-full rounded-full select-none',
        'focus-visible:ring-brand/50 focus-visible:outline-none focus-visible:ring-1',
        grabbing ? 'cursor-grabbing' : 'cursor-grab',
        className,
      )}
      /* `pan-y`, not `none`: yaw is the interaction that matters and it is
       * horizontal, so surrendering the vertical axis keeps the page scrollable
       * through the sphere on a phone. Trapping a reader's scroll inside a
       * decorative tile would be a worse bug than losing touch pitch.
       *
       * Inline rather than `touch-pan-y` deliberately. This is behaviour, not
       * decoration, and the landing's utilities come from a stylesheet compiled by
       * a separate build step; a class that has not been regenerated yet would
       * fail silently and break touch dragging with nothing on screen to show for
       * it. An inline declaration cannot be out of date. */
      style={{ touchAction: 'pan-y' }}
      onPointerDown={handlePointerDown}
      onPointerMove={handlePointerMove}
      onPointerUp={endDrag}
      onPointerCancel={endDrag}
      onKeyDown={handleKeyDown}
    >
      {backdrop ? (
        <div ref={backdropRef} aria-hidden className="pointer-events-none absolute inset-0 z-0">
          {backdrop}
        </div>
      ) : null}

      {core ? (
        <div
          aria-hidden
          className="pointer-events-none absolute top-1/2 left-1/2"
          /* Centred with an inline transform rather than `-translate-x-1/2`.
           * That utility is the one class this app's two Tailwind majors express
           * differently — v3 writes it into `transform`, v4 into the standalone
           * `translate` property — so both can apply and shift the element twice.
           * `tools/build-landing-css.mjs` emits a guard for exactly this, but an
           * inline transform sidesteps the hazard instead of depending on the
           * guard having been regenerated. */
          style={{ zIndex: CORE_Z, transform: 'translate(-50%, -50%)' }}
        >
          {core}
        </div>
      ) : null}

      {items.map((item, index) => (
        <div
          key={item.key}
          ref={(node) => {
            nodeRefs.current[index] = node;
          }}
          aria-hidden
          className="absolute top-1/2 left-1/2 will-change-transform"
          onPointerEnter={() => setHover(index, item.name)}
          onPointerLeave={() => setHover(-1, null)}
        >
          {item.node}
        </div>
      ))}
    </div>
  );
}
