'use client'
import { useState, useEffect } from 'react'
import { ShieldCheck, ShieldX, Clock } from 'lucide-react'
import { motion } from 'framer-motion'
import { ConsentRecord } from '@/types/consent'
import { api } from '@/services/api'
import { useCustomerStore } from '@/store/useCustomerStore'

export default function ConsentManager() {
  const customer = useCustomerStore((s) => s.customer)
  const [records, setRecords] = useState<ConsentRecord[]>([])
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (!customer) return
    setLoading(true)
    api.getConsent(customer.id).then((res) => {
      setRecords(res.data)
      setLoading(false)
    }).catch(() => setLoading(false))
  }, [customer])

  const handleRevoke = async (record: ConsentRecord) => {
    if (!customer) return
    await api.recordConsent(customer.id, record.action_type, false)
    setRecords((prev) =>
      prev.map((r) => (r.id === record.id ? { ...r, granted: false } : r))
    )
  }

  const active = records.filter((r) => r.granted)
  const expired = records.filter((r) => !r.granted && new Date(r.expires_at) < new Date())

  if (loading) {
    return (
      <div className="space-y-3">
        {[1, 2, 3].map((i) => (
          <div key={i} className="h-16 skeleton rounded-card" />
        ))}
      </div>
    )
  }

  if (records.length === 0) {
    return (
      <div className="text-center py-16">
        <ShieldCheck size={40} className="mx-auto text-text-hint mb-3" />
        <p className="text-text-muted text-sm">No consent records yet. Actions you authorize will appear here.</p>
      </div>
    )
  }

  return (
    <div className="space-y-8">
      {active.length > 0 && (
        <Section title="Active" count={active.length} color="accent" icon={<ShieldCheck size={16} className="text-accent" />}>
          {active.map((record) => (
            <RecordRow key={record.id} record={record} onRevoke={handleRevoke} />
          ))}
        </Section>
      )}

      {expired.length > 0 && (
        <Section title="Expired" count={expired.length} color="text-muted" icon={<Clock size={16} className="text-text-muted" />}>
          {expired.map((record) => (
            <RecordRow key={record.id} record={record} />
          ))}
        </Section>
      )}

      {records.filter((r) => !r.granted && new Date(r.expires_at) >= new Date()).length > 0 && (
        <Section title="Revoked" count={records.filter((r) => !r.granted && new Date(r.expires_at) >= new Date()).length} color="danger" icon={<ShieldX size={16} className="text-danger" />}>
          {records.filter((r) => !r.granted && new Date(r.expires_at) >= new Date()).map((record) => (
            <RecordRow key={record.id} record={record} />
          ))}
        </Section>
      )}
    </div>
  )
}

function Section({ title, count, color, icon, children }: { title: string; count: number; color: string; icon: React.ReactNode; children: React.ReactNode }) {
  return (
    <div>
      <div className="flex items-center gap-2 mb-3">
        {icon}
        <h3 className="text-sm font-semibold" style={{ color: `var(--${color})` }}>{title}</h3>
        <span className="text-xs text-text-hint">({count})</span>
      </div>
      <div className="space-y-2">{children}</div>
    </div>
  )
}

function RecordRow({ record, onRevoke }: { record: ConsentRecord; onRevoke?: (r: ConsentRecord) => void }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      className="flex items-center justify-between p-4 bg-white rounded-card border border-[rgba(26,58,92,0.10)] shadow-card"
    >
      <div>
        <p className="text-sm font-medium text-primary capitalize">{record.action_type.replace(/_/g, ' ')}</p>
        <div className="flex items-center gap-3 mt-1">
          <span className={`text-[11px] px-2 py-0.5 rounded-badge font-medium ${
            record.granted ? 'bg-accent-light text-accent-dark' : 'bg-[#FCEBEB] text-danger'
          }`}>
            {record.granted ? 'Active' : 'Revoked'}
          </span>
          <span className="text-[11px] text-text-hint">
            {new Date(record.timestamp).toLocaleDateString()}
          </span>
          <span className="text-[11px] text-text-hint">
            Expires: {new Date(record.expires_at).toLocaleDateString()}
          </span>
        </div>
      </div>
      {record.granted && onRevoke && (
        <button
          onClick={() => onRevoke(record)}
          className="text-xs text-danger font-medium px-3 py-1.5 rounded-lg hover:bg-[#FFF0F0] transition-colors"
        >
          Revoke
        </button>
      )}
    </motion.div>
  )
}
