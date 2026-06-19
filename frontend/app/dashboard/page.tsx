'use client'
import { useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import { ArrowUpRight, ArrowDownRight, Banknote, Briefcase, Bell, Activity } from 'lucide-react'
import { useRouter } from 'next/navigation'
import TopBar from '@/components/shared/TopBar'
import CustomerCard from '@/components/CustomerCard/CustomerCard'
import { useCustomerStore } from '@/store/useCustomerStore'
import { useCountUp } from '@/hooks/useCountUp'
import { api } from '@/services/api'
import AgentBadge from '@/components/shared/AgentBadge'
import { AgentName } from '@/types/agent'
import { MOCK_RECOMMENDATIONS } from '@/services/mockData'
import { useT } from '@/services/translations'

const pageVariants = {
  initial: { opacity: 0, y: 16 },
  animate: { opacity: 1, y: 0, transition: { duration: 0.3, ease: [0.22, 1, 0.36, 1] } },
}

const containerVariants = {
  animate: { transition: { staggerChildren: 0.07 } },
}

const itemVariants = {
  initial: { opacity: 0, y: 12 },
  animate: { opacity: 1, y: 0, transition: { duration: 0.25, ease: 'easeOut' } },
}

export default function Dashboard() {
  const customer = useCustomerStore((s) => s.customer)
  const router = useRouter()
  const [recs, setRecs] = useState<any[]>([])
  const _t = useT()
  const balance = useCountUp(customer?.balance || 0)

  useEffect(() => {
    if (!customer) return
    api.getRecommendations(customer.id).then((res) => {
      if (res.data.length > 0) setRecs(res.data)
      else setRecs(MOCK_RECOMMENDATIONS)
    }).catch(() => {
      setRecs(MOCK_RECOMMENDATIONS)
    })
  }, [customer])

  if (!customer) return null

  const metrics = [
    { label: _t('Balance'), value: `₹${balance.toLocaleString()}`, icon: Banknote, color: '#1A3A5C', prefix: true },
    { label: _t('Active Products'), value: customer.active_products.length.toString(), icon: Briefcase, color: '#0F6E56', change: _t('+1 this month') },
    { label: _t('Pending Actions'), value: '1', icon: Bell, color: '#BA7517', change: _t('Idle balance FD') },
    { label: _t('Last Activity'), value: 'Today', icon: Activity, color: '#5C6F82', sub: '6:30 AM' },
  ]

  return (
    <>
      <TopBar title={_t('Dashboard')} />
      <motion.div
        variants={pageVariants}
        initial="initial"
        animate="animate"
        className="flex-1 overflow-y-auto p-6"
      >
        {/* Greeting */}
        <div className="mb-6">
          <h2 className="text-2xl font-bold text-primary tracking-tight">
            Namaste, {customer.name_hindi || customer.name}
          </h2>
          <div className="w-12 h-0.5 bg-gold mt-2 rounded-full" />
        </div>

        {/* Customer card */}
        <motion.div variants={itemVariants} className="mb-6 max-w-2xl">
          <CustomerCard />
        </motion.div>

        {/* Metrics grid */}
        <motion.div
          variants={containerVariants}
          className="grid grid-cols-4 gap-4 mb-8"
        >
          {metrics.map((m) => (
            <motion.div
              key={m.label}
              variants={itemVariants}
              whileHover={{ y: -3, boxShadow: '0 8px 24px rgba(13,27,42,0.12)' }}
              transition={{ duration: 0.2 }}
              className="bg-white rounded-card shadow-card border border-[rgba(26,58,92,0.10)] p-5 relative overflow-hidden"
            >
              <div
                className="absolute left-0 top-0 bottom-0 w-1 rounded-l-sm"
                style={{ background: m.color }}
              />
              <div className="flex items-start justify-between mb-1">
                <span className="text-[11px] uppercase tracking-wider text-text-muted font-medium">
                  {m.label}
                </span>
                <m.icon size={16} style={{ color: m.color }} />
              </div>
              <div className="text-2xl font-bold text-primary tabular-nums mb-1">
                {m.prefix ? m.value : m.value}
              </div>
              {(m as any).change && (
                <div className="flex items-center gap-1">
                  <ArrowUpRight size={12} className="text-accent" />
                  <span className="text-[11px] text-accent">{(m as any).change}</span>
                </div>
              )}
              {(m as any).sub && (
                <span className="text-[11px] text-text-hint">{(m as any).sub}</span>
              )}
            </motion.div>
          ))}
        </motion.div>

        <div className="grid grid-cols-5 gap-6">
          {/* Recent activity */}
          <div className="col-span-3">
            <h3 className="text-sm font-semibold text-primary mb-4 tracking-tight">{_t('Recent Agent Activity')}</h3>
            <div className="space-y-2">
              {[
                { agent: 'margdarshan' as AgentName, action: 'Idle balance detected — FD recommendation generated', time: '2 min ago', status: 'pending' as const },
                { agent: 'saathi' as AgentName, action: 'Spending pattern analyzed — no unusual activity', time: '1 day ago', status: 'success' as const },
                { agent: 'mitra' as AgentName, action: 'KYC document verification completed', time: '3 days ago', status: 'success' as const },
              ].map((act, idx) => (
                <motion.div
                  key={idx}
                  initial={{ opacity: 0, y: 8 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: idx * 0.05 }}
                  className="flex items-center gap-4 p-4 bg-white rounded-card border border-[rgba(26,58,92,0.10)] shadow-card"
                >
                  <AgentBadge agent={act.agent} size="sm" />
                  <div className="flex-1 min-w-0">
                    <p className="text-sm text-primary truncate">{act.action}</p>
                  </div>
                  <span className="text-[11px] text-text-hint shrink-0">{act.time}</span>
                  <span className={`text-[10px] font-medium px-2 py-0.5 rounded-badge ${
                    act.status === 'success' ? 'bg-accent-light text-accent-dark' : 'bg-gold-light text-warning'
                  }`}>
                    {act.status}
                  </span>
                </motion.div>
              ))}
            </div>
          </div>

          {/* Recommendations */}
          <div className="col-span-2">
            <h3 className="text-sm font-semibold text-primary mb-4 tracking-tight">{_t('Recommendations')}</h3>
            <div className="space-y-3">
              {recs.map((rec, idx) => (
                <motion.div
                  key={rec.id || idx}
                  initial={{ opacity: 0, y: 8 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: idx * 0.05 }}
                  whileHover={{ y: -2 }}
                  className="bg-white rounded-card shadow-card border border-[rgba(26,58,92,0.10)] p-4"
                >
                  <AgentBadge agent={rec.agent as AgentName} size="sm" />
                  <p className="text-sm text-primary mt-2 leading-relaxed">{rec.text}</p>
                  <button
                    onClick={() => router.push('/voice-banking')}
                    className="mt-3 text-xs font-medium text-accent hover:text-accent-dark transition-colors"
                  >
                    {_t('Ask Saarthi')} &rarr;
                  </button>
                </motion.div>
              ))}
            </div>
          </div>
        </div>
      </motion.div>
    </>
  )
}
