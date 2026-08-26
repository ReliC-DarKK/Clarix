import { Section } from '@/components/landing/section'

const PIPELINE = [
  {
    title: 'Satellite imagery',
    body: 'We start from freely available medium-resolution scenes — useful coverage, but too coarse to read small features clearly.',
  },
  {
    title: 'Image preprocessing',
    body: 'Each scene is cleaned and normalised so brightness, scale and tiling are consistent before anything is learned from it.',
  },
  {
    title: 'Deep-learning super-resolution',
    body: 'A trained model rebuilds the fine detail that a coarse sensor could not capture, guided by patterns it learned from sharper imagery.',
  },
  {
    title: 'Bicubic baseline',
    body: 'The same scene is also enlarged with classic interpolation, giving an honest reference point for what the model actually adds.',
  },
  {
    title: 'PSNR / SSIM evaluation',
    body: 'Two standard measures compare both results against the reference: one for pixel accuracy, one for structural likeness.',
  },
  {
    title: 'Land-cover segmentation',
    body: 'Finally the sharpened scene is grouped into surface classes — vegetation, water, built-up, roads — as a readable map.',
  },
]

export function TechnologySection() {
  return (
    <Section
      id="technology"
      label="Technology"
      title="A short pipeline, explained plainly"
      description="CLARIX turns a coarse scene into a sharper one, checks the result against a fair baseline, and then reads the surface as a map."
    >
      <div className="grid gap-px overflow-hidden border border-border bg-border sm:grid-cols-2 lg:grid-cols-3">
        {PIPELINE.map((item, index) => (
          <article
            key={item.title}
            className="group relative flex flex-col gap-5 bg-background px-6 py-9 transition-colors duration-500 hover:bg-card/60 md:px-8 md:py-12"
          >
            <span className="font-mono text-[0.62rem] tracking-[0.28em] text-primary/70">
              {String(index + 1).padStart(2, '0')}
            </span>
            <h3 className="text-lg font-semibold uppercase tracking-[0.01em] md:text-xl">{item.title}</h3>
            <p className="text-sm leading-relaxed text-muted-foreground">{item.body}</p>
            <span
              aria-hidden
              className="absolute inset-x-0 bottom-0 h-px scale-x-0 bg-primary/60 transition-transform duration-500 group-hover:scale-x-100"
            />
          </article>
        ))}
      </div>
    </Section>
  )
}
