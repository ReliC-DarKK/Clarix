import Image from 'next/image'

export interface ComparisonImages {
  input: string
  bicubic: string
  clarix: string
}

interface ImageComparisonProps {
  images: ComparisonImages
  /** Optional caption shown as a technical footer on each panel. */
  scaleFactor?: number | null
}

function Panel({
  label,
  index,
  caption,
  src,
  featured = false,
  meta,
}: {
  label: string
  index: string
  caption: string
  src: string
  featured?: boolean
  meta: string
}) {
  return (
    <figure
      className={`group relative flex flex-col overflow-hidden rounded-sm border transition-colors duration-500 ${
        featured
          ? 'border-primary/40 bg-primary/[0.04] shadow-[0_0_90px_-40px_var(--primary)]'
          : 'border-border bg-card/40 hover:border-foreground/25'
      }`}
    >
      <div className="flex items-center justify-between gap-4 border-b border-inherit px-4 py-3">
        <div className="flex items-center gap-3">
          <span className={`font-mono text-[0.62rem] tracking-[0.28em] ${featured ? 'text-primary' : 'text-muted-foreground'}`}>
            {index}
          </span>
          <figcaption
            className={`font-mono text-[0.7rem] uppercase tracking-[0.24em] ${
              featured ? 'text-primary' : 'text-foreground'
            }`}
          >
            {label}
          </figcaption>
        </div>
        {featured && (
          <span className="flex items-center gap-2 font-mono text-[0.6rem] uppercase tracking-[0.2em] text-primary/80">
            <span className="size-1.5 animate-pulse rounded-full bg-primary" />
            Enhanced
          </span>
        )}
      </div>

      <div className={`relative overflow-hidden ${featured ? 'aspect-[16/11]' : 'aspect-[4/3]'}`}>
        <Image
          src={src || '/placeholder.svg'}
          alt={`${label} — ${caption}`}
          fill
          sizes="(max-width: 1024px) 100vw, 50vw"
          className="object-cover transition-transform duration-[1200ms] ease-out group-hover:scale-[1.06]"
        />
        <div aria-hidden className="grid-overlay pointer-events-none absolute inset-0 opacity-40" />
        {featured && (
          <div aria-hidden className="pointer-events-none absolute inset-0 overflow-hidden">
            <div className="animate-scan absolute inset-x-0 top-0 h-16 bg-gradient-to-b from-transparent via-primary/15 to-transparent" />
          </div>
        )}
      </div>

      <div className="flex items-center justify-between gap-4 border-t border-inherit px-4 py-3">
        <p className="text-xs leading-relaxed text-muted-foreground">{caption}</p>
        <span className="hidden font-mono text-[0.6rem] uppercase tracking-[0.2em] text-muted-foreground/70 sm:block">
          {meta}
        </span>
      </div>
    </figure>
  )
}

export function ImageComparison({ images, scaleFactor }: ImageComparisonProps) {
  const scaleLabel = scaleFactor ? `${scaleFactor}×` : '—'

  return (
    <div className="grid gap-4 lg:grid-cols-12">
      <div className="grid gap-4 lg:col-span-5">
        <Panel
          index="01"
          label="Input"
          caption="Medium-resolution input"
          src={images.input}
          meta="Source"
        />
        <Panel
          index="02"
          label="Bicubic"
          caption="Traditional interpolation baseline"
          src={images.bicubic}
          meta={scaleLabel}
        />
      </div>

      <div className="lg:col-span-7">
        <Panel
          index="03"
          label="Clarix AI"
          caption="AI super-resolved output"
          src={images.clarix}
          featured
          meta={scaleLabel}
        />
      </div>
    </div>
  )
}
