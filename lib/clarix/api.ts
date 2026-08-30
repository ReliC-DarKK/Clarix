import {
  PIPELINE_STAGES,
  type AnalysisResult,
  type LandCoverClass,
  type PipelineStageId,
  type SourceImageMeta,
} from './types'

/**
 * Set NEXT_PUBLIC_CLARIX_API_URL to the FastAPI base URL.
 *
 * Example:
 * NEXT_PUBLIC_CLARIX_API_URL=http://127.0.0.1:8000
 */

const API_BASE =
  process.env.NEXT_PUBLIC_CLARIX_API_URL ?? ''

export const isLiveBackend =
  API_BASE.length > 0

export const LAND_COVER_CLASSES: LandCoverClass[] = [
  {
    id: 'vegetation',
    label: 'Vegetation',
    color: 'var(--vegetation)',
    share: null,
  },
  {
    id: 'water',
    label: 'Water',
    color: 'var(--water)',
    share: null,
  },
  {
    id: 'builtup',
    label: 'Built-up',
    color: 'var(--builtup)',
    share: null,
  },
  {
    id: 'road',
    label: 'Road',
    color: 'var(--road)',
    share: null,
  },
  {
    id: 'other',
    label: 'Other',
    color: 'var(--muted-foreground)',
    share: null,
  },
]

export interface StageEvent {
  stage: PipelineStageId
  message: string
}

export interface RunAnalysisOptions {
  file: File
  source: SourceImageMeta
  previewUrl?: string
  onStage?: (event: StageEvent) => void
  signal?: AbortSignal
}

/**
 * Backend pipeline result.
 *
 * FastAPI /analyze returns:
 *
 * {
 *   success: true,
 *   job_id: string,
 *   filename: string,
 *   result: {
 *     raw: string,
 *     hr: string,
 *     lr: string,
 *     sr: string,
 *     bicubic: string,
 *     p4?: string,
 *     p4_visual?: string,
 *     landCover?: [...]
 *   }
 * }
 */

interface BackendPipelineResult {
  raw: string
  hr: string
  lr: string
  sr: string
  bicubic: string

  // P1 evaluation
  psnr?: number
  ssim?: number

  // P3 baseline evaluation
  bicubic_psnr?: number
  bicubic_ssim?: number

  // P4
  p4?: string
  p4_visual?: string
  landCover?: LandCoverClass[]
}

interface BackendAnalyzeResponse {
  success: boolean
  job_id: string
  filename: string
  result: BackendPipelineResult
}

/**
 * Convert backend filesystem paths into browser URLs.
 *
 * Backend may return paths such as:
 *
 * C:\Users\DIVYA\Documents\clarix\backend_data\sr\image.png
 *
 * FastAPI exposes backend_data through:
 *
 * /pipeline-files/
 *
 * Therefore this becomes:
 *
 * http://127.0.0.1:8000/pipeline-files/sr/image.png
 */

function backendFileToUrl(
  filePath: string
): string {
  if (!filePath) {
    return ''
  }

  /**
   * If backend already returned a browser URL,
   * use it directly.
   */

  if (
    filePath.startsWith('http://') ||
    filePath.startsWith('https://')
  ) {
    return filePath
  }

  /**
   * Extract path relative to backend_data.
   *
   * Handles Windows:
   * C:\...\backend_data\sr\file.png
   *
   * and Unix:
   * /.../backend_data/sr/file.png
   */

  const marker = 'backend_data'

  const markerIndex =
    filePath
      .toLowerCase()
      .indexOf(marker.toLowerCase())

  if (markerIndex !== -1) {
    let relativePath =
      filePath.slice(
        markerIndex + marker.length
      )

    /**
     * Convert Windows "\" separators
     * into browser "/" separators.
     */

    relativePath =
      relativePath.replace(/\\/g, '/')

    /**
     * Remove leading slash.
     */

    relativePath =
      relativePath.replace(/^\/+/, '')

    /**
     * Encode each path segment safely.
     */

    const encodedPath =
      relativePath
        .split('/')
        .map(
          (segment) =>
            encodeURIComponent(segment)
        )
        .join('/')

    return `${API_BASE}/pipeline-files/${encodedPath}`
  }

  /**
   * If the backend returns something unexpected,
   * return it unchanged rather than silently
   * replacing it with demo data.
   */

  return filePath
}

/**
 * Live run against the FastAPI backend.
 *
 * The backend performs the pipeline synchronously.
 */

