'use client'

import { motion } from 'framer-motion'
import { useRouter } from 'next/navigation'
import { CheckCircle } from 'lucide-react'

import TopBar from '@/components/shared/TopBar'

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

export default function SuccessPage() {
  const router = useRouter()

  return (
    <>
      <TopBar title="Success" />

      <motion.div
        variants={pageVariants}
        initial="initial"
        animate="animate"
        className="flex-1 overflow-y-auto p-6 flex items-center justify-center"
      >
        <div className="w-full max-w-lg bg-white rounded-3xl shadow-xl p-8">
          {/* Success Icon */}
          <div className="text-center">
            <div className="w-20 h-20 mx-auto rounded-full bg-green-100 flex items-center justify-center">
              <CheckCircle
                size={48}
                className="text-green-600"
              />
            </div>

            <h1 className="text-3xl font-bold text-slate-900 mt-5">
              Success
            </h1>

            <p className="text-green-600 font-semibold mt-2 text-lg">
              FD Created Successfully
            </p>
          </div>

          {/* FD Details */}
          <div className="mt-8 bg-slate-50 border border-slate-200 rounded-2xl p-6">
            <div className="space-y-5">
              <div className="flex justify-between">
                <span className="text-gray-500">
                  FD Number
                </span>

                <span className="font-semibold text-slate-900">
                  FD001245
                </span>
              </div>

              <div className="flex justify-between">
                <span className="text-gray-500">
                  Amount
                </span>

                <span className="font-semibold text-slate-900">
                  ₹5,000
                </span>
              </div>

              <div className="flex justify-between">
                <span className="text-gray-500">
                  Maturity Amount
                </span>

                <span className="font-bold text-green-600">
                  ₹5,340
                </span>
              </div>
            </div>
          </div>

          {/* Button */}
          <button
            onClick={() => router.push('/dashboard')}
            className="w-full mt-8 bg-blue-600 text-white rounded-xl py-3 font-medium hover:bg-blue-700 transition"
          >
            Back to Dashboard
          </button>
        </div>
      </motion.div>
    </>
  )
}