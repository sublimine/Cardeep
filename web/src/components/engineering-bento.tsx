import { Container } from '@/components/ui/container';
import { BENTO } from '@/content/site';
import { DesignDevelopmentCard } from '@/components/bento/design-development-card';
import { ProgressTrackingCard } from '@/components/bento/progress-tracking-card';
import { HostingMapCard } from '@/components/bento/hosting-map-card';
import { GoogleSearchCard } from '@/components/bento/google-search-card';
import { ComponentsCard } from '@/components/bento/components-card';

/**
 * Product bento grid, anchored at `#producto` for the navbar link.
 *
 * The 19-column track lets the feature card take 6/19 and the four supporting
 * cards share the remaining 13 on large screens, collapsing to one and then two
 * columns below that. `--box-min-height` keeps the four smaller cards on a
 * common baseline height.
 */
export function EngineeringBento() {
  return (
    <Container id="producto" className="flex flex-col gap-15 py-4">
      <h2 className="text-heading text-left text-4xl font-semibold tracking-tight md:text-5xl">
        {BENTO.heading}
      </h2>
      <div className="grid grid-cols-19 gap-3">
        <DesignDevelopmentCard />
        <div className="col-span-19 grid grid-cols-1 gap-3 md:grid-cols-2 lg:col-span-13 lg:grid-cols-5 [--box-min-height:314px]">
          <ProgressTrackingCard />
          <HostingMapCard />
          <GoogleSearchCard />
          <ComponentsCard />
        </div>
      </div>
    </Container>
  );
}
