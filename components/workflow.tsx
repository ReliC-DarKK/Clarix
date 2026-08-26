"use client"
import { UploadCloud, SlidersHorizontal, Sparkles, Gauge, Map as MapIcon } from 'lucide-react'

const STEPS = [
  {
    id: '01',
    title: 'Upload',
    icon: UploadCloud,
    description: 'A medium-resolution scene enters the pipeline as a PNG or JPEG tile.',
  },
  {
    id: '02',
    title: 'Preprocess',
    icon: SlidersHorizontal,
    description: 'Values are normalised and the tile is aligned to a consistent grid.',
  },
  {
    id: '03',
    title: 'AI Super-Resolution',
    icon: Sparkles,
    description: 'A trained model reconstructs fine detail the sensor could not record.',
  },
  {
    id: '04',
    title: 'Evaluation',
    icon: Gauge,
    description: 'The result is measured with PSNR and SSIM against a bicubic baseline.',
  },
  {
    id: '05',
    title: 'Spatial Mapping',
    icon: MapIcon,
    description: 'The sharpened scene is segmented into land-cover classes.',
  },
]

export function Workflow() {
  return (
    <ol className="relative">
      {STEPS.map((step, index) => {
        const Icon = step.icon
        const isLast = index === STEPS.length - 1
        return (
          <li key={step.id} className="group relative grid grid-cols-[auto_1fr] gap-6 md:gap-10">
            {/* rail */}
            <div className="relative flex flex-col items-center">
              <span className="flex size-12 items-center justify-center rounded-full border border-border bg-card/60 text-muted-foreground transition-colors duration-500 group-hover:border-primary/60 group-hover:text-primary md:size-14">
                <Icon className="size-5" />
              </span>
              {!isLast && (
                <span aria-hidden className="relative w-px flex-1 overflow-hidden bg-border">
                  <span
                    className="animate-pulse-line absolute inset-x-0 top-0 h-full bg-gradient-to-b from-primary/70 via-primary/20 to-transparent"
                    style={{ animationDelay: `${index * 0.35}s` }}
                  />
                </span>
              )}
            </div>

            <div className={`pt-2 ${isLast ? 'pb-0' : 'pb-12 md:pb-16'}`}>
              <div className="flex items-baseline gap-4">
                <span className="font-mono text-[0.65rem] tracking-[0.28em] text-primary/70">{step.id}</span>
                <h3 className="text-xl font-semibold uppercase tracking-[0.02em] md:text-3xl">{step.title}</h3>
              </div>
              <p className="mt-3 max-w-xl text-sm leading-relaxed text-muted-foreground md:text-base">
                {step.description}
              </p>
            </div>
          </li>
        )
      })}
    </ol>
  )
}
