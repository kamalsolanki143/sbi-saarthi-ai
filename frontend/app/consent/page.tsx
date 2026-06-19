'use client'
import { motion } from 'framer-motion'
import { ShieldCheck } from 'lucide-react'
import TopBar from '@/components/shared/TopBar'
import ConsentManager from '@/components/ConsentManager/ConsentManager'
import { useT } from '@/services/translations'

const pageVariants = {
  initial: { opacity: 0, y: 16 },
  animate: { opacity: 1, y: 0, transition: { duration: 0.3, ease: [0.22, 1, 0.36, 1] } },
}

export default function ConsentPage() {
  const _t = useT()
  return (
    <>
      <TopBar title="Consent Manager" />
      <motion.div
        variants={pageVariants}
        initial="initial"
        animate="animate"
        className="flex-1 overflow-y-auto p-6"
      >
        {/* Header */}
        <div className="flex items-start gap-4 mb-8 max-w-2xl">
          <div className="w-10 h-10 rounded-full bg-accent-light flex items-center justify-center shrink-0">
            <ShieldCheck size={20} className="text-accent" />
          </div>
          <div>
            <h2 className="text-lg font-semibold text-primary">{_t('Your Consent, Your Control')}</h2>
            <p className="text-sm text-text-muted mt-1 leading-relaxed">
              In compliance with the DPDP Act, Saarthi AI requires your explicit consent before processing any voice data, storing conversation history, or generating personalized recommendations. You can review and revoke any consent at any time.
            </p>
          </div>
        </div>

        <ConsentManager />
      </motion.div>
    </>
  )
}
