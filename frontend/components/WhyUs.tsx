'use client'
import { motion } from 'framer-motion'
import { Bot, Globe, ShieldCheck, Brain, Users, GitBranch } from 'lucide-react'

const reasons = [
  {
    icon: GitBranch,
    title: 'Agentic Orchestration',
    desc: 'Not a chatbot. Three specialized AI agents — Mitra, Margdarshan, Saathi — collaborate through shared memory to understand context and take intelligent action.',
  },
  {
    icon: Globe,
    title: 'Bharat-First by Design',
    desc: 'Voice-first interface in Hindi, Bengali, and Tamil. Built for rural and semi-urban users who find traditional banking apps difficult to navigate.',
  },
  {
    icon: ShieldCheck,
    title: 'Human-in-the-Loop Security',
    desc: 'AI recommends. You approve. Every action requires MPIN or biometric confirmation. SAARTHI cannot execute transactions autonomously — ever.',
  },
  {
    icon: Brain,
    title: 'Explainable Intelligence',
    desc: 'Every recommendation comes with a clear reason: "Why am I seeing this?" No black boxes. Full audit trail of every decision made.',
  },
]

export default function WhyUs() {
  return (
    <section className="py-24 bg-[#0D1B2A] relative overflow-hidden">
      <div className="absolute inset-0 bg-grid opacity-20" />
      <div className="relative z-10 max-w-7xl mx-auto px-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: '-100px' }}
          transition={{ duration: 0.5 }}
          className="text-center max-w-2xl mx-auto mb-16"
        >
          <span className="text-accent text-sm font-medium tracking-wider uppercase">Why SAARTHI</span>
          <h2 className="text-3xl md:text-4xl font-bold text-white mt-3 tracking-tight">
            Not Just Another Banking Chatbot
          </h2>
          <p className="text-white/40 mt-4 leading-relaxed">
            SAARTHI is an agentic AI layer purpose-built for India&apos;s largest bank. It reasons, recommends, and acts — securely.
          </p>
        </motion.div>

        <div className="grid md:grid-cols-2 gap-6">
          {reasons.map((reason, idx) => {
            const Icon = reason.icon
            return (
              <motion.div
                key={idx}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true, margin: '-50px' }}
                transition={{ delay: idx * 0.1, duration: 0.4 }}
                whileHover={{ y: -3 }}
                className="group bg-white/[0.03] border border-white/5 rounded-xl p-6 hover:bg-white/[0.06] hover:border-accent/20 transition-all"
              >
                <div className="w-10 h-10 rounded-xl bg-accent/10 flex items-center justify-center mb-4 group-hover:bg-accent/20 transition-colors">
                  <Icon size={20} className="text-accent" />
                </div>
                <h3 className="text-lg font-semibold text-white mb-2">{reason.title}</h3>
                <p className="text-sm text-white/50 leading-relaxed">{reason.desc}</p>
              </motion.div>
            )
          })}
        </div>
      </div>
    </section>
  )
}
