'use client'

import { motion } from 'framer-motion'

const agents = [
  {
    name: 'MITRA',
    role: 'Customer Acquisition',
    icon: '🧠',
    gradient: 'bg-gradient-to-r from-blue-500 to-cyan-500',
    glow: 'from-blue-500/20 to-cyan-500/20',
    description:
      'Understands customer intent, onboarding, KYC and product discovery.',
  },
  {
    name: 'MARGDARSHAN',
    role: 'Policy Intelligence',
    icon: '🛡️',
    gradient: 'bg-gradient-to-r from-purple-500 to-pink-500',
    glow: 'from-purple-500/20 to-pink-500/20',
    description:
      'Validates policies, compliance, recommendations and confidence.',
  },
  {
    name: 'SAATHI',
    role: 'Secure Execution',
    icon: '⚡',
    gradient: 'bg-gradient-to-r from-orange-500 to-red-500',
    glow: 'from-orange-500/20 to-red-500/20',
    description:
      'Executes approved actions after MPIN verification.',
  },
]

export default function AgentsSection() {
  return (
    <section className="relative overflow-hidden bg-[#0A1628] py-24">
      <div className="absolute inset-0 opacity-20 bg-grid-dark" />

      <div className="relative z-10 mx-auto max-w-7xl px-6">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 25 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="mb-16 text-center"
        >
          <span className="inline-flex items-center rounded-full border border-blue-500/30 bg-blue-500/10 px-4 py-2 text-sm font-medium text-blue-300">
            Multi-Agent Intelligence Layer
          </span>

          <h2 className="mt-6 text-4xl font-bold text-white md:text-5xl">
            Meet the AI Workforce Behind
            <span className="block bg-gradient-to-r from-blue-400 via-cyan-400 to-indigo-400 bg-clip-text text-transparent">
              SAARTHI Banking OS
            </span>
          </h2>

          <p className="mx-auto mt-5 max-w-3xl text-lg text-white/60">
            Three specialized agents collaborate to understand customer
            requests, ensure compliance, and securely execute banking actions.
          </p>
        </motion.div>

        {/* Cards */}
        <div className="grid gap-8 md:grid-cols-3">
          {agents.map((agent, index) => (
            <motion.div
              key={agent.name}
              initial={{ opacity: 0, y: 40 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{
                duration: 0.5,
                delay: index * 0.15,
              }}
              whileHover={{ y: -8 }}
              className="group relative overflow-hidden rounded-3xl border border-white/10 bg-white/5 p-8 backdrop-blur-xl"
            >
              {/* Glow */}
              <div
                className={`absolute inset-0 bg-gradient-to-br ${agent.glow} opacity-50 blur-3xl transition-all duration-500 group-hover:opacity-80`}
              />

              <div className="relative z-10">
                {/* Icon */}
                <div
                  className={`mb-6 flex h-16 w-16 items-center justify-center rounded-2xl text-3xl shadow-lg ${agent.gradient}`}
                >
                  {agent.icon}
                </div>

                {/* Title */}
                <h3 className="text-3xl font-bold text-white">
                  {agent.name}
                </h3>

                <p className="mt-1 font-medium text-blue-300">
                  {agent.role}
                </p>

                <p className="mt-4 leading-relaxed text-gray-300">
                  {agent.description}
                </p>

                {/* Status Chips */}
                <div className="mt-6 flex flex-wrap gap-2">
                  <span className="rounded-full bg-green-500/20 px-3 py-1 text-xs font-medium text-green-400">
                    Active
                  </span>

                  <span className="rounded-full bg-white/10 px-3 py-1 text-xs text-white/70">
                    Confidence 94%
                  </span>
                </div>

                {/* Footer */}
                <div className="mt-8 flex items-center justify-between border-t border-white/10 pt-6">
                  <span className="text-sm text-white/40">
                    Agent Status
                  </span>

                  <span className="text-sm font-medium text-green-400">
                    Operational
                  </span>
                </div>
              </div>
            </motion.div>
          ))}
        </div>

        {/* Collaboration Flow */}
        <section className="mt-20">
          <div className="mb-10 text-center">
            <h3 className="text-3xl font-bold text-white">
              Agent Collaboration Flow
            </h3>

            <p className="mt-3 text-white/60">
              Multi-agent coordination from customer request to secure banking
              action
            </p>
          </div>

          <div className="flex flex-col items-center justify-center gap-6 md:flex-row">
            <div className="rounded-xl bg-blue-600 px-6 py-4 font-bold text-white shadow-lg">
              MITRA
            </div>

            <div className="text-3xl text-white/50">↓</div>

            <div className="rounded-xl bg-purple-600 px-6 py-4 font-bold text-white shadow-lg">
              MARGDARSHAN
            </div>

            <div className="text-3xl text-white/50">↓</div>

            <div className="rounded-xl bg-orange-600 px-6 py-4 font-bold text-white shadow-lg">
              SAATHI
            </div>
          </div>

          <div className="mt-12 text-center">
            <div className="space-y-3 text-white/80">
              <div>Customer Request</div>
              <div className="text-blue-400">↓</div>

              <div>Intent Understanding</div>
              <div className="text-purple-400">↓</div>

              <div>Policy Validation</div>
              <div className="text-pink-400">↓</div>

              <div>MPIN Approval</div>
              <div className="text-orange-400">↓</div>

              <div className="font-semibold text-green-400">
                Secure Execution
              </div>
            </div>
          </div>
        </section>
      </div>
    </section>
  )
}