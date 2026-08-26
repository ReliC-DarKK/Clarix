import {
  PIPELINE_STAGES,
  type AnalysisJobStatus,
  type AnalysisResult,
  type LandCoverClass,
  type PipelineStageId,
  type SourceImageMeta,
} from './types'

/**
 * Set NEXT_PUBLIC_CLARIX_API_URL to the FastAPI base URL (e.g. https://api.clarix.dev)
 * to switch the UI from mock mode to the real pipeline. No component changes required.
 */
const API_BASE = process.env.NEXT_PUBLIC_CLARIX_API_URL ?? ''

export const isLiveBackend = API_BASE.length > 0

export const LAND_COVER_CLASSES: LandCoverClass[] = [
  { id: 'vegetation', label: 'Vegetation', color: 'var(--vegetation)', share: null },
  { id: 'water', label: 'Water', color: 'var(--water)', share: null },
  { id: 'builtup', label: 'Built-up', color: 'var(--builtup)', share: null },
  { id: 'road', label: 'Road', color: 'var(--road)', share: null },
  { id: 'other', label: 'Other', color: 'var(--muted-foreground)', share: null },
]

/** Reference imagery used while the pipeline is not connected. */
const PLACEHOLDER_IMAGES = {
  input: '/images/tile-input.png',
  bicubic: '/images/tile-bicubic.png',
  clarix: '/images/tile-clarix.png',
  landCover: '/images/landcover-map.png',
}

export interface StageEvent {
  stage: PipelineStageId
  message: string
}

export interface RunAnalysisOptions {
  file: File
  source: SourceImageMeta
  /** Preview object URL of the uploaded file, used as the INPUT panel in mock mode. */
  previewUrl?: string
  onStage?: (event: StageEvent) => void
  signal?: AbortSignal
}

function delay(ms: number, signal?: AbortSignal) {
  return new Promise<void>((resolve, reject) => {
    const timer = setTimeout(resolve, ms)
    signal?.addEventListener('abort', () => {
      clearTimeout(timer)
      reject(new DOMException('Aborted', 'AbortError'))
    })
  })
}

/**
 * Mock run: walks the real stage sequence so the UI is exercised end-to-end.
 * Metrics stay null — the UI renders them as pending rather than inventing numbers.
 */
async function runMockAnalysis(options: RunAnalysisOptions): Promise<AnalysisResult> {
  for (const stage of PIPELINE_STAGES) {
    options.onStage?.({ stage: stage.id, message: stage.detail })
    await delay(1500, options.signal)
  }

  return {
    jobId: `mock-${Date.now().toString(36)}`,
    source: options.source,
    images: {
      input: options.previewUrl ?? PLACEHOLDER_IMAGES.input,
      bicubic: PLACEHOLDER_IMAGES.bicubic,
      clarix: PLACEHOLDER_IMAGES.clarix,
      landCover: PLACEHOLDER_IMAGES.landCover,
    },
    metrics: { psnr: null, ssim: null, scaleFactor: null },
    landCover: LAND_COVER_CLASSES,
  }
}

/**
 * Live run against FastAPI:
 *   POST {API_BASE}/analyze        multipart/form-data -> { jobId }
 *   GET  {API_BASE}/jobs/{jobId}   -> AnalysisJobStatus
 */
async function runLiveAnalysis(options: RunAnalysisOptions): Promise<AnalysisResult> {
  const body = new FormData()
  body.append('image', options.file)

  const created = await fetch(`${API_BASE}/analyze`, {
    method: 'POST',
    body,
    signal: options.signal,
  })
  if (!created.ok) throw new Error(`Pipeline rejected the upload (${created.status})`)

  const { jobId } = (await created.json()) as { jobId: string }

  // Poll until the job resolves. The backend owns real stage progression.
  for (;;) {
    const res = await fetch(`${API_BASE}/jobs/${jobId}`, { signal: options.signal })
    if (!res.ok) throw new Error(`Unable to read job status (${res.status})`)

    const status = (await res.json()) as AnalysisJobStatus
    options.onStage?.({ stage: status.stage, message: status.message ?? '' })

    if (status.state === 'failed') throw new Error(status.message ?? 'Pipeline failed')
    if (status.state === 'succeeded' && status.result) return status.result

    await delay(1200, options.signal)
  }
}

export function runAnalysis(options: RunAnalysisOptions): Promise<AnalysisResult> {
  return isLiveBackend ? runLiveAnalysis(options) : runMockAnalysis(options)
}

export function formatPsnr(value: number | null) {
  return value === null ? '—' : `${value.toFixed(2)} dB`
}

export function formatSsim(value: number | null) {
  return value === null ? '—' : value.toFixed(4)
}

export function formatBytes(bytes: number) {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(2)} MB`
}
