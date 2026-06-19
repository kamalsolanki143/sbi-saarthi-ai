'use client'
import { motion } from 'framer-motion'
import { AgentName } from '@/types/agent'

const agentColors: Record<AgentName, string> = {
  mitra: '#F0997B',
  margdarshan: '#5DCAA5',
  saathi: '#85B7EB',
}

export default function AgentTypingIndicator({ agent = 'margdarshan' }: { agent?: AgentName }) {
  const color = agentColors[agent]
  return (
    <div className="flex items-center gap-3 px-1 py-3">
      <div className="flex items-center gap-1">
        {[0, 1, 2].map((i) => (
          <motion.span
            key={i}
            className="w-2 h-2 rounded-full"
            style={{ background: color }}
            animate={{ y: [0, -6, 0] }}
            transition={{ duration: 0.6, repeat: Infinity, delay: i * 0.15 }}
          />
        ))}
      </div>
      <span className="text-xs text-text-muted">Thinking...</span>
    </div>
  )
}
