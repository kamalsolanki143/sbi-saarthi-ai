'use client'

import { motion } from 'framer-motion'

export default function ActionPreviewShowcase() {
  const flowSteps = [
    'Recommendation',
    'Action Preview',
    'Consent Manager',
    'MPIN Verification',
    'Execution',
    'Audit Trail',
  ]

  return (
    <section className="py-24 px-6 bg-slate-950">
      <div className="max-w-6xl mx-auto">
        {/* Heading */}
        <div className="text-center mb-16">
          <h2 className="text-4xl md:text-5xl font-bold text-white mb-4">
            Action Preview
          </h2>

          <p className="text-xl text-blue-300">
            Review Before Execution
          </p>
        </div>

        {/* Preview Card */}
        <motion.div
          initial={{ opacity: 0, y: 25 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
          className="max-w-2xl mx-auto"
        >
          <div className="bg-slate-900 border border-slate-700 rounded-3xl p-8">
            <div className="space-y-6">
              <div>
                <p className="text-slate-400 text-sm mb-2">
                  Action Type
                </p>
                <p className="text-white text-lg font-semibold">
                  Create Fixed Deposit
                </p>
              </div>

              <hr className="border-slate-700" />

              <div>
                <p className="text-slate-400 text-sm mb-2">
                  Amount
                </p>
                <p className="text-white text-lg font-semibold">
                  ₹50,000
                </p>
              </div>

              <hr className="border-slate-700" />

              <div>
                <p className="text-slate-400 text-sm mb-2">
                  Tenure
                </p>
                <p className="text-white text-lg font-semibold">
                  12 Months
                </p>
              </div>

              <hr className="border-slate-700" />

              <div>
                <p className="text-slate-400 text-sm mb-2">
                  Expected Returns
                </p>
                <p className="text-green-400 text-lg font-semibold">
                  ₹53,600
                </p>
              </div>

              <hr className="border-slate-700" />

              <div>
                <p className="text-slate-400 text-sm mb-2">
                  Agent
                </p>
                <p className="text-blue-400 text-lg font-semibold">
                  MARGDARSHAN
                </p>
              </div>

              <hr className="border-slate-700" />

              <div>
                <p className="text-slate-400 text-sm mb-2">
                  Confidence
                </p>
                <p className="text-green-400 text-lg font-semibold">
                  94%
                </p>
              </div>
            </div>
          </div>
        </motion.div>

        {/* Workflow */}
        <div className="mt-20">
          <h3 className="text-center text-2xl font-bold text-white mb-10">
            SBI-Safe Workflow
          </h3>

          <div className="flex flex-col items-center">
            {flowSteps.map((step, index) => (
              <div
                key={step}
                className="flex flex-col items-center"
              >
                <div className="bg-blue-600/20 border border-blue-500/30 text-white px-6 py-3 rounded-xl min-w-[220px] text-center">
                  {step}
                </div>

                {index !== flowSteps.length - 1 && (
                  <div className="text-blue-400 text-2xl my-3">
                    ↓
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  )
}
