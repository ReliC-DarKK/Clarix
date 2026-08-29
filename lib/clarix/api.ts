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
 *
 * If it is not set, the frontend uses mock mode.
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

/**
 * Reference imagery used while the real pipeline
 * is not connected.
 */

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

  /**
   * Preview object URL of the uploaded file.
   *
   * Used as the INPUT panel in mock mode.
   */
  previewUrl?: string

  onStage?: (event: StageEvent) => void
  signal?: AbortSignal
}

/**
 * Small helper used by the mock pipeline.
 */
function delay(
  ms: number,
  signal?: AbortSignal
) {
  return new Promise<void>((resolve, reject) => {
    const timer = setTimeout(resolve, ms)

    signal?.addEventListener(
      'abort',
      () => {
        clearTimeout(timer)

        reject(
          new DOMException(
            'Aborted',
            'AbortError'
          )
        )
      },
      { once: true }
    )
  })
}

/**
 * Mock run.
 *
 * Walks through the same pipeline stages so the UI
 * can be tested even when the FastAPI backend
 * is not connected.
 */
async function runMockAnalysis(
  options: RunAnalysisOptions
): Promise<AnalysisResult> {
  for (const stage of PIPELINE_STAGES) {
    options.onStage?.({
      stage: stage.id,
      message: stage.detail,
    })

    await delay(
      1500,
      options.signal
    )
  }

  return {
    jobId:
      `mock-${Date.now().toString(36)}`,

    source:
      options.source,

    images: {
      input:
        options.previewUrl ??
        PLACEHOLDER_IMAGES.input,

      bicubic:
        PLACEHOLDER_IMAGES.bicubic,

      clarix:
        PLACEHOLDER_IMAGES.clarix,

      landCover:
        PLACEHOLDER_IMAGES.landCover,
    },

    metrics: {
      psnr: null,
      ssim: null,
      scaleFactor: null,
    },

    landCover:
      LAND_COVER_CLASSES,
  }
}

/**
 * Current FastAPI backend response.
 *
 * POST /analyze returns:
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
 *     bicubic: string
 *   }
 * }
 */

interface BackendPipelineResult {
  raw: string
  hr: string
  lr: string
  sr: string
  bicubic: string
}

interface BackendAnalyzeResponse {
  success: boolean
  job_id: string
  filename: string
  result: BackendPipelineResult
}

/**
 * Convert a backend filesystem path into a browser URL.
 *
 * Backend returns Windows paths such as:
 *
 * C:\Users\DIVYA\Documents\clarix\backend_data\sr\image.png
 *
 * FastAPI exposes backend_data through:
 *
 * /pipeline-files/
 *
 * Therefore the browser URL becomes:
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
   * Extract the path relative to backend_data.
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
      .indexOf(
        marker.toLowerCase()
      )

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
   * If backend somehow already returns a URL,
   * use it directly.
   */

  if (
    filePath.startsWith('http://') ||
    filePath.startsWith('https://')
  ) {
    return filePath
  }

  return filePath
}

/**
 * Live run against the FastAPI backend.
 *
 * The backend currently performs the pipeline
 * synchronously.
 */

async function runLiveAnalysis(
  options: RunAnalysisOptions
): Promise<AnalysisResult> {
  const body = new FormData()

  /**
   * FastAPI expects:
   *
   * file: UploadFile = File(...)
   *
   * Therefore the multipart field must be "file".
   */

  body.append(
    'file',
    options.file
  )

  options.onStage?.({
    stage: 'preprocessing',
    message:
      'Uploading image for preprocessing',
  })

  const response =
    await fetch(
      `${API_BASE}/analyze`,
      {
        method: 'POST',
        body,
        signal: options.signal,
      }
    )

  if (!response.ok) {
    let message =
      `Pipeline rejected the upload (${response.status})`

    try {
      const errorData =
        await response.json() as {
          detail?: string
        }

      if (errorData.detail) {
        message =
          errorData.detail
      }
    } catch {
      // Keep the default error message.
    }

    throw new Error(message)
  }

  const data =
    await response.json() as BackendAnalyzeResponse

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
   * Backend is synchronous.
   *
   * By the time /analyze responds:
   *
   * P2 is complete
   * P1 is complete
   * P3 is complete
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
   * into URLs that the browser can actually load.
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
   * Return the existing frontend AnalysisResult.
   *
   * IMPORTANT:
   *
   * INPUT is now the actual LR 256x256 image
   * generated by P2.
   *
   * P3 = Bicubic 1024x1024
   * P1 = Real-ESRGAN 1024x1024
   */

  return {
    jobId:
      data.job_id,

    source:
      options.source,

    images: {
      /**
       * P2 LR 256x256
       *
       * This is now shown as the INPUT
       * instead of the original uploaded image.
       */

      input:
        lrUrl ||
        PLACEHOLDER_IMAGES.input,

      /**
       * P3 Bicubic 1024x1024
       */

      bicubic:
        bicubicUrl ||
        PLACEHOLDER_IMAGES.bicubic,

      /**
       * P1 Real-ESRGAN 1024x1024
       */

      clarix:
        srUrl ||
        PLACEHOLDER_IMAGES.clarix,

      /**
       * P4 is not integrated yet.
       */

      landCover:
        PLACEHOLDER_IMAGES.landCover,
    },

    metrics: {
      psnr: null,
      ssim: null,
      scaleFactor: 4,
    },

    landCover:
      LAND_COVER_CLASSES,
  }
}

/**
 * Main analysis entry point.
 */

export function runAnalysis(
  options: RunAnalysisOptions
): Promise<AnalysisResult> {
  return isLiveBackend
    ? runLiveAnalysis(options)
    : runMockAnalysis(options)
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