'use client'

import { useEffect } from 'react'
import { motion } from 'framer-motion'
import { useRouter } from 'next/navigation'

import TopBar from '@/components/shared/TopBar'
import ActionPreview from '@/components/ActionPreview/ActionPreview'
import MPINVerification from '@/components/MPINVerification/MPINVerification'

import { useAgentStore } from '@/store/useAgentStore'

const pageVariants = {
  initial: { opacity: 0, y: 16 },
  animate: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.3, ease: [0.22, 1, 0.36, 1] },
  },
}

export default function ActionPreviewPage() {
  const router = useRouter()

  const {
    pendingAction,
    awaitingMPIN,
    setAwaitingMPIN,
    setPendingAction,
    activeAgent,
  } = useAgentStore()

  // ✅ Fallback: if Zustand is empty, load from localStorage
  useEffect(() => {
    if (!pendingAction) {
      const stored = localStorage.getItem('activeAction')

      if (stored) {
        const parsed = JSON.parse(stored)

        setPendingAction({
          ...parsed,
          display_label: parsed.title,
        })
      }
    }
  }, [pendingAction, setPendingAction])

  // ❌ No action state
  if (!pendingAction) {
    return (
      <>
        <TopBar title="Action Preview" />

        <motion.div
          variants={pageVariants}
          initial="initial"
          animate="animate"
          className="flex-1 flex items-center justify-center"
        >
          <p className="text-gray-500 text-sm">
            No pending action. Please start from Quick Actions or Voice Banking.
          </p>
        </motion.div>
      </>
    )
  }

  return (
    <>
      <TopBar title="Action Preview" />

      <motion.div
        variants={pageVariants}
        initial="initial"
        animate="animate"
        className="flex-1 overflow-y-auto p-6 max-w-lg mx-auto"
      >
        {/* Action Preview Card */}
        <ActionPreview
          action={pendingAction}
          agent={(activeAgent as any) || 'margdarshan'}
          onAuthorize={() => setAwaitingMPIN(true)}
          onDecline={() => {
            setPendingAction(null)
            router.push('/dashboard')
          }}
        />

        {/* MPIN Verification Layer */}
        {awaitingMPIN && (
          <MPINVerification
            actionLabel={pendingAction.display_label || pendingAction.title}
            onSuccess={() => {
              setAwaitingMPIN(false)
              setPendingAction(null)
              router.push('/dashboard')
            }}
            onCancel={() => setAwaitingMPIN(false)}
          />
        )}
      </motion.div>
    </>
  )
}