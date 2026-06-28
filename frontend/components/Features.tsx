'use client'
import { motion } from 'framer-motion'
import { Mic, Zap, Brain, ShieldCheck, Wifi, ScrollText, Users, Languages } from 'lucide-react'

const features = [
  {
    icon: Mic,
    title: 'Voice-First Banking',
    desc: 'Speak naturally in Hindi, Bengali, or Tamil. SAARTHI understands, processes, and responds in your language — no typing needed.',
    color: '#0F6E56',
  },
  {
    icon: Users,
    title: 'Shared Customer Memory',
    desc: 'Every interaction across agents contributes to a unified customer profile. SAARTHI remembers who you are and what you need.',
    color: '#C9A84C',
  },
  {
    icon: Zap,
    title: 'Event-Trigger Engine',
    desc: 'Salary credits, subsidy deposits, idle balances — SAARTHI detects financial events in real time and acts intelligently.',
    color: '#F0997B',
  },
  {
    icon: Brain,
    title: 'Explainable Recommendations',
    desc: 'Every suggestion includes a clear rationale. No black-box decisions. Full transparency on why a product or action is recommended.',
    color: '#85B7EB',
  },
  {
    icon: ShieldCheck,
    title: 'Human-in-the-Loop',
    desc: 'AI proposes, you dispose. Every action — FD creation, account opening — requires explicit MPIN or biometric approval.',
    color: '#BA7517',
  },
  {
    icon: Wifi,
    title: 'Low-Bandwidth Ready',
    desc: 'Optimized for Bharat&apos;s connectivity realities. Works on 2G, low storage devices, and in areas with intermittent internet.',
    color: '#5DCAA5',
  },
  {
    icon: ScrollText,
    title: 'Audit Trail',
    desc: 'Every decision, recommendation, and action is logged with timestamps, confidence scores, and agent attribution for full accountability.',
    color: '#1A3A5C',
  },
  {
    icon: Languages,
    title: 'Multilingual by Design',
    desc: 'Built for India&apos;s linguistic diversity. Currently supports Hindi, Bengali, Tamil — with more regional languages in the pipeline.',
    color: '#712B13',
  },
]

export default function Features() {
  return (
    <section id="features" className="py-24 bg-[#0A1628] relative overflow-hidden">
      <div className="absolute inset-0 bg-grid-dark opacity-30" />
      <div className="relative z-10 max-w-7xl mx-auto px-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: '-100px' }}
          transition={{ duration: 0.5 }}
          className="text-center max-w-2xl mx-auto mb-16"
        >
          <span className="text-accent text-sm font-medium tracking-wider uppercase">Platform Features</span>
          <h2 className="text-3xl md:text-4xl font-bold text-white mt-3 tracking-tight">
            Built for Intelligence, Security, and Scale
          </h2>
          <p className="text-white/40 mt-4 leading-relaxed">
            Every feature designed to make banking accessible, understandable, and secure for every Indian.
          </p>
        </motion.div>

        <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-5">
          {features.map((feature, idx) => {
            const Icon = feature.icon
            return (
              <motion.div
                key={idx}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true, margin: '-50px' }}
                transition={{ delay: idx * 0.05, duration: 0.4 }}
                whileHover={{ y: -4, transition: { duration: 0.2 } }}
                className="group bg-white/[0.03] border border-white/[0.06] rounded-xl p-5 hover:bg-white/[0.06] transition-all relative overflow-hidden"
              >
                <div
                  className="absolute top-0 left-0 right-0 h-0.5 opacity-0 group-hover:opacity-100 transition-opacity duration-300"
                  style={{ background: feature.color }}
                />
                <div
                  className="w-9 h-9 rounded-lg flex items-center justify-center mb-3"
                  style={{ background: `${feature.color}15` }}
                >
                  <Icon size={18} style={{ color: feature.color }} />
                </div>
                <h3 className="text-sm font-semibold text-white mb-2">{feature.title}</h3>
                <p className="text-xs text-white/50 leading-relaxed">{feature.desc}</p>
              </motion.div>
            )
          })}
        </div>
      </div>
    </section>
  )
}
