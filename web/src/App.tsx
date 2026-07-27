import { Navbar } from '@/components/navbar';
import { Hero } from '@/components/hero';
import { LogoWall } from '@/components/logo-wall';
import { EngineeringBento } from '@/components/engineering-bento';
import { Projects } from '@/components/projects';
import { Insights } from '@/components/insights';
import { Scaling } from '@/components/scaling';
import { Comparison } from '@/components/comparison';
import { Pricing } from '@/components/pricing';
import { FoundersDesk } from '@/components/founders-desk';
import { Feedback } from '@/components/feedback';
import { Faq } from '@/components/faq';
import { SiteFooter } from '@/components/site-footer';

export default function App() {
  return (
    <div className="bg-background relative font-sans antialiased">
      {/* Ambient bloom the glass panels refract; purely decorative. */}
      <div className="aurora" aria-hidden="true" />
      <div className="relative z-10">
        <Navbar />
        <section className="flex max-w-screen flex-col items-center justify-center overflow-x-hidden">
          <Hero />
          <LogoWall />
          <EngineeringBento />
          <Projects />
          <Insights />
          <Scaling />
          <Comparison />
          <Pricing />
          <FoundersDesk />
          <Feedback />
          <Faq />
        </section>
        <SiteFooter />
      </div>
    </div>
  );
}
