'use client'
import { useState, useMemo } from 'react'
import { ShieldCheck, ShieldX } from 'lucide-react'
import { motion } from 'framer-motion'
import { AuditLog } from '@/types/audit'
import { AgentName } from '@/types/agent'

interface Props {
  logs: AuditLog[]
  loading?: boolean
}

const statusBadge: Record<string, string> = {
  success: 'bg-[#E1F5EE] text-[#085041]',
  rejected: 'bg-[#FCEBEB] text-[#791F1F]',
  pending: 'bg-[#FBF5E6] text-[#854F0B]',
}

export default function AuditTrail({ logs, loading }: Props) {
  const [agentFilter, setAgentFilter] = useState<AgentName | 'all'>('all')
  const [statusFilter, setStatusFilter] = useState<string>('all')

  const filtered = useMemo(() => {
    return logs.filter((log) => {
      if (agentFilter !== 'all' && log.agent !== agentFilter) return false
      if (statusFilter !== 'all' && log.status !== statusFilter) return false
      return true
    })
  }, [logs, agentFilter, statusFilter])

  if (loading) {
    return (
      <div className="space-y-3">
        {[1, 2, 3, 4, 5].map((i) => (
          <div key={i} className="h-14 skeleton rounded-card" />
        ))}
      </div>
    )
  }

  return (
    <div>
      {/* Filters */}
      <div className="flex items-center gap-3 mb-6">
        <select
          value={agentFilter}
          onChange={(e) => setAgentFilter(e.target.value as AgentName | 'all')}
          className="h-9 px-3 rounded-input border border-[rgba(26,58,92,0.15)] text-xs font-medium text-primary bg-white focus:border-primary focus:ring-[3px] focus:ring-[rgba(26,58,92,0.12)]"
        >
          <option value="all">All Agents</option>
          <option value="mitra">Mitra</option>
          <option value="margdarshan">Margdarshan</option>
          <option value="saathi">Saathi</option>
        </select>
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          className="h-9 px-3 rounded-input border border-[rgba(26,58,92,0.15)] text-xs font-medium text-primary bg-white focus:border-primary focus:ring-[3px] focus:ring-[rgba(26,58,92,0.12)]"
        >
          <option value="all">All Status</option>
          <option value="success">Success</option>
          <option value="rejected">Rejected</option>
          <option value="pending">Pending</option>
        </select>
        <span className="text-xs text-text-hint ml-auto">{filtered.length} entries</span>
      </div>

      {/* Table */}
      {filtered.length === 0 ? (
        <div className="text-center py-16">
          <p className="text-text-muted text-sm">No audit entries found.</p>
        </div>
      ) : (
        <div className="space-y-2">
          {filtered.map((log, idx) => (
            <motion.div
              key={log.id}
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: idx * 0.03 }}
              className="flex items-center gap-4 p-4 bg-white rounded-card border border-[rgba(26,58,92,0.10)] shadow-card"
            >
              <div className="min-w-[130px]">
                <span className="text-[11px] text-text-hint">
                  {new Date(log.timestamp).toLocaleString()}
                </span>
              </div>
              <div className="w-20">
                <span className="text-xs font-medium text-primary capitalize">{log.agent}</span>
              </div>
              <div className="flex-1 min-w-0">
                <span className="text-sm text-primary truncate block">{log.action}</span>
              </div>
              <div>
                <span
                  className={`text-[11px] font-medium px-2.5 py-1 rounded-badge ${statusBadge[log.status] || ''}`}
                >
                  {log.status}
                </span>
              </div>
              <div className="w-28">
                <div className="flex items-center gap-2">
                  <div className="flex-1 h-1.5 rounded-full bg-primary-light overflow-hidden">
                    <div
                      className="h-full rounded-full transition-all"
                      style={{
                        width: `${Math.round(log.confidence * 100)}%`,
                        background: log.confidence > 0.7 ? '#0F6E56' : log.confidence > 0.4 ? '#BA7517' : '#A32D2D',
                      }}
                    />
                  </div>
                  <span className="text-[10px] text-text-hint w-8 text-right">
                    {Math.round(log.confidence * 100)}%
                  </span>
                </div>
              </div>
              <div>
                {log.mpin_verified ? (
                  <ShieldCheck size={16} className="text-accent" />
                ) : (
                  <ShieldX size={16} className="text-danger" />
                )}
              </div>
            </motion.div>
          ))}
        </div>
      )}
    </div>
  )
}
