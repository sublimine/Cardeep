import { IconMenu2 } from '@tabler/icons-react';

import { Button } from '@/components/ui/button';

const NAV_LINKS = [
  { label: 'Work', href: '/work' },
  { label: 'Products', href: '/products' },
  { label: 'Pricing', href: '/pricing' },
  { label: 'Blog', href: '/blog' },
] as const;

/**
 * Top navigation floating over the dark hero. No entrance animation: the only
 * motion is the CSS colour transition on the links and the shared Button hover.
 */
export function Navbar() {
  return (
    <nav className="absolute inset-x-0 top-4 z-50 mx-auto w-full lg:top-4 lg:max-w-[calc(100%-4rem)]">
      <div className="max-w-container mx-auto px-4 lg:px-8">
        <div className="flex h-16 items-center justify-between">
          <div className="flex shrink-0 items-center gap-2 lg:min-w-45">
            <a className="size-8" href="/">
              <img
                alt="Logo"
                loading="lazy"
                width={50}
                height={50}
                decoding="async"
                className="block dark:hidden size-8"
                src="/logo.webp"
              />
              <img
                alt="Logo"
                loading="lazy"
                width={50}
                height={50}
                decoding="async"
                className="hidden dark:block size-8"
                src="/logo-dark.webp"
              />
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
            <Button avatar="/manu.webp">Chat with Alex</Button>
          </div>

          <div className="md:hidden">
            <button className="p-2 text-white/80 hover:text-white">
              <IconMenu2 className="size-6 text-natural-white" />
            </button>
          </div>
        </div>
      </div>
    </nav>
  );
}
