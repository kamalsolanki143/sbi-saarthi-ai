'use client'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { LayoutDashboard, Mic, UserPlus, ScrollText, ShieldCheck, Settings } from 'lucide-react'
import { motion } from 'framer-motion'
import { useCustomerStore } from '@/store/useCustomerStore'
import CustomerCard from '@/components/CustomerCard/CustomerCard'
import { useT } from '@/services/translations'

const navItems = [
  { href: '/dashboard', key: 'Dashboard', icon: LayoutDashboard },
  { href: '/voice-banking', key: 'Voice Banking', icon: Mic },
  { href: '/onboarding', key: 'Onboarding', icon: UserPlus },
  { href: '/audit-trail', key: 'Audit Trail', icon: ScrollText },
  { href: '/consent', key: 'Consent', icon: ShieldCheck },
  { href: '/settings', key: 'Settings', icon: Settings },
]

export default function Sidebar() {
  const pathname = usePathname()
  const customer = useCustomerStore((s) => s.customer)
  const _t = useT()

  return (
    <aside className="fixed left-0 top-0 h-full w-[248px] bg-primary flex flex-col z-50">
      <div className="h-16 flex items-center px-6 border-b border-white/10 shrink-0">
        <span className="text-gold font-bold text-xl tracking-tight">
          SAARTHI
          <sup className="text-white/60 text-[10px] ml-0.5">AI</sup>
        </span>
      </div>

      <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
        {navItems.map((item) => {
          const isActive = pathname === item.href || pathname.startsWith(item.href + '/')
          const Icon = item.icon
          return (
            <Link key={item.href} href={item.href}>
              <div
                className={`relative flex items-center gap-3 h-10 px-4 rounded-lg text-sm transition-colors duration-150 ${
                  isActive
                    ? 'bg-[rgba(15,110,86,0.25)] text-white'
                    : 'text-white/70 hover:bg-[rgba(255,255,255,0.07)] hover:text-white'
                }`}
              >
                {isActive && (
                  <motion.div
                    layoutId="nav-indicator"
                    className="absolute left-0 top-1/2 -translate-y-1/2 w-[3px] h-5 bg-accent rounded-r-sm"
                  />
                )}
                <Icon size={18} />
                <span>{_t(item.key)}</span>
              </div>
            </Link>
          )
        })}
      </nav>

      <div className="p-3 border-t border-white/10 shrink-0">
        {customer ? (
          <div className="bg-primary-dark/60 rounded-card p-3">
            <CustomerCard compact />
          </div>
        ) : (
          <div className="text-white/40 text-xs text-center py-2">{_t('No pending action')}</div>
        )}
      </div>
    </aside>
  )
}
