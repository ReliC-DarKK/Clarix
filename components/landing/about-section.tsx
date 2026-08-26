import { Section } from '@/components/landing/section'

const NOTES = [
  ['Purpose', 'Make coarse public imagery useful for reading land surface at a finer scale.'],
  ['Method', 'Deep-learning reconstruction, measured against a classic interpolation baseline.'],
  ['Honesty', 'Results are reported with standard metrics — never asserted without measurement.'],
  ['Interface', 'Built as a research console: upload a scene, inspect the output, compare, repeat.'],
]

export function AboutSection() {
  return (
    <Section
      id="about"
      label="About"
      title="Built as an instrument, not a demo"
      description="CLARIX is a research interface for super-resolution mapping. The frontend shown here is designed to sit directly on top of the processing pipeline that produces its outputs."
    >
      <dl className="grid gap-x-16 gap-y-10 sm:grid-cols-2">
        {NOTES.map(([term, body]) => (
          <div key={term} className="border-t border-border pt-6">
            <dt className="label-xs">{term}</dt>
            <dd className="mt-4 max-w-md text-sm leading-relaxed text-foreground/85 md:text-base">{body}</dd>
          </div>
        ))}
      </dl>
    </Section>
  )
}
