'use client'
import { motion } from 'framer-motion'
import { ShieldCheck, Lock, Eye, FileCheck, UserCheck, Scale, Fingerprint, ClipboardCheck } from 'lucide-react'

const principles = [
  {
    icon: ShieldCheck,
    title: 'Zero-Execute Autonomy',
    desc: 'AI can recommend, analyze, and prepare actions — but cannot execute a single transaction without explicit human approval via MPIN or biometric.',
  },
  {
    icon: Lock,
    title: 'Human-in-the-Loop',
    desc: 'Every financial action requires a verified human confirm. The AI presents a clear action preview; the user reviews and authorizes with their MPIN.',
  },
  {
    icon: FileCheck,
    title: 'Consent Management',
    desc: 'Explicit consent required for voice processing, memory storage, and personalized recommendations. Revocable at any time from the consent dashboard.',
  },
  {
    icon: ClipboardCheck,
    title: 'Full Audit Trail',
    desc: 'Every AI decision is logged: timestamp, agent, confidence score, guardrail status, action taken, and MPIN verification status. Fully auditable.',
  },
  {
    icon: Scale,
    title: 'DPDP Act Compliant',
    desc: 'Built in alignment with India&apos;s Digital Personal Data Protection Act. Data minimization, purpose limitation, and citizen rights by design.',
  },
  {
    icon: Eye,
    title: 'Explainable AI',
    desc: 'No black boxes. Every recommendation includes a clear rationale — why this product, why now, what benefit, what risk. Confidence scores visibly displayed.',
  },
]

const numbers = [
  { value: '100%', label: 'Human approval required for actions' },
  { value: '0', label: 'Autonomous transaction execution' },
  { value: '100%', label: 'Audit trail coverage' },
  { value: '85%', label: 'Confidence threshold before fallback' },
]

export default function SecuritySection() {
  return (
    <section id="security" className="py-24 bg-[#0A1628] relative overflow-hidden">
      <div className="absolute inset-0 bg-grid-dark opacity-20" />
      <div className="relative z-10 max-w-7xl mx-auto px-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: '-100px' }}
          transition={{ duration: 0.5 }}
          className="text-center max-w-2xl mx-auto mb-16"
        >
          <span className="text-accent text-sm font-medium tracking-wider uppercase">Security & Compliance</span>
          <h2 className="text-3xl md:text-4xl font-bold text-white mt-3 tracking-tight">
            Trust Built Into Every Layer
          </h2>
          <p className="text-white/40 mt-4 leading-relaxed">
            SAARTHI is designed with security-first principles. The AI assists but never acts alone.
          </p>
        </motion.div>

        {/* Stats */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-16">
          {numbers.map((num, idx) => (
            <motion.div
              key={idx}
              initial={{ opacity: 0, y: 15 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: idx * 0.1 }}
              whileHover={{ y: -2 }}
              className="bg-white/[0.03] border border-white/5 rounded-xl p-5 text-center"
            >
              <p className="text-3xl font-bold text-accent mb-1">{num.value}</p>
              <p className="text-xs text-white/50">{num.label}</p>
            </motion.div>
          ))}
        </div>

        {/* Principles */}
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-5">
          {principles.map((principle, idx) => {
            const Icon = principle.icon
            return (
              <motion.div
                key={idx}
                initial={{ opacity: 0, y: 15 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true, margin: '-50px' }}
                transition={{ delay: idx * 0.05, duration: 0.4 }}
                whileHover={{ y: -3 }}
                className="bg-white/[0.03] border border-white/5 rounded-xl p-5 group hover:bg-white/[0.06] hover:border-accent/15 transition-all"
              >
                <div className="w-9 h-9 rounded-lg bg-accent/10 flex items-center justify-center mb-3 group-hover:bg-accent/20 transition-colors">
                  <Icon size={18} className="text-accent" />
                </div>
                <h3 className="text-sm font-semibold text-white mb-2">{principle.title}</h3>
                <p className="text-xs text-white/50 leading-relaxed">{principle.desc}</p>
              </motion.div>
            )
          })}
        </div>

        {/* Trust note */}
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="mt-12 p-4 rounded-xl bg-gold/5 border border-gold/10 text-center"
        >
          <p className="text-sm text-white/60">
            <span className="text-gold font-medium">SAARTHI is a decision-support system, not an autonomous agent.</span>{' '}
            It recommends. You decide. Every action requires your explicit MPIN or biometric confirmation.
          </p>
        </motion.div>
      </div>
    </section>
  )
}
