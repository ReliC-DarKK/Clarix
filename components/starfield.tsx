'use client'

import { useEffect, useRef } from 'react'

type Particle = {
  x: number
  y: number
  r: number
  a: number
  vx: number
  vy: number
  tw: number
}

/**
 * Lightweight atmospheric particle layer. Purely decorative.
 */
export function Starfield({ className = '', density = 0.00012 }: { className?: string; density?: number }) {
  const canvasRef = useRef<HTMLCanvasElement | null>(null)

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return
    const ctx = canvas.getContext('2d')
    if (!ctx) return

    const reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches
    let particles: Particle[] = []
    let frame = 0
    let raf = 0

    const setup = () => {
      const dpr = Math.min(window.devicePixelRatio || 1, 2)
      const { width, height } = canvas.getBoundingClientRect()
      canvas.width = Math.floor(width * dpr)
      canvas.height = Math.floor(height * dpr)
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0)

      const count = Math.round(width * height * density)
      particles = Array.from({ length: count }, () => ({
        x: Math.random() * width,
        y: Math.random() * height,
        r: Math.random() * 1.2 + 0.3,
        a: Math.random() * 0.5 + 0.15,
        vx: (Math.random() - 0.5) * 0.06,
        vy: (Math.random() - 0.5) * 0.06,
        tw: Math.random() * Math.PI * 2,
      }))
    }

    const draw = () => {
      const { width, height } = canvas.getBoundingClientRect()
      ctx.clearRect(0, 0, width, height)
      frame += 1

      for (const p of particles) {
        if (!reduced) {
          p.x += p.vx
          p.y += p.vy
          if (p.x < 0) p.x = width
          if (p.x > width) p.x = 0
          if (p.y < 0) p.y = height
          if (p.y > height) p.y = 0
        }
        const twinkle = reduced ? 1 : 0.65 + 0.35 * Math.sin(p.tw + frame * 0.02)
        ctx.beginPath()
        ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2)
        ctx.fillStyle = `rgba(214, 232, 255, ${p.a * twinkle})`
        ctx.fill()
      }

      raf = requestAnimationFrame(draw)
    }

    setup()
    draw()
    window.addEventListener('resize', setup)
    return () => {
      cancelAnimationFrame(raf)
      window.removeEventListener('resize', setup)
    }
  }, [density])

  return <canvas ref={canvasRef} aria-hidden className={`pointer-events-none size-full ${className}`} />
}
