'use client'

import { motion } from 'framer-motion'
import { useRouter } from 'next/navigation'
import { ActionPayload, AgentName } from '@/types/agent'
import AgentBadge from '@/components/shared/AgentBadge'

interface Props {
  action: ActionPayload
  agent: AgentName
  onAuthorize: () => void
  onDecline: () => void
}

export default function ActionPreview({
  action,
  agent,
  onAuthorize,
  onDecline,
}: Props) {
  const router = useRouter()

  const amount = action.amount || 5000
  const interestRate = action.interest_rate || 6.8
  const tenure = action.duration || '1 Year'

  const maturityAmount = Math.round(
    amount + (amount * Number(interestRate)) / 100
  )

  return (
    <div className="bg-white rounded-3xl shadow-xl p-8">
      {/* Header */}
      <div className="mb-8">
        <AgentBadge agent={agent} size="md" />

        <h1 className="text-3xl font-bold mt-4 text-slate-900">
          Action Preview
        </h1>

        <p className="text-gray-500 mt-2">
          Please review before proceeding
        </p>
      </div>

      {/* FD Card */}
      <div className="bg-slate-50 border border-slate-200 rounded-2xl p-6">
        <h2 className="text-2xl font-semibold mb-6 text-slate-900">
          {action.display_label || 'FD Creation'}
        </h2>

        <div className="space-y-5">
          <div className="flex items-center justify-between">
            <span className="text-gray-500">
              Amount
            </span>

            <span className="font-semibold text-slate-900">
              ₹{amount.toLocaleString()}
            </span>
          </div>

          <div className="flex items-center justify-between">
            <span className="text-gray-500">
              Interest
            </span>

            <span className="font-semibold text-green-600">
              {interestRate}%
            </span>
          </div>

          <div className="flex items-center justify-between">
            <span className="text-gray-500">
              Tenure
            </span>

            <span className="font-semibold text-slate-900">
              {tenure}
            </span>
          </div>

          <div className="border-t border-slate-200 pt-5 flex items-center justify-between">
            <span className="text-gray-500">
              Maturity Amount
            </span>

            <span className="font-bold text-xl text-blue-600">
              ₹{maturityAmount.toLocaleString()}
            </span>
          </div>
        </div>
      </div>

      {/* Risk Badge */}
      {action.risk_level && (
        <div className="mt-6 flex justify-between items-center">
          <span className="text-sm text-gray-500">
            Risk Level
          </span>

          <span
            className={`px-3 py-1 rounded-full text-xs font-medium ${
              action.risk_level === 'high'
                ? 'bg-red-100 text-red-700'
                : action.risk_level === 'medium'
                ? 'bg-yellow-100 text-yellow-700'
                : 'bg-green-100 text-green-700'
            }`}
          >
            {action.risk_level.charAt(0).toUpperCase() +
              action.risk_level.slice(1)}
          </span>
        </div>
      )}

      {/* Buttons */}
      <div className="flex gap-4 mt-8">
        <motion.button
          onClick={onDecline}
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.97 }}
          className="flex-1 border border-gray-300 rounded-xl py-3 font-medium text-slate-700 hover:bg-gray-50 transition"
        >
          Cancel
        </motion.button>

        <motion.button
          onClick={() => router.push('/consent')}
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.97 }}
          className="flex-1 bg-blue-600 text-white rounded-xl py-3 font-medium hover:bg-blue-700 transition"
        >
          Proceed
        </motion.button>
      </div>
    </div>
  )
}