import Image from 'next/image'
import type { LandCoverClass } from '@/lib/clarix/types'

interface LandCoverMapProps {
  src: string
  classes: LandCoverClass[]
  /** Optional identifier shown in the panel header, e.g. the job id. */
  reference?: string
}

export function LandCoverMap({ src, classes, reference }: LandCoverMapProps) {
  return (
    <div className="grid gap-6 lg:grid-cols-[1fr_260px] lg:gap-10">
      <div className="relative overflow-hidden rounded-sm border border-border bg-card/40">
        <div className="flex items-center justify-between gap-4 border-b border-border px-4 py-3">
          <span className="font-mono text-[0.68rem] uppercase tracking-[0.24em] text-foreground">
            Classified raster
          </span>
          <span className="font-mono text-[0.6rem] uppercase tracking-[0.2em] text-muted-foreground/70">
            {reference ?? 'Nadir · Natural color'}
          </span>
        </div>
        <div className="relative aspect-[16/10]">
          <Image
            src={src || '/placeholder.svg'}
            alt="Land-cover classification map derived from the super-resolved scene"
            fill
            sizes="(max-width: 1024px) 100vw, 70vw"
            className="object-cover"
          />
          <div aria-hidden className="grid-overlay pointer-events-none absolute inset-0 opacity-50" />
          <div
            aria-hidden
            className="pointer-events-none absolute inset-0 ring-1 ring-inset ring-primary/10"
          />
          {/* corner ticks */}
          {[
            'left-3 top-3 border-l border-t',
            'right-3 top-3 border-r border-t',
            'left-3 bottom-3 border-l border-b',
            'right-3 bottom-3 border-r border-b',
          ].map((pos) => (
            <span key={pos} aria-hidden className={`pointer-events-none absolute size-4 border-primary/50 ${pos}`} />
          ))}
        </div>
      </div>

      <div className="flex flex-col justify-between gap-8">
        <div>
          <p className="label-xs">Legend</p>
          <ul className="mt-5 flex flex-col gap-4">
            {classes.map((item) => (
              <li key={item.id} className="flex items-center justify-between gap-4 border-b border-border pb-3">
                <span className="flex items-center gap-3">
                  <span
                    aria-hidden
                    className="size-3 rounded-[2px]"
                    style={{ backgroundColor: item.color }}
                  />
                  <span className="text-sm text-foreground">{item.label}</span>
                </span>
                <span className="font-mono text-[0.65rem] tracking-[0.16em] text-muted-foreground">
                  {item.share === null ? '—' : `${Math.round(item.share * 100)}%`}
                </span>
              </li>
            ))}
          </ul>
        </div>

        <p className="text-xs leading-relaxed text-muted-foreground">
          Class shares are reported by the segmentation service once the pipeline is connected.
        </p>
      </div>
    </div>
  )
}
