'use client'

import { RotateCcw } from 'lucide-react'
import { ImageComparison } from '@/components/analysis/image-comparison'
import { LandCoverMap } from '@/components/analysis/land-cover-map'
import { Metrics } from '@/components/analysis/metrics'
import { formatBytes } from '@/lib/clarix/api'
import type { AnalysisResult } from '@/lib/clarix/types'

export function Results({ result, onRestart }: { result: AnalysisResult; onRestart: () => void }) {
  return (
    <div className="animate-rise">
      <header className="flex flex-col gap-8 border-b border-border pb-10 md:flex-row md:items-end md:justify-between">
        <div>
          <div className="flex items-center gap-4">
            <span className="h-px w-10 bg-primary/60" />
            <span className="label-xs text-primary/80">Run {result.jobId}</span>
          </div>
          <h1 className="mt-7 text-[clamp(2.2rem,7vw,5rem)] font-bold uppercase leading-[0.95] tracking-[-0.02em] text-balance">
            Analysis complete
          </h1>
          <p className="mt-5 max-w-xl text-sm leading-relaxed text-muted-foreground md:text-base">
            {result.source.filename} · {result.source.width} × {result.source.height} px ·{' '}
            {formatBytes(result.source.size)}
          </p>
        </div>

        <button
          type="button"
          onClick={onRestart}
          className="inline-flex shrink-0 items-center justify-center gap-3 self-start rounded-sm border border-primary/50 bg-primary/10 px-7 py-4 font-mono text-[0.7rem] uppercase tracking-[0.2em] text-primary transition-colors hover:bg-primary hover:text-primary-foreground md:self-auto"
        >
          <RotateCcw className="size-3.5" />
          New Analysis
        </button>
      </header>

      <section aria-labelledby="comparison-heading" className="pt-16 md:pt-24">
        <div className="flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
          <h2 id="comparison-heading" className="text-2xl font-semibold uppercase tracking-[0.01em] md:text-4xl">
            Reconstruction comparison
          </h2>
          <p className="max-w-md text-sm leading-relaxed text-muted-foreground">
            The same scene shown as recorded, as interpolated, and as reconstructed by the model.
          </p>
        </div>
        <div className="mt-10">
          <ImageComparison images={result.images} scaleFactor={result.metrics.scaleFactor} />
        </div>
      </section>

      <section aria-labelledby="metrics-heading" className="pt-20 md:pt-28">
        <p className="label-xs">Quantitative evaluation</p>
        <h2 id="metrics-heading" className="sr-only">
          Evaluation metrics
        </h2>
        <div className="mt-10">
          <Metrics metrics={result.metrics} />
        </div>
      </section>

      <section aria-labelledby="map-heading" className="pt-20 md:pt-28">
        <div className="flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
          <h2 id="map-heading" className="text-2xl font-semibold uppercase tracking-[0.01em] md:text-4xl">
            Spatial land-cover map
          </h2>
          <p className="max-w-md text-sm leading-relaxed text-muted-foreground">
            Land-cover classes segmented from the super-resolved scene.
          </p>
        </div>
        <div className="mt-10">
          <LandCoverMap src={result.images.landCover} classes={result.landCover} reference={result.jobId} />
        </div>
      </section>
    </div>
  )
}
