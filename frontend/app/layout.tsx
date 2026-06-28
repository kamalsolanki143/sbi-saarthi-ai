'use client'

import { Inter } from 'next/font/google'
import './globals.css'
import Sidebar from '@/components/shared/Sidebar'
import { usePathname } from 'next/navigation'
import { useEffect } from 'react'
import { useCustomerStore } from '@/store/useCustomerStore'

const inter = Inter({
  subsets: ['latin'],
  display: 'swap',
})

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const pathname = usePathname()

  const fetchCustomer = useCustomerStore((s) => s.fetchCustomer)
  const customer = useCustomerStore((s) => s.customer)

  const isDashboard = pathname?.startsWith('/dashboard')

  useEffect(() => {
    if (isDashboard && !customer) {
      const customerId =
        process.env.NEXT_PUBLIC_DEMO_CUSTOMER_ID || 'CUST001'

      fetchCustomer(customerId)
    }
  }, [isDashboard, customer, fetchCustomer])

  return (
    <html lang="en">
      <body className={inter.className}>
        {/* DASHBOARD LAYOUT */}
        {isDashboard ? (
          <div className="flex min-h-screen bg-white">
            <Sidebar />
            <div className="ml-[248px] flex-1 flex flex-col min-h-screen">
              {children}
            </div>
          </div>
        ) : (
          /* ALL OTHER PAGES */
          <div>{children}</div>
        )}
      </body>
    </html>
  )
}