import { cn } from '@/lib/utils';

/**
 * The Cardeep mark — the car silhouette enclosed in a rounded triangle, taken
 * from the brand artwork rather than redrawn.
 *
 * It renders as a masked block so it inherits `currentColor`: cobalt on a light
 * surface, white over the hero plate, charcoal in print. One asset, every
 * context, crisp at any size.
 */
export function Logo({ className }: { className?: string }) {
  return <span aria-hidden className={cn('brand-mark inline-block', className)} />;
}

/** Mark plus wordmark, for the footer and anywhere the full lockup fits. */
export function Wordmark({ className }: { className?: string }) {
  return (
    <span className={cn('inline-flex items-center gap-2.5', className)}>
      <Logo className="text-primary size-7" />
      <span className="text-foreground -tracking-lg text-[1.35rem] leading-none font-semibold">
        cardeep
      </span>
    </span>
  );
}
