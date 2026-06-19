'use client'
import { AgentName } from '@/types/agent'

const agentConfig: Record<AgentName, { label: string; bg: string; border: string; text: string }> = {
  mitra: { label: 'Mitra · Acquisition', bg: '#FAECE7', border: '#F0997B', text: '#712B13' },
  margdarshan: { label: 'Margdarshan · Adoption', bg: '#E1F5EE', border: '#5DCAA5', text: '#085041' },
  saathi: { label: 'Saathi · Engagement', bg: '#E6F1FB', border: '#85B7EB', text: '#0C447C' },
}

export default function AgentBadge({ agent, size = 'sm' }: { agent: AgentName; size?: 'sm' | 'md' }) {
  const cfg = agentConfig[agent]
  return (
    <span
      style={{ background: cfg.bg, borderColor: cfg.border, color: cfg.text }}
      className={`inline-flex items-center gap-1.5 rounded-badge font-medium leading-none ${
        size === 'sm' ? 'px-2.5 py-1 text-[10px]' : 'px-3 py-1.5 text-xs'
      } border`}
    >
      <span className="w-1.5 h-1.5 rounded-full" style={{ background: cfg.text }} />
      {cfg.label}
    </span>
  )
}
