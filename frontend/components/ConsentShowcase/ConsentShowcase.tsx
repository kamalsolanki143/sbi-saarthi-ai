'use client'

import { motion } from 'framer-motion'
import { Lock } from 'lucide-react'

export default function ConsentShowcase() {
  return (
    <section className="py-24 px-6 bg-slate-900">
      <div className="max-w-7xl mx-auto">
        {/* Heading */}
        <div className="text-center mb-16">
          <h2 className="text-4xl md:text-5xl font-bold text-white mb-4">
            Consent Manager
          </h2>

          <p className="text-xl text-blue-300 mb-4">
            You Always Stay In Control
          </p>

          <p className="text-slate-400 max-w-3xl mx-auto">
            Every high-impact banking action requires explicit user approval.
            SAARTHI explains the recommendation, shows the reasoning,
            and waits for secure consent before execution.
          </p>
        </div>

        {/* Consent Card */}
        <motion.div
          initial={{ opacity: 0, y: 25 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
          className="max-w-2xl mx-auto"
        >
          <div className="bg-slate-950 border border-slate-700 rounded-3xl p-8 shadow-2xl">
            <div className="flex items-center gap-3 mb-8">
              <div className="p-3 rounded-full bg-blue-600">
                <Lock className="w-5 h-5 text-white" />
              </div>

              <div>
                <h3 className="text-xl font-bold text-white">
                  Consent Required
                </h3>

                <p className="text-slate-400 text-sm">
                  Review and approve this action
                </p>
              </div>
            </div>

            <div className="space-y-5">
              <div>
                <p className="text-slate-400 text-sm">Action</p>
                <p className="text-white font-medium">
                  Create Fixed Deposit
                </p>
              </div>

              <div>
                <p className="text-slate-400 text-sm">Amount</p>
                <p className="text-white font-medium">
                  ₹50,000
                </p>
              </div>

              <div>
                <p className="text-slate-400 text-sm">Duration</p>
                <p className="text-white font-medium">
                  12 Months
                </p>
              </div>

              <div>
                <p className="text-slate-400 text-sm">Recommended By</p>
                <p className="text-blue-400 font-semibold">
                  MARGDARSHAN
                </p>
              </div>

              <div>
                <p className="text-slate-400 text-sm">Reason</p>
                <p className="text-white">
                  Idle balance detected in savings account.
                </p>
              </div>

              <div>
                <p className="text-slate-400 text-sm">Risk Level</p>
                <span className="inline-flex px-3 py-1 rounded-full bg-green-500/20 text-green-400 text-sm font-medium">
                  Low
                </span>
              </div>
            </div>

            <div className="flex flex-col sm:flex-row gap-4 mt-10">
              <button className="flex-1 bg-blue-600 hover:bg-blue-700 transition-colors text-white font-medium py-3 rounded-xl">
                Approve via MPIN
              </button>

              <button className="flex-1 border border-slate-600 hover:bg-slate-800 transition-colors text-white font-medium py-3 rounded-xl">
                Cancel
              </button>
            </div>
          </div>
        </motion.div>
      </div>
    </section>
  )
}
