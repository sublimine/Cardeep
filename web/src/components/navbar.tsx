import { IconMenu2 } from '@tabler/icons-react';

import { Button } from '@/components/ui/button';
import { Logo } from '@/components/ui/logo';
import { BRAND, NAV_LINKS, PRIMARY_CTA } from '@/content/site';

/**
 * Top navigation floating over the dark hero. No entrance animation: the only
 * motion is the CSS colour transition on the links and the shared Button hover.
 *
 * The bar itself carries no surface — it sits directly on the hero — so no glass
 * utility is applied here.
 */
export function Navbar() {
  return (
    <nav className="absolute inset-x-0 top-4 z-50 mx-auto w-full lg:top-4 lg:max-w-[calc(100%-4rem)]">
      <div className="max-w-container mx-auto px-4 lg:px-8">
        <div className="flex h-16 items-center justify-between">
          <div className="flex shrink-0 items-center gap-2 lg:min-w-45">
            <a className="size-8" href="/" aria-label={BRAND.name}>
              {/* The nav floats over the black hero, so the mark is always the light one. */}
              <Logo tone="light" className="size-8" title={BRAND.name} />
            </a>
          </div>

          <div className="hidden md:block">
            <div className="ml-10 flex items-baseline space-x-8">
              {NAV_LINKS.map((link) => (
                <a
                  key={link.href}
                  className="px-3 py-2 text-sm font-medium transition-colors duration-200 text-natural-white/80 hover:text-natural-white"
                  href={link.href}
                >
                  {link.label}
                </a>
              ))}
            </div>
          </div>

          <div className="hidden md:block">
            {/* The accent box reveals the Cardeep mark on hover, where the reference
                template revealed a portrait. Same motion, no invented person. */}
            <Button avatar="/shots/mark.webp">{PRIMARY_CTA}</Button>
          </div>

          <div className="md:hidden">
            <button aria-label="Abrir menú" className="p-2 text-white/80 hover:text-white">
              <IconMenu2 className="size-6 text-natural-white" />
            </button>
          </div>
        </div>
      </div>
    </nav>
  );
}
