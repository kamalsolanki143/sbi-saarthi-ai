'use client'
import { useEffect } from 'react'
import { Inter } from 'next/font/google'
import './globals.css'
import Sidebar from '@/components/shared/Sidebar'
import { useCustomerStore } from '@/store/useCustomerStore'
import { usePathname } from 'next/navigation'

const inter = Inter({ subsets: ['latin'], display: 'swap' })

const publicPaths = ['/', '/landing']
const appPaths = ['/dashboard', '/voice-banking', '/onboarding', '/consent', '/action-preview', '/audit-trail', '/settings', '/profile']

export default function RootLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname()
  const fetchCustomer = useCustomerStore((s) => s.fetchCustomer)
  const customer = useCustomerStore((s) => s.customer)
  const isPublic = publicPaths.includes(pathname)
  const isApp = appPaths.includes(pathname)

  useEffect(() => {
    if (isApp && !customer) {
      const customerId = process.env.NEXT_PUBLIC_DEMO_CUSTOMER_ID || 'CUST001'
      fetchCustomer(customerId)
    }
  }, [isApp, customer, fetchCustomer])

  if (isPublic) {
    return (
      <html lang="en">
        <body className={inter.className} style={{ background: '#0A1628' }}>
          {children}
        </body>
      </html>
    )
  }

  if (!customer && isApp) {
    return (
      <html lang="en">
        <body className={inter.className}>
          <div className="flex items-center justify-center h-screen bg-surface">
            <div className="flex items-center gap-3">
              <span className="w-3 h-3 rounded-full bg-accent animate-pulse" />
              <span className="text-sm text-text-muted">Loading Saarthi...</span>
            </div>
          </div>
        </body>
      </html>
    )
  }

  return (
    <html lang="en">
      <body className={inter.className}>
        <div className="flex min-h-screen">
          <Sidebar />
          <div className="ml-[248px] flex-1 flex flex-col min-h-screen">
            {children}
          </div>
        </div>
      </body>
    </html>
  )
}
