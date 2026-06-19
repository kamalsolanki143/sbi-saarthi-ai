'use client'
import { motion } from 'framer-motion'
import { ActionPayload, AgentName } from '@/types/agent'
import AgentBadge from '@/components/shared/AgentBadge'

interface Props {
  action: ActionPayload
  agent: AgentName
  onAuthorize: () => void
  onDecline: () => void
}

const riskColors: Record<string, { bg: string; text: string }> = {
  low: { bg: '#E1F5EE', text: '#085041' },
  medium: { bg: '#FBF5E6', text: '#854F0B' },
  high: { bg: '#FCEBEB', text: '#791F1F' },
}

export default function ActionPreview({ action, agent, onAuthorize, onDecline }: Props) {
  const risk = riskColors[action.risk_level || 'low']

  return (
    <div className="h-full flex flex-col">
      {/* Gold top border */}
      <div className="w-full h-[3px] bg-gold pulsate-border shrink-0" />

      <div className="flex-1 p-6 space-y-6 overflow-y-auto">
        {/* Agent badge */}
        <AgentBadge agent={agent} size="md" />

        {/* Action headline */}
        <h2 className="text-2xl font-bold text-primary tracking-tight">
          {action.display_label}
        </h2>

        {/* Details grid */}
        <div className="bg-surface rounded-card border border-[rgba(26,58,92,0.08)] divide-y divide-[rgba(26,58,92,0.06)]">
          {[
            { label: 'Amount', value: action.amount ? `₹${action.amount.toLocaleString()}` : '-' },
            { label: 'Product', value: action.product || '-' },
            { label: 'Duration', value: action.duration || '-' },
            { label: 'Interest Rate', value: action.interest_rate ? `${action.interest_rate}%` : '-' },
          ].map((row) => (
            <div key={row.label} className="flex items-center justify-between px-5 py-3.5">
              <span className="text-xs uppercase tracking-wider text-text-muted">{row.label}</span>
              <span className="text-sm font-semibold text-primary tabular-nums">{row.value}</span>
            </div>
          ))}
        </div>

        {/* Risk badge */}
        <div className="flex items-center justify-between">
          <span className="text-xs text-text-muted uppercase tracking-wider">Risk Level</span>
          <span
            className="text-[11px] font-medium px-3 py-1 rounded-badge"
            style={{ background: risk.bg, color: risk.text }}
          >
            {action.risk_level ? `${action.risk_level.charAt(0).toUpperCase() + action.risk_level.slice(1)} risk` : '-'}
          </span>
        </div>

        {/* Action buttons */}
        <div className="space-y-3 pt-4">
          <motion.button
            onClick={onAuthorize}
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.97 }}
            className="w-full h-11 rounded-input bg-accent text-white font-medium text-sm hover:bg-accent-dark transition-colors"
          >
            Authorize with MPIN
          </motion.button>
          <motion.button
            onClick={onDecline}
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.97 }}
            className="w-full h-11 rounded-input bg-transparent border border-[rgba(163,45,45,0.25)] text-danger font-medium text-sm hover:bg-[#FFF0F0] transition-colors"
          >
            Decline
          </motion.button>
        </div>
      </div>
    </div>
  )
}
