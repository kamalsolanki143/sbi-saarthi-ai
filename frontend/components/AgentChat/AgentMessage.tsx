'use client'
import { motion } from 'framer-motion'
import { AgentMessage as AgentMessageType } from '@/types/agent'
import AgentBadge from '@/components/shared/AgentBadge'
import ConfidenceFallback from '@/components/ConfidenceFallback/ConfidenceFallback'

const agentLeftBorders: Record<string, string> = {
  mitra: '#F0997B',
  margdarshan: '#5DCAA5',
  saathi: '#85B7EB',
}

export default function AgentMessage({ message, isLatest }: { message: AgentMessageType; isLatest?: boolean }) {
  const isAgent = message.type !== 'completed' && message.type !== 'error'
  const showBadge = isAgent && isLatest

  const messageStyle = isAgent
    ? {
        alignSelf: 'flex-start' as const,
        background: '#FFFFFF',
        borderLeft: `4px solid ${agentLeftBorders[message.agent] || '#5DCAA5'}`,
        boxShadow: '0 1px 3px rgba(13,27,42,0.06), 0 4px 12px rgba(13,27,42,0.05)',
        borderTopRightRadius: '14px',
        borderBottomRightRadius: '14px',
        borderTopLeftRadius: '4px',
        borderBottomLeftRadius: '14px',
        maxWidth: '75%',
      }
    : {
        alignSelf: 'flex-end' as const,
        background: '#1A3A5C',
        color: '#FFFFFF',
        borderTopLeftRadius: '14px',
        borderTopRightRadius: '14px',
        borderBottomLeftRadius: '14px',
        borderBottomRightRadius: '4px',
        maxWidth: '75%',
      }

  return (
    <motion.div
      initial={{ opacity: 0, x: isAgent ? -20 : 20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ type: 'spring', stiffness: 300, damping: 28 }}
      className="mb-4"
    >
      {showBadge && (
        <div className="mb-1.5 ml-1">
          <AgentBadge agent={message.agent} size="sm" />
        </div>
      )}
      <div style={messageStyle} className="px-4 py-3">
        <p
          className={`text-sm leading-relaxed ${
            message.language === 'hi' || message.language === 'bn' || message.language === 'ta'
              ? 'font-devanagari text-[15px] leading-[1.8]'
              : ''
          } ${!isAgent ? 'text-white' : 'text-primary'}`}
        >
          {message.content}
        </p>
      </div>
      <div className={`flex items-center gap-2 mt-1 ${isAgent ? '' : 'justify-end'}`}>
        <span className="text-[11px] text-text-hint">
          {new Date(message.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
        </span>
        {message.confidence >= 0 && (
          <span className="text-[10px] text-text-hint">
            Confidence: {Math.round(message.confidence * 100)}%
          </span>
        )}
      </div>
      {message.confidence < 0.7 && (
        <ConfidenceFallback confidence={message.confidence} />
      )}
    </motion.div>
  )
}
