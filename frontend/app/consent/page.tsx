'use client'

import { useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import { useRouter } from 'next/navigation'
import { ShieldCheck } from 'lucide-react'

import TopBar from '@/components/shared/TopBar'
import { api } from '@/services/api'

const pageVariants = {
  initial: { opacity: 0, y: 16 },
  animate: {
    opacity: 1,
    y: 0,
    transition: {
      duration: 0.3,
      ease: [0.22, 1, 0.36, 1],
    },
  },
}

export default function ConsentPage() {
  const router = useRouter()

  const [accepted, setAccepted] = useState(false)
  const [action, setAction] = useState<any>(null)
  const [loading, setLoading] = useState(false)

  // ✅ STEP 1: Load action from localStorage
  useEffect(() => {
    const stored = localStorage.getItem('activeAction')

    if (stored) {
      setAction(JSON.parse(stored))
    }
  }, [])

  // fallback UI
  if (!action) {
    return (
      <>
        <TopBar title="Consent Required" />
        <div className="flex items-center justify-center h-screen text-sm text-gray-500">
          No action found. Please start from Quick Actions.
        </div>
      </>
    )
  }

  // ✅ APPROVE FLOW (API + NAVIGATION)
  const handleApprove = async () => {
    try {
      setLoading(true)

      await api.recordConsent(
        action.customerId || 'default-user',
        action.type,
        true
      )

      router.push('/success')
    } catch (err) {
      console.error(err)
      router.push('/dashboard')
    } finally {
      setLoading(false)
    }
  }

  // ❌ REJECT FLOW (API + NAVIGATION)
  const handleReject = async () => {
    try {
      setLoading(true)

      await api.recordConsent(
        action.customerId || 'default-user',
        action.type,
        false
      )

      router.push('/dashboard')
    } catch (err) {
      console.error(err)
      router.push('/dashboard')
    } finally {
      setLoading(false)
    }
  }

  return (
    <>
      <TopBar title="Consent Required" />

      <motion.div
        variants={pageVariants}
        initial="initial"
        animate="animate"
        className="flex-1 overflow-y-auto p-6 flex items-center justify-center"
      >
        <div className="w-full max-w-lg bg-white rounded-3xl shadow-xl p-8">

          {/* Header */}
          <div className="text-center">
            <div className="w-16 h-16 mx-auto rounded-full bg-blue-100 flex items-center justify-center">
              <ShieldCheck size={32} className="text-blue-600" />
            </div>

            <h1 className="text-3xl font-bold text-slate-900 mt-5">
              Consent Required
            </h1>

            <p className="mt-4 text-gray-600 leading-relaxed">
              You are about to perform:{' '}
              <span className="font-semibold text-slate-900">
                {action.title}
              </span>
            </p>

            <p className="mt-2 text-sm text-gray-500">
              {action.description}
            </p>
          </div>

          {/* Consent Box */}
          <div className="mt-8 border rounded-2xl bg-slate-50 p-4">
            <label className="flex items-center gap-3 cursor-pointer">
              <input
                type="checkbox"
                checked={accepted}
                onChange={(e) => setAccepted(e.target.checked)}
                className="w-5 h-5"
              />

              <span className="font-medium text-slate-700">
                I understand and authorize this action
              </span>
            </label>
          </div>

          {/* Buttons */}
          <div className="flex gap-4 mt-8">

            {/* Decline */}
            <button
              onClick={handleReject}
              disabled={loading}
              className="flex-1 border border-gray-300 rounded-xl py-3 font-medium text-slate-700 hover:bg-gray-50 transition"
            >
              Decline
            </button>

            {/* Approve */}
            <button
              disabled={!accepted || loading}
              onClick={handleApprove}
              className={`flex-1 rounded-xl py-3 font-medium transition ${
                accepted && !loading
                  ? 'bg-blue-600 text-white hover:bg-blue-700'
                  : 'bg-gray-300 text-gray-500 cursor-not-allowed'
              }`}
            >
              {loading ? 'Processing...' : 'Approve'}
            </button>

          </div>
        </div>
      </motion.div>
    </>
  )
}