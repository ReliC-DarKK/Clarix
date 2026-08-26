import type { Metadata } from 'next'
import { AnalysisFlow } from '@/components/analysis/analysis-flow'
import { Navigation } from '@/components/navigation'
import { SiteFooter } from '@/components/site-footer'

export const metadata: Metadata = {
  title: 'Analyze Imagery — CLARIX',
  description:
    'Upload a medium-resolution satellite image to generate a super-resolved representation and spatial land-cover map.',
}

export default function AnalysisPage() {
  return (
    <>
      <Navigation />
      <main className="relative min-h-svh overflow-hidden">
        <div aria-hidden className="pointer-events-none absolute inset-0">
          <div className="absolute -top-40 left-1/2 size-[46rem] -translate-x-1/2 rounded-full bg-primary/[0.07] blur-[140px]" />
          <div className="absolute right-0 top-1/3 size-[30rem] rounded-full bg-accent/[0.06] blur-[130px]" />
          <div className="grid-overlay absolute inset-0 opacity-40 [mask-image:radial-gradient(80%_50%_at_50%_0%,black,transparent)]" />
        </div>
        <div className="relative">
          <AnalysisFlow />
        </div>
      </main>
      <SiteFooter />
    </>
  )
}
