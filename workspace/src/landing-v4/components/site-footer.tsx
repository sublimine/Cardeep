import { Button } from '@landing/components/ui/button';
import { Logo } from '@landing/components/ui/logo';
import { Container } from '@landing/components/ui/container';
import { BRAND, FOOTER } from '@landing/content/site';

type FooterLink = {
  readonly label: string;
  readonly href: string;
};

type FooterColumn = {
  readonly title: string;
  readonly links: readonly FooterLink[];
};

function LinkColumn({ title, links }: FooterColumn) {
  return (
    <div className="flex flex-col gap-4">
      <h3 className="text-muted-foreground -tracking-sm text-xs leading-5 font-medium">
        {title}
      </h3>
      <ul className="flex flex-col gap-4">
        {links.map((link) => (
          <li key={link.label}>
            <a
              className="text-natural-white -tracking-sm text-sm leading-5 font-medium hover:underline"
              href={link.href}
            >
              {link.label}
            </a>
          </li>
        ))}
      </ul>
    </div>
  );
}

/**
 * Black page footer: glass CTA panel with the giant gradient "Cardeep"
 * watermark, brand block, four link columns, and the copyright bottom bar.
 *
 * No entrance animations here — the target footer only uses CSS hover
 * transitions (link underline, contact link colour, Button hover choreography).
 *
 * Cardeep has no social accounts yet, so the icon row is replaced by the contact
 * address: a live mailto beats three dead profiles.
 */
export function SiteFooter() {
  return (
    <footer className="bg-natural-black relative overflow-hidden">
      <div className="absolute inset-0 -left-128.75">
        <div className="absolute top-0 left-[387.07px] h-293.75 w-[720.16px] rounded-full bg-[#27251F] blur-[287.15px]" />
        <div className="absolute top-[284.85px] left-0 h-[502.50px] w-[488.15px] rounded-full bg-white blur-[215.36px]" />
      </div>
      <Container className="flex flex-col gap-30 pt-20 pb-10">
        {/* Access is requested, not self-served, so the nav's "API" link lands here. */}
        <div
          id="api"
          className="glass-dark relative h-112 overflow-hidden rounded-4xl"
        >
          <div className="-tracking-xl absolute top-51 -left-3.25 justify-start text-[132px] leading-75 font-medium opacity-25 md:text-[240px] lg:text-[300px] bg-[linear-gradient(90deg,#FFFFFF_0%,rgba(52,52,52,0)_100%)] bg-clip-text text-transparent">
            {FOOTER.watermark}
          </div>
          <div className="absolute inset-0 flex h-fit w-full flex-col items-start justify-between px-6 pt-10 md:flex-row md:px-15 md:pt-16">
            {/* `ctaTitle` carries its own line break; honour it instead of guessing a wrap. */}
            <div className="text-natural-white -tracking-lg w-full max-w-135 justify-center text-[32px] font-medium whitespace-pre-line md:text-5xl md:leading-14 lg:text-[56px] lg:leading-16">
              {FOOTER.ctaTitle}
            </div>
            <div className="inline-flex w-16 flex-col items-start justify-start gap-2.5 py-6">
              <a
                aria-label={FOOTER.cta}
                className="bg-natural-white shadow-card-md inline-flex items-center justify-center gap-2.5 self-stretch rounded-xl px-6 py-2"
                href="#precios"
              >
                <svg
                  width="24"
                  height="24"
                  viewBox="0 0 24 24"
                  fill="none"
                  xmlns="http://www.w3.org/2000/svg"
                  className="scale-150"
                >
                  <path
                    d="M18 8L22 12L18 16"
                    stroke="black"
                    strokeWidth="1.5"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  />
                  <path
                    d="M2 12H22"
                    stroke="black"
                    strokeWidth="1.5"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  />
                </svg>
              </a>
            </div>
          </div>
        </div>
        <div className="relative z-10 flex flex-col items-center justify-center gap-18">
          <div className="grid w-full grid-cols-1 gap-15 lg:grid-cols-2 lg:gap-0">
            <div className="flex flex-col gap-4">
              <a className="size-8" href="/" aria-label={BRAND.name}>
                {/* Footer is black, so the light mark. */}
                <Logo tone="light" className="size-8" title={BRAND.name} />
              </a>
              <span className="text-muted-foreground text-sm leading-5">
                {FOOTER.blurb}
              </span>
              <div>
                {/* The accent box reveals the Cardeep mark on hover — no invented portrait. */}
                <Button avatar="/shots/mark.webp">{FOOTER.cta}</Button>
              </div>
            </div>
            <div className="grid grid-cols-2 gap-10 md:grid-cols-4 md:gap-0">
              {FOOTER.columns.map((column) => (
                <LinkColumn
                  key={column.title}
                  title={column.title}
                  links={column.links}
                />
              ))}
            </div>
          </div>
          <div
            id="legal"
            className="flex w-full flex-col justify-between gap-6 md:flex-row md:items-center md:gap-0"
          >
            <div>
              <span className="flex items-center gap-1">
                <svg
                  width="12"
                  height="12"
                  viewBox="0 0 12 12"
                  fill="none"
                  xmlns="http://www.w3.org/2000/svg"
                >
                  <g clipPath="url(#clip0_2623_9646)">
                    <path
                      d="M6 11C8.76142 11 11 8.76142 11 6C11 3.23858 8.76142 1 6 1C3.23858 1 1 3.23858 1 6C1 8.76142 3.23858 11 6 11Z"
                      stroke="#8B8B8B"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                    />
                    <path
                      d="M7.41343 7.415C7.13363 7.69448 6.77726 7.88474 6.38936 7.96173C6.00146 8.03872 5.59944 7.99899 5.23412 7.84755C4.8688 7.69611 4.55657 7.43976 4.33691 7.11091C4.11724 6.78206 4 6.39547 4 6C4 5.60453 4.11724 5.21794 4.33691 4.88909C4.55657 4.56024 4.8688 4.3039 5.23412 4.15245C5.59944 4.00101 6.00146 3.96128 6.38936 4.03827C6.77726 4.11526 7.13363 4.30552 7.41343 4.585"
                      stroke="#8B8B8B"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                    />
                  </g>
                  <defs>
                    <clipPath id="clip0_2623_9646">
                      <rect width="12" height="12" fill="white" />
                    </clipPath>
                  </defs>
                </svg>
                <span className="text-muted-foreground text-xs leading-5 font-medium">
                  {/* The mark to the left already draws the ©; drop the duplicate glyph. */}
                  {FOOTER.legal.replace(/^©\s*/, '')}
                </span>
              </span>
            </div>
            <div className="flex items-center gap-5">
              <a
                className="text-muted-foreground hover:text-natural-white text-xs leading-5 font-medium transition-colors"
                href={`mailto:${BRAND.email}`}
              >
                {BRAND.email}
              </a>
            </div>
          </div>
        </div>
      </Container>
    </footer>
  );
}
