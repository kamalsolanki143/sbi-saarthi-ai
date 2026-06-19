'use client'
import { useEffect } from 'react'
import { motion } from 'framer-motion'
import { ScrollText } from 'lucide-react'
import TopBar from '@/components/shared/TopBar'
import AuditTrail from '@/components/AuditTrail/AuditTrail'
import { useAuditStore } from '@/store/useAuditStore'
import { useCustomerStore } from '@/store/useCustomerStore'
import { useT } from '@/services/translations'

const pageVariants = {
  initial: { opacity: 0, y: 16 },
  animate: { opacity: 1, y: 0, transition: { duration: 0.3, ease: [0.22, 1, 0.36, 1] } },
}

export default function AuditTrailPage() {
  const { logs, loading, fetchLogs } = useAuditStore()
  const customer = useCustomerStore((s) => s.customer)
  const _t = useT()

  useEffect(() => {
    if (customer) fetchLogs(customer.id)
  }, [customer, fetchLogs])

  return (
    <>
      <TopBar title="Audit Trail" />
      <motion.div
        variants={pageVariants}
        initial="initial"
        animate="animate"
        className="flex-1 overflow-y-auto p-6"
      >
        <div className="flex items-start gap-4 mb-8">
          <div className="w-10 h-10 rounded-full bg-primary-light flex items-center justify-center shrink-0">
            <ScrollText size={20} className="text-primary" />
          </div>
          <div>
            <h2 className="text-lg font-semibold text-primary">{_t('Every AI action is logged and auditable.')}</h2>
            <p className="text-sm text-text-muted mt-1">
              All decisions, recommendations, and actions taken by Saarthi AI agents are recorded with timestamps, confidence scores, and MPIN verification status.
            </p>
          </div>
        </div>

        <AuditTrail logs={logs} loading={loading} />
      </motion.div>
    </>
  )
}
