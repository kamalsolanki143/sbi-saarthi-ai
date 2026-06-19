'use client'
import { motion } from 'framer-motion'
import { UserPlus, TrendingUp, HeartHandshake, ArrowRight, Database, Share2, ShieldCheck } from 'lucide-react'

const agents = [
  {
    name: 'Mitra',
    role: 'Acquisition',
    icon: UserPlus,
    color: '#F0997B',
    gradient: 'from-[#F0997B]/20 to-transparent',
    actions: [
      'Greets customer in preferred language',
      'Identifies suitable banking products',
      'Guides through KYC and document upload',
      'Opens account or initiates application',
    ],
  },
  {
    name: 'Margdarshan',
    role: 'Adoption',
    icon: TrendingUp,
    color: '#5DCAA5',
    gradient: 'from-[#5DCAA5]/20 to-transparent',
    actions: [
      'Monitors account for financial events',
      'Detects salary/subsidiy/idle balance',
      'Generates personalized recommendations',
      'Prepares action for MPIN confirmation',
    ],
  },
  {
    name: 'Saathi',
    role: 'Engagement',
    icon: HeartHandshake,
    color: '#85B7EB',
    gradient: 'from-[#85B7EB]/20 to-transparent',
    actions: [
      'Analyzes spending patterns',
      'Detects life events (fees, travel, festivals)',
      'Suggests proactive financial steps',
      'Deepens customer relationship over time',
    ],
  },
]

const steps = [
  { icon: Database, label: '1. Event Detected', desc: 'Salary, subsidy, or behavioral trigger' },
  { icon: Share2, label: '2. Shared Memory', desc: 'Customer context across all agents' },
  { icon: ShieldCheck, label: '3. Recommendation', desc: 'Agent generates explainable action' },
  { icon: ArrowRight, label: '4. MPIN Gate', desc: 'Human confirms before execution' },
]

export default function AgentsSection() {
  return (
    <section className="py-24 bg-[#0A1628] relative overflow-hidden">
      <div className="absolute inset-0 bg-grid-dark opacity-20" />
      <div className="relative z-10 max-w-7xl mx-auto px-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: '-100px' }}
          transition={{ duration: 0.5 }}
          className="text-center max-w-2xl mx-auto mb-16"
        >
          <span className="text-accent text-sm font-medium tracking-wider uppercase">How Agents Work</span>
          <h2 className="text-3xl md:text-4xl font-bold text-white mt-3 tracking-tight">
            Collaboration Through Shared Intelligence
          </h2>
          <p className="text-white/40 mt-4 leading-relaxed">
            Agents don&apos;t work in isolation. They share memory, context, and customer state to deliver cohesive banking experiences.
          </p>
        </motion.div>

        {/* Agent workflow cards */}
        <div className="grid md:grid-cols-3 gap-5 mb-16">
          {agents.map((agent, idx) => {
            const Icon = agent.icon
            return (
              <motion.div
                key={agent.name}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true, margin: '-50px' }}
                transition={{ delay: idx * 0.1, duration: 0.4 }}
                whileHover={{ y: -4 }}
                className="relative bg-gradient-to-b rounded-xl border border-white/5 overflow-hidden group"
                style={{ backgroundImage: `linear-gradient(to bottom, ${agent.color}08, transparent)` }}
              >
                <div className="absolute top-0 left-0 right-0 h-1" style={{ background: agent.color }} />
                <div className="p-6">
                  <div
                    className="w-10 h-10 rounded-xl flex items-center justify-center mb-4"
                    style={{ background: `${agent.color}20` }}
                  >
                    <Icon size={20} style={{ color: agent.color }} />
                  </div>
                  <h3 className="text-lg font-bold text-white mb-1">
                    {agent.name}
                    <span className="text-sm font-normal ml-2" style={{ color: agent.color }}>{agent.role}</span>
                  </h3>
                  <ul className="mt-4 space-y-2">
                    {agent.actions.map((action, ai) => (
                      <li key={ai} className="flex items-start gap-2 text-sm text-white/50">
                        <span className="w-1 h-1 rounded-full mt-1.5 shrink-0" style={{ background: agent.color }} />
                        {action}
                      </li>
                    ))}
                  </ul>
                </div>
              </motion.div>
            )
          })}
        </div>

        {/* Workflow steps */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: '-50px' }}
          className="bg-white/[0.03] border border-white/5 rounded-xl p-8"
        >
          <h3 className="text-lg font-semibold text-white mb-6 text-center">End-to-End Agent Workflow</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
            {steps.map((step, idx) => {
              const Icon = step.icon
              return (
                <div key={idx} className="text-center">
                  <div className="w-12 h-12 rounded-full bg-accent/10 flex items-center justify-center mx-auto mb-3">
                    <Icon size={20} className="text-accent" />
                  </div>
                  <p className="text-sm font-medium text-white mb-1">{step.label}</p>
                  <p className="text-xs text-white/40">{step.desc}</p>
                  {idx < steps.length - 1 && (
                    <div className="hidden md:block absolute top-6 left-[60%] w-[80%] h-px border-t border-dashed border-white/10" />
                  )}
                </div>
              )
            })}
          </div>
        </motion.div>
      </div>
    </section>
  )
}
