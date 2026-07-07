import type { Metadata } from 'next'
import './globals.css'
import { I18nProvider } from '@/i18n/I18nProvider'
import ChatPanel from '@/components/ChatPanel'

export const metadata: Metadata = {
  title: 'Baholash Platformasi',
  description: 'Professional Baholovchilar Uchun Avtomatlashtirilgan Veb Platforma',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body suppressHydrationWarning>
        <I18nProvider>
          {children}
          <ChatPanel />
        </I18nProvider>
      </body>
    </html>
  )
}
