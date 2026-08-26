'use client'

import { useCallback, useEffect, useRef, useState } from 'react'
import { Processing } from '@/components/analysis/processing'
import { Results } from '@/components/analysis/results'
import { Upload, type SelectedImage } from '@/components/analysis/upload'
import { runAnalysis } from '@/lib/clarix/api'
import type { AnalysisResult, PipelineStageId } from '@/lib/clarix/types'

type Phase = 'upload' | 'processing' | 'results'

export function AnalysisFlow() {
  const [phase, setPhase] = useState<Phase>('upload')
  const [stage, setStage] = useState<PipelineStageId>('preprocessing')
  const [status, setStatus] = useState<string | undefined>(undefined)
  const [error, setError] = useState<string | null>(null)
  const [filename, setFilename] = useState<string | undefined>(undefined)
  const [result, setResult] = useState<AnalysisResult | null>(null)
  const controllerRef = useRef<AbortController | null>(null)

  useEffect(() => {
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }, [phase])

  const start = useCallback(async (selection: SelectedImage) => {
    const controller = new AbortController()
    controllerRef.current = controller

    setPhase('processing')
    setStage('preprocessing')
    setStatus(undefined)
    setError(null)
    setFilename(selection.meta.filename)

    try {
      const analysis = await runAnalysis({
        file: selection.file,
        source: selection.meta,
        previewUrl: selection.previewUrl,
        signal: controller.signal,
        onStage: ({ stage: nextStage, message }) => {
          setStage(nextStage)
          setStatus(message)
        },
      })
      setResult(analysis)
      setPhase('results')
    } catch (err) {
      if ((err as Error)?.name === 'AbortError') return
      setError(err instanceof Error ? err.message : 'The pipeline returned an unexpected error.')
    }
  }, [])

  const reset = useCallback(() => {
    controllerRef.current?.abort()
    controllerRef.current = null
    setPhase('upload')
    setResult(null)
    setError(null)
    setStatus(undefined)
  }, [])

  if (phase === 'processing') {
    return <Processing activeStage={stage} status={status} filename={filename} error={error} onCancel={reset} />
  }

  if (phase === 'results' && result) {
    return (
      <div className="mx-auto w-full max-w-[1400px] px-5 py-28 md:px-10 md:py-36">
        <Results result={result} onRestart={reset} />
      </div>
    )
  }

  return (
    <div className="mx-auto w-full max-w-[1400px] px-5 py-28 md:px-10 md:py-36">
      <header className="max-w-3xl">
        <div className="flex items-center gap-4">
          <span className="h-px w-10 bg-primary/60" />
          <span className="label-xs text-primary/80">Analysis console</span>
        </div>
        <h1 className="mt-8 text-[clamp(2.2rem,7vw,5rem)] font-bold uppercase leading-[0.95] tracking-[-0.02em] text-balance">
          Analyze satellite imagery
        </h1>
        <p className="mt-6 text-base leading-relaxed text-muted-foreground text-pretty md:text-lg">
          Upload a medium-resolution satellite image to generate a super-resolved representation and spatial land-cover
          map.
        </p>
      </header>

      <div className="mt-16 md:mt-20">
        <Upload onSubmit={start} />
      </div>
    </div>
  )
}
