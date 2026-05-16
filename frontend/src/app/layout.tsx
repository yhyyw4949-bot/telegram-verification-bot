import type { Metadata } from 'next'
import './globals.css'
import { Toaster } from 'react-hot-toast'

export const metadata: Metadata = {
  title: 'VerifPlatform | منصة التوثيق',
  description: 'منصة التوثيق الاحترافية لمنصات العملات الرقمية',
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="ar" dir="rtl" className="dark">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@300;400;500;600;700;800&display=swap" rel="stylesheet" />
      </head>
      <body className="bg-dark-950 text-white antialiased">
        <Toaster position="top-center" toastOptions={{
          style: { background: '#1e293b', color: '#fff', border: '1px solid #334155' }
        }} />
        {children}
      </body>
    </html>
  )
}
