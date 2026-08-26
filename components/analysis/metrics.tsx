import { formatPsnr, formatSsim, isLiveBackend } from '@/lib/clarix/api'
import type { AnalysisMetrics } from '@/lib/clarix/types'

function MetricCell({
  label,
  value,
  unitNote,
  description,
}: {
  label: string
  value: string
  unitNote: string
  description: string
}) {
  return (
    <div className="relative border-t border-border pt-6 md:border-t-0 md:border-l md:pl-8 md:pt-0 md:first:border-l-0 md:first:pl-0">
      <p className="label-xs">{label}</p>
      <p className="mt-4 font-mono text-[clamp(2.4rem,6vw,4.5rem)] font-semibold leading-none tracking-tight text-foreground">
        {value}
      </p>
      <p className="mt-3 font-mono text-[0.62rem] uppercase tracking-[0.24em] text-primary/70">{unitNote}</p>
      <p className="mt-4 max-w-xs text-sm leading-relaxed text-muted-foreground">{description}</p>
    </div>
  )
}

export function Metrics({ metrics }: { metrics: AnalysisMetrics }) {
  return (
    <div>
      <div className="grid gap-8 md:grid-cols-3">
        <MetricCell
          label="PSNR"
          value={formatPsnr(metrics.psnr)}
          unitNote="Decibels"
          description="Peak signal-to-noise ratio between the reconstruction and the reference scene."
        />
        <MetricCell
          label="SSIM"
          value={formatSsim(metrics.ssim)}
          unitNote="0 – 1 index"
          description="Structural similarity — how well shapes, edges and texture are preserved."
        />
        <MetricCell
          label="Scale"
          value={metrics.scaleFactor ? `${metrics.scaleFactor}×` : '—'}
          unitNote="Upscaling factor"
          description="Resolution gain applied by the super-resolution model."
        />
      </div>

      {!isLiveBackend && (
        <p className="mt-10 flex items-start gap-3 border-t border-border pt-5 font-mono text-[0.62rem] uppercase leading-relaxed tracking-[0.18em] text-muted-foreground/80">
          <span className="mt-[3px] size-1.5 shrink-0 rounded-full bg-accent" />
          Metric values are populated by the evaluation service. Awaiting pipeline connection.
        </p>
      )}
    </div>
  )
}
