import { Navigation } from '@/components/navigation'
import { SiteFooter } from '@/components/site-footer'
import { AboutSection } from '@/components/landing/about-section'
import { Hero } from '@/components/landing/hero'
import { ResultsSection } from '@/components/landing/results-section'
import { Section } from '@/components/landing/section'
import { TechnologySection } from '@/components/landing/technology-section'
import { Workflow } from '@/components/workflow'

export default function HomePage() {
  return (
    <>
      <Navigation />
      <main>
        <Hero />
        <TechnologySection />

        <Section
          id="workflow"
          label="Workflow"
          title="From one tile to a readable map"
          description="Five stages run in sequence. Each one hands a measurable artifact to the next."
        >
          <div className="max-w-3xl">
            <Workflow />
          </div>
        </Section>

        <ResultsSection />
        <AboutSection />
      </main>
      <SiteFooter />
    </>
  )
}
