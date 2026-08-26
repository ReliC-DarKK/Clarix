"use client"
import Link from 'next/link'
import { ArrowRight } from 'lucide-react'
import { ImageComparison } from '@/components/analysis/image-comparison'
import { LandCoverMap } from '@/components/analysis/land-cover-map'
import { Metrics } from '@/components/analysis/metrics'
import { Section } from '@/components/landing/section'
import { LAND_COVER_CLASSES } from '@/lib/clarix/api'

const SAMPLE_IMAGES = {
  input: '/images/tile-input.png',
  bicubic: '/images/tile-bicubic.png',
  clarix: '/images/tile-clarix.png',
  landCover: '/images/landcover-map.png',
}

export function ResultsSection() {
  return (
    <Section
      id="results"
      label="Results"
      title="Three views of the same scene"
      description="Every run returns the recorded input, an interpolated baseline and the model output — side by side, with measured evaluation."
    >
      <ImageComparison images={SAMPLE_IMAGES} scaleFactor={null} />

      <div className="mt-20 border-t border-border pt-12 md:mt-28">
        <p className="label-xs">Quantitative evaluation</p>
        <div className="mt-10">
          <Metrics metrics={{ psnr: null, ssim: null, scaleFactor: null }} />
        </div>
      </div>

      <div className="mt-20 border-t border-border pt-12 md:mt-28">
        <div className="flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
          <h3 className="text-2xl font-semibold uppercase tracking-[0.01em] md:text-4xl">Spatial land-cover map</h3>
          <p className="max-w-md text-sm leading-relaxed text-muted-foreground">
            The sharpened scene, read as surface classes.
          </p>
        </div>
        <div className="mt-10">
          <LandCoverMap src={SAMPLE_IMAGES.landCover} classes={LAND_COVER_CLASSES} reference="Reference scene" />
        </div>
      </div>

      <div className="mt-16 flex flex-col gap-6 border-t border-border pt-10 md:flex-row md:items-center md:justify-between">
        <p className="max-w-lg text-sm leading-relaxed text-muted-foreground">
          Run the full sequence on your own scene — upload, reconstruct, evaluate, map.
        </p>
        <Link
          href="/analysis"
          className="group inline-flex items-center justify-center gap-3 self-start rounded-sm bg-primary px-8 py-4 font-mono text-[0.7rem] uppercase tracking-[0.22em] text-primary-foreground transition-all hover:shadow-[0_0_44px_-8px_var(--primary)] md:self-auto"
        >
          Start Analysis
          <ArrowRight className="size-4 transition-transform group-hover:translate-x-1" />
        </Link>
      </div>
    </Section>
  )
}
