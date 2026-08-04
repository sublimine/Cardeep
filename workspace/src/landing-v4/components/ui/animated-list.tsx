import {
  Children,
  useEffect,
  useMemo,
  useState,
  type ReactElement,
  type ReactNode,
} from 'react';
import { AnimatePresence, motion, useReducedMotion } from 'framer-motion';

/**
 * A feed that admits one item at a time, newest on top.
 *
 * WHY THIS IS NOT THE REFERENCE IMPLEMENTATION. The pattern this is adapted from
 * renders `children.slice(0, index + 1).reverse()`, so the rendered list GROWS by
 * one on every tick until it wraps. That is fine in a page-height demo and wrong
 * in a bento tile: this one lives inside a 314px card, so an unbounded list would
 * push its own oldest rows straight through the bottom edge and force the card to
 * either clip mid-row or scroll. Here the window is fixed — `visibleCount` items
 * are on screen at any moment, the newest enters at the top and the oldest leaves
 * from the bottom — which is also what a real notification feed does.
 *
 * The modulo walk backwards from `index` is what makes the feed endless without
 * duplicating the data: the source list is a ring, not a queue.
 */
interface AnimatedListProps {
  children: ReactNode;
  className?: string;
  /** Milliseconds one item spends before the next arrives. */
  delay?: number;
  /** How many items stay on screen at once. */
  visibleCount?: number;
}

export function AnimatedList({
  children,
  className,
  delay = 2600,
  visibleCount = 4,
}: AnimatedListProps) {
  const items = useMemo(() => Children.toArray(children), [children]);
  const reduced = useReducedMotion();
  const [index, setIndex] = useState(visibleCount - 1);

  useEffect(() => {
    // A feed that advances on its own is motion the user cannot opt out of by
    // not scrolling, so reduced-motion stops the clock rather than just easing
    // the transition: the card settles on a full, readable window and holds.
    if (reduced || items.length === 0) return;
    const id = setInterval(
      () => setIndex((current) => (current + 1) % items.length),
      delay,
    );
    return () => clearInterval(id);
  }, [items.length, delay, reduced]);

  const visible = useMemo(() => {
    const size = Math.min(visibleCount, items.length);
    return Array.from(
      { length: size },
      (_, step) => items[(index - step + items.length * 2) % items.length],
    );
  }, [index, items, visibleCount]);

  return (
    <div className={className}>
      <AnimatePresence initial={false}>
        {visible.map((item) => (
          <AnimatedListItem key={(item as ReactElement).key}>
            {item}
          </AnimatedListItem>
        ))}
      </AnimatePresence>
    </div>
  );
}

/**
 * One row's arrival and departure.
 *
 * `layout` is what makes the rows below slide down to make room instead of
 * jumping — framer-motion animates the reflow, so only transform and opacity are
 * ever written and the whole feed stays on the compositor.
 */
function AnimatedListItem({ children }: { children: ReactNode }) {
  const reduced = useReducedMotion();

  if (reduced) return <div className="w-full">{children}</div>;

  return (
    <motion.div
      layout
      initial={{ opacity: 0, scale: 0.94, y: -12 }}
      animate={{ opacity: 1, scale: 1, y: 0 }}
      exit={{ opacity: 0, scale: 0.96 }}
      transition={{ type: 'spring', stiffness: 350, damping: 40 }}
      className="w-full"
    >
      {children}
    </motion.div>
  );
}
