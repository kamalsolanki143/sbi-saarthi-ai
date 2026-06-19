'use client'
import { Bell } from 'lucide-react'
import LanguageSelector from '@/components/LanguageSelector/LanguageSelector'
import NetworkStatus from '@/components/NetworkStatus/NetworkStatus'
import { useT } from '@/services/translations'

interface TopBarProps {
  title: string
}

export default function TopBar({ title }: TopBarProps) {
  const _t = useT()
  return (
    <header className="h-14 bg-white border-b border-[rgba(26,58,92,0.08)] flex items-center justify-between px-6 shrink-0 shadow-[0_1px_0_rgba(26,58,92,0.06)]">
      <h1 className="text-base font-semibold text-primary tracking-tight">{_t(title)}</h1>
      <div className="flex items-center gap-4">
        <NetworkStatus />
        <LanguageSelector />
        <button className="relative p-1.5 rounded-lg hover:bg-primary-light transition-colors text-text-muted hover:text-primary">
          <Bell size={18} />
          <span className="absolute -top-0.5 -right-0.5 w-2 h-2 bg-danger rounded-full" />
        </button>
      </div>
    </header>
  )
}