async function runLiveAnalysis(
  options: RunAnalysisOptions
): Promise<AnalysisResult> {

  /**
   * FastAPI expects:
   *
   * file: UploadFile = File(...)
   *
   * Therefore the multipart field MUST be "file".
   */

  const body = new FormData()

  body.append(
    'file',
    options.file
  )

  options.onStage?.({
    stage: 'preprocessing',
    message:
      'Uploading image for preprocessing',
  })

  /**
   * Send image to FastAPI.
   */

  let response: Response

  try {
    response = await fetch(
      `${API_BASE}/analyze`,
      {
        method: 'POST',
        body,
        signal: options.signal,
      }
    )
  } catch (error) {

    /**
     * Do NOT fall back to demo/mock data.
     */

    if (
      error instanceof DOMException &&
      error.name === 'AbortError'
    ) {
      throw error
    }

    throw new Error(
      'Could not connect to the Clarix backend. Make sure FastAPI is running on http://127.0.0.1:8000.'
    )
  }

  /**
   * Handle HTTP errors.
   */

  if (!response.ok) {
    let message =
      `Pipeline rejected the upload (${response.status})`

    try {
      const errorData =
        await response.json() as {
          detail?: string
        }

      if (errorData.detail) {
        message = errorData.detail
      }
    } catch {
      // Keep default error message.
    }

    throw new Error(message)
  }

  /**
   * Parse backend response.
   */

  let data: BackendAnalyzeResponse

  try {
    data =
      await response.json() as BackendAnalyzeResponse
  } catch {
    throw new Error(
      'The backend returned an invalid response.'
    )
  }

  /**
   * Validate backend response.
   */

  if (!data.success) {
    throw new Error(
      'The pipeline did not complete successfully.'
    )
  }

  if (!data.result) {
    throw new Error(
      'The pipeline completed without returning a result.'
    )
  }

  /**
   * Make sure the actual pipeline outputs exist.
   *
   * We intentionally DO NOT replace missing outputs
   * with demo images.
   */

  if (!data.result.lr) {
    throw new Error(
      'P2 completed but did not return an LR image.'
    )
  }

  if (!data.result.bicubic) {
    throw new Error(
      'P3 completed but did not return a Bicubic image.'
    )
  }

  if (!data.result.sr) {
    throw new Error(
      'P1 completed but did not return an SR image.'
    )
  }

  /**
   * Pipeline stages completed.
   */

  options.onStage?.({
    stage: 'preprocessing',
    message:
      'Preprocessing completed',
  })

  options.onStage?.({
    stage: 'super-resolution',
    message:
      'Super-resolution completed',
  })

  options.onStage?.({
    stage: 'evaluation',
    message:
      'Evaluation completed',
  })

  options.onStage?.({
    stage: 'mapping',
    message:
      'Land-cover mapping completed',
  })

  /**
   * Convert backend filesystem paths
   * into browser-accessible URLs.
   */

  const lrUrl =
    backendFileToUrl(
      data.result.lr
    )

  const srUrl =
    backendFileToUrl(
      data.result.sr
    )

  const bicubicUrl =
    backendFileToUrl(
      data.result.bicubic
    )

  /**
   * P4 visualization.
   *
   * If P4 has not been connected yet,
   * keep this empty.
   *
   * IMPORTANT:
   * We do NOT use /images/landcover-map.png
   * as a fallback.
   */

  const landCoverUrl =
    data.result.p4_visual
      ? backendFileToUrl(
          data.result.p4_visual
        )
      : ''

  /**
   * Actual frontend result.
   *
   * INPUT  = P2 LR 256x256
   * BICUBIC = P3 1024x1024
   * CLARIX = P1 Real-ESRGAN 1024x1024
   * LAND COVER = P4 visualization
   */

  return {
    jobId:
      data.job_id,

    source:
      options.source,

    images: {
      /**
       * P2 LR output
       * shown as Input.
       */

      input:
        lrUrl,

      /**
       * P3 Bicubic output.
       */

      bicubic:
        bicubicUrl,

      /**
       * P1 Real-ESRGAN output.
       */

      clarix:
        srUrl,

      /**
       * P4 segmentation visualization.
       *
       * Empty if P4 visual is not returned.
       */

      landCover:
        landCoverUrl,
    },

    metrics: {
      /**
       * Evaluation values are not currently
       * being returned by the backend response
       * interface.
       */

      psnr:
      typeof data.result.psnr === 'number'
      ? data.result.psnr
      : null,

      ssim:
      typeof data.result.ssim === 'number'
      ? data.result.ssim
      : null,
      /**
       * P1 is 4x.
       */

      scaleFactor: 4,
    },

    /**
     * Actual P4 class percentages if returned.
     *
     * Only use the static class definitions
     * if the backend hasn't returned percentages.
     */

    landCover:
      data.result.landCover ??
      LAND_COVER_CLASSES,
  }
}

/**
 * Main analysis entry point.
 *
 * IMPORTANT:
 *
 * There is intentionally NO mock fallback here.
 *
 * If the backend is unavailable,
 * runAnalysis() throws an error.
 */

export function runAnalysis(
  options: RunAnalysisOptions
): Promise<AnalysisResult> {

  if (!API_BASE) {
    return Promise.reject(
      new Error(
        'NEXT_PUBLIC_CLARIX_API_URL is not configured. Start the FastAPI backend and set the API URL in .env.local.'
      )
    )
  }

  return runLiveAnalysis(options)
}

/**
 * Format PSNR value.
 */

export function formatPsnr(
  value: number | null
) {
  return value === null
    ? '—'
    : `${value.toFixed(2)} dB`
}

/**
 * Format SSIM value.
 */

export function formatSsim(
  value: number | null
) {
  return value === null
    ? '—'
    : value.toFixed(4)
}

/**
 * Format file size.
 */

export function formatBytes(
  bytes: number
) {
  if (bytes < 1024) {
    return `${bytes} B`
  }

  if (bytes < 1024 * 1024) {
    return `${(
      bytes / 1024
    ).toFixed(1)} KB`
  }

  return `${(
    bytes /
    (1024 * 1024)
  ).toFixed(2)} MB`
}