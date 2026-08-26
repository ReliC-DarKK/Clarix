'use client'

import Image from 'next/image'
import { useCallback, useRef, useState } from 'react'
import { ArrowRight, ImageIcon, RotateCcw, UploadCloud } from 'lucide-react'
import { formatBytes } from '@/lib/clarix/api'
import type { SourceImageMeta } from '@/lib/clarix/types'

const ACCEPTED = ['image/png', 'image/jpeg']

export interface SelectedImage {
  file: File
  previewUrl: string
  meta: SourceImageMeta
}

interface UploadProps {
  onSubmit: (selection: SelectedImage) => void
}

export function Upload({ onSubmit }: UploadProps) {
  const inputRef = useRef<HTMLInputElement | null>(null)
  const [dragging, setDragging] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [selection, setSelection] = useState<SelectedImage | null>(null)

  const handleFile = useCallback((file: File) => {
    if (!ACCEPTED.includes(file.type)) {
      setError('Unsupported format. Provide a PNG, JPG or JPEG scene.')
      return
    }
    setError(null)
    const previewUrl = URL.createObjectURL(file)
    const probe = new window.Image()
    probe.crossOrigin = 'anonymous'
    probe.onload = () => {
      setSelection({
        file,
        previewUrl,
        meta: {
          filename: file.name,
          width: probe.naturalWidth,
          height: probe.naturalHeight,
          size: file.size,
        },
      })
    }
    probe.onerror = () => setError('That file could not be read as an image.')
    probe.src = previewUrl
  }, [])

  const reset = () => {
    if (selection) URL.revokeObjectURL(selection.previewUrl)
    setSelection(null)
    setError(null)
    if (inputRef.current) inputRef.current.value = ''
  }

  return (
    <div className="grid gap-10 lg:grid-cols-[1.15fr_1fr] lg:gap-14">
      <div>
        <div
          onDragOver={(e) => {
            e.preventDefault()
            setDragging(true)
          }}
          onDragLeave={() => setDragging(false)}
          onDrop={(e) => {
            e.preventDefault()
            setDragging(false)
            const file = e.dataTransfer.files?.[0]
            if (file) handleFile(file)
          }}
          className={`relative flex min-h-[22rem] flex-col items-center justify-center overflow-hidden rounded-sm border border-dashed px-6 py-16 text-center transition-colors duration-300 md:min-h-[26rem] ${
            dragging ? 'border-primary bg-primary/[0.06]' : 'border-border bg-card/30 hover:border-foreground/30'
          }`}
        >
          <div aria-hidden className="grid-overlay pointer-events-none absolute inset-0 opacity-60" />
          <div aria-hidden className="pointer-events-none absolute -bottom-24 left-1/2 size-80 -translate-x-1/2 rounded-full bg-primary/10 blur-[100px]" />

          <span className="relative flex size-16 items-center justify-center rounded-full border border-border bg-background/60">
            <UploadCloud className={`size-6 transition-colors ${dragging ? 'text-primary' : 'text-muted-foreground'}`} />
          </span>

          <p className="relative mt-8 font-mono text-sm uppercase tracking-[0.24em] text-foreground md:text-base">
            Drop satellite image here
          </p>
          <button
            type="button"
            onClick={() => inputRef.current?.click()}
            className="relative mt-4 font-mono text-[0.7rem] uppercase tracking-[0.2em] text-primary underline decoration-primary/40 underline-offset-[6px] transition-colors hover:decoration-primary"
          >
            or browse files
          </button>
          <p className="relative mt-8 font-mono text-[0.6rem] uppercase tracking-[0.22em] text-muted-foreground/70">
            PNG · JPG · JPEG
          </p>

          <input
            ref={inputRef}
            type="file"
            accept="image/png,image/jpeg"
            className="sr-only"
            onChange={(e) => {
              const file = e.target.files?.[0]
              if (file) handleFile(file)
            }}
          />
        </div>

        {error && (
          <p role="alert" className="mt-4 font-mono text-[0.65rem] uppercase tracking-[0.18em] text-destructive">
            {error}
          </p>
        )}
      </div>

      <div className="flex flex-col">
        <p className="label-xs">Scene preview</p>

        <div className="mt-5 relative aspect-[4/3] overflow-hidden rounded-sm border border-border bg-card/40">
          {selection ? (
            <Image
              src={selection.previewUrl}
              alt={`Preview of ${selection.meta.filename}`}
              fill
              unoptimized
              sizes="(max-width: 1024px) 100vw, 40vw"
              className="object-cover"
            />
          ) : (
            <div className="flex size-full flex-col items-center justify-center gap-3 text-muted-foreground/60">
              <ImageIcon className="size-6" />
              <span className="font-mono text-[0.6rem] uppercase tracking-[0.22em]">No scene selected</span>
            </div>
          )}
          <div aria-hidden className="grid-overlay pointer-events-none absolute inset-0 opacity-40" />
        </div>

        <dl className="mt-6 flex flex-col gap-3">
          {[
            ['File', selection?.meta.filename ?? '—'],
            [
              'Dimensions',
              selection ? `${selection.meta.width} × ${selection.meta.height} px` : '—',
            ],
            ['Size', selection ? formatBytes(selection.meta.size) : '—'],
          ].map(([term, value]) => (
            <div key={term} className="flex items-center justify-between gap-6 border-b border-border pb-2">
              <dt className="label-xs">{term}</dt>
              <dd className="truncate font-mono text-xs text-foreground">{value}</dd>
            </div>
          ))}
        </dl>

        <div className="mt-8 flex flex-col gap-3 sm:flex-row">
          <button
            type="button"
            disabled={!selection}
            onClick={() => selection && onSubmit(selection)}
            className="group inline-flex flex-1 items-center justify-center gap-3 rounded-sm bg-primary px-7 py-4 font-mono text-[0.7rem] uppercase tracking-[0.22em] text-primary-foreground transition-all hover:shadow-[0_0_44px_-8px_var(--primary)] disabled:cursor-not-allowed disabled:bg-secondary disabled:text-muted-foreground disabled:shadow-none"
          >
            Generate SR Map
            <ArrowRight className="size-4 transition-transform group-hover:translate-x-1" />
          </button>
          {selection && (
            <button
              type="button"
              onClick={reset}
              className="inline-flex items-center justify-center gap-2 rounded-sm border border-border px-5 py-4 font-mono text-[0.7rem] uppercase tracking-[0.2em] text-muted-foreground transition-colors hover:text-foreground"
            >
              <RotateCcw className="size-3.5" />
              Clear
            </button>
          )}
        </div>
      </div>
    </div>
  )
}
