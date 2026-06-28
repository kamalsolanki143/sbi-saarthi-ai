'use client'

import { motion } from 'framer-motion'

const timeline = [
  {
    time: '12:01 PM',
    agent: 'MITRA',
    title: 'Intent Detected',
    details: '"Open Fixed Deposit"',
    confidence: '96%',
    status: '✓ Logged',
  },
  {
    time: '12:02 PM',
    agent: 'MARGDARSHAN',
    title: 'Policy Validation',
    details: 'FD Eligible • Risk Score: Low',
    confidence: '94%',
    status: '✓ Approved',
  },
  {
    time: '12:03 PM',
    agent: 'SAATHI',
    title: 'Action Prepared',
    details: 'FD Amount: ₹50,000',
    confidence: '97%',
    status: '✓ Awaiting MPIN',
  },
  {
    time: '12:04 PM',
    agent: 'USER',
    title: 'MPIN Verified',
    details: '',
    confidence: '',
    status: '✓ Executed',
  },
]

const metrics = [
  {
    value: '100%',
    label: 'Audit Coverage',
  },
  {
    value: '94%',
    label: 'Average Confidence',
  },
  {
    value: '0',
    label: 'Unapproved Transactions',
  },
  {
    value: '100%',
    label: 'Traceable Actions',
  },
]

export default function AuditTrailSection() {
  return (
    <section className="py-24 px-6 bg-slate-950">
      <div className="max-w-7xl mx-auto">
        <div className="text-center mb-16">
          <h2 className="text-4xl md:text-5xl font-bold text-white mb-4">
            Live Audit Trail
          </h2>

          <p className="text-xl text-blue-300 mb-4">
            Every AI Decision is Transparent & Traceable
          </p>

          <p className="text-slate-400 max-w-3xl mx-auto">
            SAARTHI records every recommendation, approval,
            and banking action with timestamps, confidence scores,
            and agent attribution.
          </p>
        </div>

        <div className="max-w-3xl mx-auto relative">
          {timeline.map((item, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 25 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: index * 0.1 }}
              className="relative mb-8"
            >
              {index !== timeline.length - 1 && (
                <div className="absolute left-6 top-20 w-0.5 h-20 bg-blue-500" />
              )}

              <div className="flex gap-4">
                <div className="w-12 h-12 rounded-full bg-blue-600 flex items-center justify-center text-white font-bold">
                  {index + 1}
                </div>

                <div className="flex-1 bg-slate-900 border border-slate-700 rounded-2xl p-6">
                  <p className="text-blue-400 text-sm">
                    {item.time}
                  </p>

                  <h3 className="text-white font-bold mt-1">
                    {item.agent}
                  </h3>

                  <p className="text-white font-medium mt-3">
                    {item.title}
                  </p>

                  {item.details && (
                    <p className="text-slate-300 mt-2">
                      {item.details}
                    </p>
                  )}

                  {item.confidence && (
                    <p className="text-green-400 mt-3">
                      Confidence: {item.confidence}
                    </p>
                  )}

                  <p className="text-emerald-400 mt-2 font-medium">
                    {item.status}
                  </p>
                </div>
              </div>
            </motion.div>
          ))}
        </div>

        <div className="grid md:grid-cols-4 gap-6 mt-20">
          {metrics.map((metric) => (
            <div
              key={metric.label}
              className="bg-slate-900 border border-slate-700 rounded-2xl p-6 text-center"
            >
              <div className="text-4xl font-bold text-blue-400">
                {metric.value}
              </div>

              <div className="text-slate-300 mt-3">
                {metric.label}
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
