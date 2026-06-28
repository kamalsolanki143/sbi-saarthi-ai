'use client'
import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { UserPlus, TrendingUp, HeartHandshake, ArrowRight, CheckCircle2 } from 'lucide-react'

const agents = [
  {
    id: 'mitra',
    name: 'Mitra',
    tagline: 'Customer Acquisition Agent',
    desc: 'Helps new and existing customers discover suitable banking products through natural conversation. Smart onboarding, KYC assistance, and product discovery.',
    color: '#F0997B',
    bgColor: '#FAECE7',
    textColor: '#712B13',
    borderColor: '#F0997B',
    icon: UserPlus,
    highlights: ['Smart Onboarding', 'Product Discovery', 'KYC Assistance', 'OCR Document Processing'],
    useCase: 'A farmer in Varanasi uses voice to open a Kisan Credit Card. Mitra guides through Aadhaar OCR, product selection, and application in Hindi.',
  },
  {
    id: 'margdarshan',
    name: 'Margdarshan',
    tagline: 'Digital Adoption Agent',
    desc: 'Proactively detects financial events and guides customers toward effective use of digital banking services. The MVP demo agent.',
    color: '#5DCAA5',
    bgColor: '#E1F5EE',
    textColor: '#085041',
    borderColor: '#5DCAA5',
    icon: TrendingUp,
    highlights: ['Salary Credit Detection', 'Subsidiy Detection', 'Idle Balance Alerts', 'FD Recommendations', 'UPI/YONO Adoption'],
    useCase: 'A salary credit of ₹15,000 triggers Margdarshan. It recommends a 1-year FD at 6.8%. The user confirms with MPIN. Action executed.',
  },
  {
    id: 'saathi',
    name: 'Saathi',
    tagline: 'Customer Engagement Agent',
    desc: 'Provides proactive financial guidance based on behavioral patterns, life events, and spending analysis. Deep customer engagement.',
    color: '#85B7EB',
    bgColor: '#E6F1FB',
    textColor: '#0C447C',
    borderColor: '#85B7EB',
    icon: HeartHandshake,
    highlights: ['Spending Analysis', 'Life Event Detection', 'Education Monitoring', 'Festival Insights', 'Travel Detection'],
    useCase: 'Detects school fee payments in June. Suggests starting a SIP for education planning. Explains the benefit in simple terms.',
  },
]

export default function AgentShowcase() {
  const [active, setActive] = useState(0)
  const agent = agents[active]

  return (
    <section id="agents" className="py-24 bg-[#0D1B2A] relative overflow-hidden">
      <div className="absolute inset-0 bg-grid opacity-20" />
      <div className="relative z-10 max-w-7xl mx-auto px-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: '-100px' }}
          transition={{ duration: 0.5 }}
          className="text-center max-w-2xl mx-auto mb-12"
        >
          <span className="text-accent text-sm font-medium tracking-wider uppercase">The Three Agents</span>
          <h2 className="text-3xl md:text-4xl font-bold text-white mt-3 tracking-tight">
            A Team of Specialized AI Agents
          </h2>
          <p className="text-white/40 mt-4 leading-relaxed">
            Each agent has a distinct role. Together they form an intelligent banking layer that understands, recommends, and protects.
          </p>
        </motion.div>

        {/* Tabs */}
        <div className="flex justify-center gap-2 mb-12">
          {agents.map((a, idx) => (
            <button
              key={a.id}
              onClick={() => setActive(idx)}
              className={`relative px-5 py-2.5 rounded-lg text-sm font-medium transition-all ${
                idx === active
                  ? 'text-white shadow-lg'
                  : 'text-white/40 hover:text-white/70 bg-white/[0.03]'
              }`}
              style={idx === active ? { background: `${a.color}20`, color: a.color } : {}}
            >
              {a.name}
              {idx === active && (
                <motion.div
                  layoutId="agent-tab"
                  className="absolute bottom-0 left-3 right-3 h-0.5 rounded-full"
                  style={{ background: a.color }}
                />
              )}
            </button>
          ))}
        </div>

        {/* Content */}
        <AnimatePresence mode="wait">
          <motion.div
            key={agent.id}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            transition={{ duration: 0.3 }}
            className="grid lg:grid-cols-2 gap-8 items-start"
          >
            <div className="bg-white/[0.03] border border-white/5 rounded-xl p-8">
              <div
                className="w-12 h-12 rounded-xl flex items-center justify-center mb-4"
                style={{ background: `${agent.color}20` }}
              >
                <agent.icon size={24} style={{ color: agent.color }} />
              </div>
              <h3 className="text-2xl font-bold text-white mb-1">{agent.name}</h3>
              <p className="text-sm font-medium mb-4" style={{ color: agent.color }}>{agent.tagline}</p>
              <p className="text-sm text-white/50 leading-relaxed mb-6">{agent.desc}</p>
              <div className="space-y-2">
                {agent.highlights.map((h) => (
                  <div key={h} className="flex items-center gap-2">
                    <CheckCircle2 size={14} style={{ color: agent.color }} />
                    <span className="text-sm text-white/70">{h}</span>
                  </div>
                ))}
              </div>
            </div>

            <div className="bg-white/[0.03] border border-white/5 rounded-xl p-8">
              <span className="text-xs font-medium text-white/30 uppercase tracking-wider">Real-World Scenario</span>
              <div
                className="mt-4 p-4 rounded-lg border-l-4"
                style={{ background: `${agent.color}08`, borderColor: agent.color }}
              >
                <p className="text-sm text-white/70 leading-relaxed">{agent.useCase}</p>
              </div>
              <div className="mt-6 pt-6 border-t border-white/5">
                <div className="flex items-center gap-2 text-sm text-white/50">
                  <span>Works alongside</span>
                  {agents.filter((_, i) => i !== active).map((a) => (
                    <span
                      key={a.id}
                      className="px-2 py-0.5 rounded text-xs font-medium"
                      style={{ background: `${a.color}15`, color: a.color }}
                    >
                      {a.name}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          </motion.div>
        </AnimatePresence>
      </div>
    </section>
  )
}
