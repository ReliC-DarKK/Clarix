import { Analytics } from '@vercel/analytics/next'
import type { Metadata, Viewport } from 'next'
import { Space_Grotesk, JetBrains_Mono } from 'next/font/google'
import './globals.css'

const displayFont = Space_Grotesk({
  subsets: ['latin'],
  variable: '--font-display',
})

const technicalFont = JetBrains_Mono({
  subsets: ['latin'],
  variable: '--font-technical',
})

export const metadata: Metadata = {
  title: 'CLARIX — Super-Resolution Mapping for Satellite Imagery',
  description:
    'CLARIX enhances medium-resolution satellite imagery with AI super-resolution and generates spatial land-cover maps.',
  generator: 'v0.app',
  icons: {
    icon: [{ url: '/icon.svg', type: 'image/svg+xml' }],
    apple: '/apple-icon.png',
  },
}

export const viewport: Viewport = {
  colorScheme: 'dark',
  themeColor: '#080b12',
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="en" className={`bg-background ${displayFont.variable} ${technicalFont.variable}`}>
      <body className="font-sans antialiased">
        {children}
        {process.env.NODE_ENV === 'production' && <Analytics />}
      </body>
    </html>
  )
}
