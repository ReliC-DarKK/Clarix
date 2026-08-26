/**
 * Shared contract between the CLARIX frontend and the Python / FastAPI pipeline.
 * Keep these types in sync with the backend response models.
 */

export type PipelineStageId = 'preprocessing' | 'super-resolution' | 'evaluation' | 'mapping'

export type StageState = 'pending' | 'active' | 'complete'

export interface PipelineStage {
  id: PipelineStageId
  label: string
  /** Short technical status line surfaced under the stage list. */
  detail: string
}

export const PIPELINE_STAGES: PipelineStage[] = [
  {
    id: 'preprocessing',
    label: 'Preprocessing',
    detail: 'Normalising bands, aligning tile grid',
  },
  {
    id: 'super-resolution',
    label: 'Super-Resolution',
    detail: 'Running deep-learning reconstruction',
  },
  {
    id: 'evaluation',
    label: 'Evaluation',
    detail: 'Computing PSNR / SSIM against baseline',
  },
  {
    id: 'mapping',
    label: 'Mapping',
    detail: 'Segmenting land-cover classes',
  },
]

export interface SourceImageMeta {
  filename: string
  width: number
  height: number
  /** Bytes. */
  size: number
}

export interface AnalysisMetrics {
  /** Peak signal-to-noise ratio, in dB. `null` until the backend reports it. */
  psnr: number | null
  /** Structural similarity index, 0–1. `null` until the backend reports it. */
  ssim: number | null
  /** Upscaling factor applied by the model, e.g. 4 for 4x. */
  scaleFactor: number | null
}

export interface LandCoverClass {
  id: string
  label: string
  /** CSS color token used by the legend swatch. */
  color: string
  /** Share of the scene, 0–1. `null` when unknown. */
  share: number | null
}

export interface AnalysisResult {
  jobId: string
  source: SourceImageMeta
  images: {
    input: string
    bicubic: string
    clarix: string
    landCover: string
  }
  metrics: AnalysisMetrics
  landCover: LandCoverClass[]
}

export interface AnalysisJobStatus {
  jobId: string
  stage: PipelineStageId
  state: 'queued' | 'running' | 'succeeded' | 'failed'
  message?: string
  result?: AnalysisResult
}
