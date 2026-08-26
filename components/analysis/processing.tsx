'use client'

import { Check, Loader2 } from 'lucide-react'
import { Starfield } from '@/components/starfield'
import { PIPELINE_STAGES, type PipelineStageId, type StageState } from '@/lib/clarix/types'

interface ProcessingProps {
  activeStage: PipelineStageId
  /** Latest technical status line reported by the pipeline. */
  status?: string
  filename?: string
  error?: string | null
  onCancel?: () => void
}

function stateFor(index: number, activeIndex: number): StageState {
  if (index < activeIndex) return 'complete'
  if (index === activeIndex) return 'active'
  return 'pending'
}

export function Processing({ activeStage, status, filename, error, onCancel }: ProcessingProps) {
  const activeIndex = PIPELINE_STAGES.findIndex((stage) => stage.id === activeStage)

  return (
    <section className="relative flex min-h-[70svh] items-center overflow-hidden">
      <div aria-hidden className="absolute inset-0">
        <div className="absolute left-1/2 top-1/2 size-[40rem] -translate-x-1/2 -translate-y-1/2 rounded-full bg-primary/10 blur-[130px]" />
        <div className="grid-overlay absolute inset-0 opacity-60 [mask-image:radial-gradient(70%_60%_at_50%_50%,black,transparent)]" />
        <div className="absolute inset-0">
          <Starfield density={0.00008} />
        </div>
      </div>

      <div className="relative mx-auto w-full max-w-[1100px] px-5 py-24 md:px-10">
        <div className="flex items-center gap-4">
          <span className="h-px w-10 bg-primary/60" />
          <span className="label-xs text-primary/80">Pipeline active</span>
        </div>

        <h1 className="mt-8 text-[clamp(2rem,6vw,4.25rem)] font-bold uppercase leading-[0.95] tracking-[-0.02em] text-balance">
          Processing scene
        </h1>
        {filename && (
          <p className="mt-4 truncate font-mono text-xs uppercase tracking-[0.2em] text-muted-foreground">
            {filename}
          </p>
        )}

        {/* indeterminate progress — real percentages come from the backend */}
        <div className="relative mt-12 h-px w-full overflow-hidden bg-border">
          {!error && (
            <div className="animate-sweep absolute inset-y-0 left-0 w-1/3 bg-gradient-to-r from-transparent via-primary to-transparent" />
          )}
        </div>

        <ol className="mt-12 grid gap-px overflow-hidden rounded-sm border border-border bg-border sm:grid-cols-2 lg:grid-cols-4">
          {PIPELINE_STAGES.map((stage, index) => {
            const state = stateFor(index, activeIndex)
            return (
              <li
                key={stage.id}
                aria-current={state === 'active' ? 'step' : undefined}
                className={`flex flex-col justify-between gap-6 bg-background px-5 py-6 transition-colors duration-500 ${
                  state === 'active' ? 'bg-primary/[0.06]' : ''
                }`}
              >
                <div className="flex items-center justify-between gap-3">
                  <span
                    className={`font-mono text-[0.6rem] tracking-[0.26em] ${
                      state === 'pending' ? 'text-muted-foreground/50' : 'text-primary/80'
                    }`}
                  >
                    {String(index + 1).padStart(2, '0')}
                  </span>
                  {state === 'complete' && <Check className="size-3.5 text-primary" />}
                  {state === 'active' && <Loader2 className="size-3.5 animate-spin text-primary" />}
                  {state === 'pending' && <span className="size-1.5 rounded-full bg-muted-foreground/40" />}
                </div>
                <p
                  className={`font-mono text-[0.7rem] uppercase leading-relaxed tracking-[0.18em] ${
                    state === 'pending' ? 'text-muted-foreground/50' : 'text-foreground'
                  }`}
                >
                  {stage.label}
                </p>
              </li>
            )
          })}
        </ol>

        <div className="mt-10 flex flex-col gap-4 border-t border-border pt-6 sm:flex-row sm:items-center sm:justify-between">
          <p
            role="status"
            aria-live="polite"
            className={`font-mono text-[0.65rem] uppercase tracking-[0.2em] ${
              error ? 'text-destructive' : 'text-muted-foreground'
            }`}
          >
            {error ?? status ?? PIPELINE_STAGES[Math.max(activeIndex, 0)]?.detail}
          </p>
          {onCancel && (
            <button
              type="button"
              onClick={onCancel}
              className="self-start font-mono text-[0.65rem] uppercase tracking-[0.2em] text-muted-foreground underline decoration-border underline-offset-[6px] transition-colors hover:text-foreground sm:self-auto"
            >
              {error ? 'Return to upload' : 'Cancel run'}
            </button>
          )}
        </div>
      </div>
    </section>
  )
}
