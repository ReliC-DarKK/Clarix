"use client"
import Image from 'next/image'
import Link from 'next/link'
import { ArrowRight } from 'lucide-react'
import { Starfield } from '@/components/starfield'

export function Hero() {
  return (
    <section className="relative flex min-h-svh flex-col justify-end overflow-hidden pt-28">
      {/* Earth limb */}
      <div aria-hidden className="absolute inset-0">
        <div className="animate-drift absolute -right-[18%] -bottom-[42%] size-[130vw] max-w-[1600px] sm:-right-[8%] sm:-bottom-[52%] sm:size-[95vw]">
          <Image
            src="/images/earth-limb.png"
            alt=""
            fill
            priority
            sizes="100vw"
            className="scale-105 object-cover opacity-75"
          />
        </div>
        <div className="absolute inset-0 bg-[radial-gradient(120%_90%_at_50%_0%,transparent_10%,var(--background)_78%)]" />
        <div className="absolute inset-x-0 bottom-0 h-64 bg-gradient-to-t from-background to-transparent" />
        <div className="absolute -top-40 left-1/2 size-[52rem] -translate-x-1/2 rounded-full bg-primary/10 blur-[140px]" />
        <div className="absolute right-[12%] top-[26%] size-[26rem] rounded-full bg-accent/10 blur-[130px]" />
        <div className="grid-overlay absolute inset-0 opacity-70 [mask-image:radial-gradient(75%_60%_at_50%_35%,black,transparent)]" />
        <div className="absolute inset-0">
          <Starfield />
        </div>
      </div>

      <div className="relative mx-auto w-full max-w-[1400px] px-5 pb-16 md:px-10 md:pb-24">
        <div className="animate-rise flex items-center gap-4">
          <span className="h-px w-10 bg-primary/60" />
          <span className="label-xs text-primary/80">Super-Resolution Mapping System</span>
        </div>

        <h1 className="animate-rise mt-8 max-w-5xl text-[clamp(2.6rem,9vw,7.5rem)] font-bold uppercase leading-[0.92] tracking-[-0.03em] text-balance">
          See more.
          <br />
          <span className="text-muted-foreground">From every</span> pixel.
        </h1>

        <div className="mt-10 flex flex-col gap-10 border-t border-border pt-8 md:flex-row md:items-end md:justify-between">
          <p className="animate-rise max-w-xl text-lg leading-relaxed text-muted-foreground text-pretty md:text-xl">
            AI-powered super-resolution mapping for medium-resolution satellite imagery.
          </p>

          <div className="animate-rise flex flex-col gap-3 sm:flex-row sm:items-center">
            <Link
              href="/analysis"
              className="group inline-flex items-center justify-center gap-3 rounded-sm bg-primary px-8 py-4 font-mono text-[0.72rem] uppercase tracking-[0.22em] text-primary-foreground transition-all hover:shadow-[0_0_44px_-8px_var(--primary)]"
            >
              Start Analysis
              <ArrowRight className="size-4 transition-transform group-hover:translate-x-1" />
            </Link>
            <Link
              href="#technology"
              className="inline-flex items-center justify-center rounded-sm border border-border px-8 py-4 font-mono text-[0.72rem] uppercase tracking-[0.22em] text-foreground transition-colors hover:border-primary/50 hover:text-primary"
            >
              Explore Technology
            </Link>
          </div>
        </div>

        <dl className="mt-14 grid grid-cols-2 gap-x-8 gap-y-8 border-t border-border pt-8 md:grid-cols-4">
          {[
            ['Input', 'Medium-resolution scenes'],
            ['Model', 'Deep-learning reconstruction'],
            ['Baseline', 'Bicubic interpolation'],
            ['Output', 'Land-cover map + metrics'],
          ].map(([term, description]) => (
            <div key={term}>
              <dt className="label-xs">{term}</dt>
              <dd className="mt-2 text-sm leading-relaxed text-foreground/80">{description}</dd>
            </div>
          ))}
        </dl>
      </div>
    </section>
  )
}
