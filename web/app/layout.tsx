import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import '@blueprintjs/core/lib/css/blueprint.css'
import '@blueprintjs/icons/lib/css/blueprint-icons.css'
import './globals.css'
import BlueprintSetup from '@/components/ui/BlueprintSetup'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'First Responder Risk Monitoring',
  description: 'Real-time monitoring system for first responders',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className="bp6-dark">
      <body className={`${inter.className}`}>
        <BlueprintSetup />
        <div className="min-h-screen">
          {children}
        </div>
      </body>
    </html>
  )
}
