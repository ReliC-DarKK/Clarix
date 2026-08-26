'use client'

import Link from 'next/link'
import { useEffect, useState } from 'react'
import { Menu, X } from 'lucide-react'

const NAV_ITEMS = [
  { label: 'Technology', href: '/#technology' },
  { label: 'Workflow', href: '/#workflow' },
  { label: 'Results', href: '/#results' },
  { label: 'About', href: '/#about' },
]

function ClarixLogo() {
  return (
    <svg
      width="42"
      height="42"
      viewBox="0 0 48 48"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      aria-label="CLARIX logo"
      className="shrink-0"
    >
      {/* Outer angular C */}
      <path
        d="M33.5 7.5L20 2.5L7 11.5V36.5L20 45.5L33.5 40.5L27.5 34.5L20 37.5L13 32.5V15.5L20 10.5L27.5 13.5L33.5 7.5Z"
        stroke="#E8F0F5"
        strokeWidth="2"
        strokeLinejoin="miter"
      />

      {/* Cyan geometric layer */}
      <path
        d="M29.5 11L20 7.5L10.5 14V34L20 40.5L29.5 37L24 32L20 34L16 31V17L20 14L24 16L29.5 11Z"
        stroke="#27D7EA"
        strokeWidth="1.8"
        strokeLinejoin="miter"
      />

      {/* Inner C */}
      <path
        d="M25.5 16L20 14L16 17.5V30.5L20 34L25.5 31.5L22 28.5L21 29V19L22 19.5L25.5 16Z"
        stroke="#DDF9FF"
        strokeWidth="1.5"
        strokeLinejoin="miter"
      />

      {/* Small cyan accent */}
      <path
        d="M27.5 13.5L24 16"
        stroke="#27D7EA"
        strokeWidth="2"
        strokeLinecap="square"
      />
    </svg>
  )
}

export function Navigation() {
  const [scrolled, setScrolled] = useState(false)
  const [open, setOpen] = useState(false)

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 12)

    onScroll()

    window.addEventListener('scroll', onScroll, { passive: true })

    return () => window.removeEventListener('scroll', onScroll)
  }, [])

  return (
    <header
      className={`fixed inset-x-0 top-0 z-50 transition-colors duration-500 ${
        scrolled || open
          ? 'border-b border-border bg-background/80 backdrop-blur-xl'
          : 'border-b border-transparent'
      }`}
    >
      <nav
        aria-label="Primary"
        className="mx-auto flex h-16 max-w-[1400px] items-center justify-between gap-8 px-5 md:h-20 md:px-10"
      >
        {/* CLARIX BRAND */}
        <Link
          href="/"
          className="group flex items-center gap-2.5"
          onClick={() => setOpen(false)}
        >
          <ClarixLogo />

          <span className="font-mono text-sm font-semibold uppercase tracking-[0.42em] text-foreground">
            Clarix
          </span>
        </Link>

        {/* DESKTOP NAVIGATION */}
        <ul className="hidden items-center gap-9 md:flex">
          {NAV_ITEMS.map((item) => (
            <li key={item.label}>
              <Link
                href={item.href}
                className="font-mono text-[0.7rem] uppercase tracking-[0.2em] text-muted-foreground transition-colors hover:text-foreground"
              >
                {item.label}
              </Link>
            </li>
          ))}
        </ul>

        {/* RIGHT SIDE */}
        <div className="flex items-center gap-3">
          <Link
            href="/analysis"
            className="hidden rounded-sm border border-primary/50 bg-primary/10 px-5 py-2.5 font-mono text-[0.7rem] uppercase tracking-[0.2em] text-primary transition-colors hover:bg-primary hover:text-primary-foreground sm:inline-block"
          >
            Start Analysis
          </Link>

          {/* MOBILE MENU BUTTON */}
          <button
            type="button"
            onClick={() => setOpen((v) => !v)}
            aria-expanded={open}
            aria-label={open ? 'Close menu' : 'Open menu'}
            className="flex size-10 items-center justify-center rounded-sm border border-border text-foreground md:hidden"
          >
            {open ? (
              <X className="size-4" />
            ) : (
              <Menu className="size-4" />
            )}
          </button>
        </div>
      </nav>

      {/* MOBILE MENU */}
      {open && (
        <div className="border-t border-border bg-background/95 px-5 py-6 md:hidden">
          <ul className="flex flex-col gap-5">
            {NAV_ITEMS.map((item) => (
              <li key={item.label}>
                <Link
                  href={item.href}
                  onClick={() => setOpen(false)}
                  className="font-mono text-xs uppercase tracking-[0.24em] text-muted-foreground"
                >
                  {item.label}
                </Link>
              </li>
            ))}

            <li>
              <Link
                href="/analysis"
                onClick={() => setOpen(false)}
                className="inline-block rounded-sm border border-primary/50 bg-primary/10 px-5 py-2.5 font-mono text-[0.7rem] uppercase tracking-[0.2em] text-primary"
              >
                Start Analysis
              </Link>
            </li>
          </ul>
        </div>
      )}
    </header>
  )
}