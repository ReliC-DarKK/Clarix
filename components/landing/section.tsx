import type { ReactNode } from 'react'

interface SectionProps {
  id: string
  label: string
  title: string
  description?: string
  children: ReactNode
  className?: string
}

export function Section({ id, label, title, description, children, className = '' }: SectionProps) {
  return (
    <section id={id} aria-labelledby={`${id}-heading`} className={`scroll-mt-24 py-24 md:py-36 ${className}`}>
      <div className="mx-auto max-w-[1400px] px-5 md:px-10">
        <div className="flex flex-col gap-6 border-t border-border pt-8 lg:flex-row lg:items-start lg:justify-between lg:gap-16">
          <div className="flex items-center gap-4 lg:w-64 lg:shrink-0">
            <span className="h-px w-8 bg-primary/60" />
            <span className="label-xs text-primary/80">{label}</span>
          </div>
          <div className="max-w-3xl">
            <h2
              id={`${id}-heading`}
              className="text-[clamp(1.9rem,5vw,3.75rem)] font-bold uppercase leading-[1] tracking-[-0.02em] text-balance"
            >
              {title}
            </h2>
            {description && (
              <p className="mt-6 text-base leading-relaxed text-muted-foreground text-pretty md:text-lg">
                {description}
              </p>
            )}
          </div>
        </div>

        <div className="mt-16 md:mt-20">{children}</div>
      </div>
    </section>
  )
}
