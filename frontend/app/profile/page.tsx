'use client'
import { motion } from 'framer-motion'
import { ArrowUpRight, ArrowDownRight } from 'lucide-react'
import TopBar from '@/components/shared/TopBar'
import CustomerCard from '@/components/CustomerCard/CustomerCard'
import { useCustomerStore } from '@/store/useCustomerStore'
import { MOCK_TRANSACTIONS } from '@/services/mockData'
import { useState, useEffect } from 'react'
import { Transaction } from '@/types/transaction'
import { useT } from '@/services/translations'

const pageVariants = {
  initial: { opacity: 0, y: 16 },
  animate: { opacity: 1, y: 0, transition: { duration: 0.3, ease: [0.22, 1, 0.36, 1] } },
}

export default function Profile() {
  const customer = useCustomerStore((s) => s.customer)
  const [txns] = useState<Transaction[]>(MOCK_TRANSACTIONS)
  const _t = useT()

  if (!customer) return null

  return (
    <>
      <TopBar title="Profile" />
      <motion.div
        variants={pageVariants}
        initial="initial"
        animate="animate"
        className="flex-1 overflow-y-auto p-6 max-w-2xl"
      >
        <CustomerCard />

        {/* Transaction history */}
        <div className="mt-6">
          <h3 className="text-sm font-semibold text-primary mb-4 tracking-tight">{_t('Transaction History')}</h3>
          <div className="space-y-2">
            {txns.map((txn, idx) => (
              <motion.div
                key={txn.id}
                initial={{ opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: idx * 0.03 }}
                className="flex items-center justify-between p-4 bg-white rounded-card border border-[rgba(26,58,92,0.10)] shadow-card"
              >
                <div className="flex items-center gap-3">
                  <div className={`w-9 h-9 rounded-full flex items-center justify-center ${
                    txn.type === 'credit' ? 'bg-accent-light' : 'bg-[#FCEBEB]'
                  }`}>
                    {txn.type === 'credit' ? (
                      <ArrowUpRight size={16} className="text-accent-dark" />
                    ) : (
                      <ArrowDownRight size={16} className="text-danger" />
                    )}
                  </div>
                  <div>
                    <p className="text-sm text-primary font-medium">{txn.description}</p>
                    <span className="text-[11px] text-text-hint">{new Date(txn.date).toLocaleDateString()} · {txn.category}</span>
                  </div>
                </div>
                <span className={`text-sm font-semibold tabular-nums ${
                  txn.type === 'credit' ? 'text-accent-dark' : 'text-danger'
                }`}>
                  {txn.type === 'credit' ? '+' : '-'}₹{txn.amount.toLocaleString()}
                </span>
              </motion.div>
            ))}
          </div>
        </div>
      </motion.div>
    </>
  )
}
