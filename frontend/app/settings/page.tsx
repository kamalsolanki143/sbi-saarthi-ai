'use client'
import { useState } from 'react'
import { motion } from 'framer-motion'
import { Bell, Languages, Trash2, ShieldCheck } from 'lucide-react'
import TopBar from '@/components/shared/TopBar'
import LanguageSelector from '@/components/LanguageSelector/LanguageSelector'
import { useCustomerStore } from '@/store/useCustomerStore'
import { api } from '@/services/api'
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

export default function Settings() {
  const customer = useCustomerStore((s) => s.customer)
  const [clearing, setClearing] = useState(false)
  const [cleared, setCleared] = useState(false)
  const _t = useT()

  const handleClearMemory = async () => {
    if (!customer) return
    setClearing(true)
    try {
      await api.clearMemory(customer.id)
      setCleared(true)
      setTimeout(() => setCleared(false), 3000)
    } catch {}
    setClearing(false)
  }

  return (
    <>
      <TopBar title="Settings" />
      <motion.div
        variants={pageVariants}
        initial="initial"
        animate="animate"
        className="flex-1 overflow-y-auto p-6 max-w-2xl"
      >
        <motion.div variants={containerVariants} className="space-y-6">
          {/* Language */}
          <motion.div variants={itemVariants} className="bg-white rounded-card shadow-card border border-[rgba(26,58,92,0.10)] p-5">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-9 h-9 rounded-full bg-primary-light flex items-center justify-center">
                <Languages size={18} className="text-primary" />
              </div>
              <h3 className="text-sm font-semibold text-primary">{_t('Language Preferences')}</h3>
            </div>
            <LanguageSelector />
          </motion.div>

          {/* Notifications */}
          <motion.div variants={itemVariants} className="bg-white rounded-card shadow-card border border-[rgba(26,58,92,0.10)] p-5">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-9 h-9 rounded-full bg-primary-light flex items-center justify-center">
                <Bell size={18} className="text-primary" />
              </div>
              <h3 className="text-sm font-semibold text-primary">{_t('Notification Preferences')}</h3>
            </div>
            <div className="space-y-3">
              {[
                { label: 'Agent recommendations', enabled: true },
                { label: 'Transaction alerts', enabled: true },
                { label: 'Daily financial summary', enabled: false },
                { label: 'Low balance warnings', enabled: true },
              ].map((notif) => (
                <div key={notif.label} className="flex items-center justify-between">
                  <span className="text-sm text-primary">{notif.label}</span>
                  <div className={`w-9 h-5 rounded-full transition-colors relative cursor-pointer ${notif.enabled ? 'bg-accent' : 'bg-[rgba(26,58,92,0.15)]'}`}>
                    <div className={`absolute top-0.5 w-4 h-4 rounded-full bg-white shadow-sm transition-transform ${notif.enabled ? 'translate-x-[18px]' : 'translate-x-0.5'}`} />
                  </div>
                </div>
              ))}
            </div>
          </motion.div>

          {/* Data & Privacy */}
          <motion.div variants={itemVariants} className="bg-white rounded-card shadow-card border border-[rgba(26,58,92,0.10)] p-5">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-9 h-9 rounded-full bg-primary-light flex items-center justify-center">
                <ShieldCheck size={18} className="text-primary" />
              </div>
              <h3 className="text-sm font-semibold text-primary">{_t('Data & Privacy')}</h3>
            </div>
            <p className="text-xs text-text-muted mb-4 leading-relaxed">
              Your conversation history and preferences are stored securely. You can clear your memory at any time.
            </p>
            <motion.button
              onClick={handleClearMemory}
              disabled={clearing}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.97 }}
              className="flex items-center gap-2 h-10 px-4 rounded-input border border-danger/25 text-danger text-sm font-medium hover:bg-[#FFF0F0] transition-colors disabled:opacity-45"
            >
              <Trash2 size={16} />
              {clearing ? 'Clearing...' : _t('Clear my conversation memory')}
            </motion.button>
            {cleared && (
              <motion.p
                initial={{ opacity: 0, y: 4 }}
                animate={{ opacity: 1, y: 0 }}
                className="text-xs text-accent mt-2"
              >
                Memory cleared successfully.
              </motion.p>
            )}
          </motion.div>
        </motion.div>
      </motion.div>
    </>
  )
}
