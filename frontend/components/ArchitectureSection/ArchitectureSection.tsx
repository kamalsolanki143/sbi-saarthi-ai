'use client'
import { motion } from 'framer-motion'
import { Mic, Zap, Brain, ShieldCheck, Database, ArrowRight, Lock, Server, Globe, Layers } from 'lucide-react'

const nodes = [
  { icon: Mic, label: 'Voice Input', sub: 'Bhashini API', x: 8, y: 50 },
  { icon: Globe, label: 'Language Layer', sub: 'Hindi / Bengali / Tamil', x: 22, y: 35 },
  { icon: Layers, label: 'LangGraph', sub: 'Agent Orchestrator', x: 36, y: 50 },
  { icon: Database, label: 'Shared Memory', sub: 'Redis + Vector DB', x: 50, y: 35 },
  { icon: Brain, label: 'Agent Layer', sub: 'Mitra · Margdarshan · Saathi', x: 64, y: 50 },
  { icon: Zap, label: 'Guardrails', sub: 'Confidence Engine', x: 78, y: 35 },
  { icon: Lock, label: 'MPIN / Biometric', sub: 'Human-in-the-Loop', x: 92, y: 50 },
]

const lines = [
  { from: { x: 14, y: 55 }, to: { x: 28, y: 40 } },
  { from: { x: 28, y: 40 }, to: { x: 42, y: 52 } },
  { from: { x: 42, y: 52 }, to: { x: 56, y: 40 } },
  { from: { x: 56, y: 40 }, to: { x: 70, y: 52 } },
  { from: { x: 70, y: 52 }, to: { x: 84, y: 40 } },
  { from: { x: 84, y: 40 }, to: { x: 97, y: 52 } },
]

export default function ArchitectureSection() {
  return (
    <section id="architecture" className="py-24 bg-[#0D1B2A] relative overflow-hidden">
      <div className="absolute inset-0 bg-grid opacity-20" />
      <div className="relative z-10 max-w-7xl mx-auto px-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: '-100px' }}
          transition={{ duration: 0.5 }}
          className="text-center max-w-3xl mx-auto mb-16"
        >
          <span className="text-accent text-sm font-medium tracking-wider uppercase">Technical Architecture</span>
          <h2 className="text-3xl md:text-4xl font-bold text-white mt-3 tracking-tight">
            Enterprise-Grade AI Infrastructure
          </h2>
          <p className="text-white/40 mt-4 leading-relaxed">
            From voice input to secure execution — every layer is designed for scale, security, and India&apos;s diverse linguistic landscape.
          </p>
        </motion.div>

        {/* Architecture diagram */}
        <div className="relative max-w-5xl mx-auto">
          {/* Connection lines */}
          <svg className="absolute inset-0 w-full h-full pointer-events-none" viewBox="0 0 100 100">
            {lines.map((line, idx) => (
              <motion.line
                key={idx}
                x1={line.from.x}
                y1={line.from.y}
                x2={line.to.x}
                y2={line.to.y}
                stroke="rgba(15,110,86,0.2)"
                strokeWidth="0.3"
                strokeDasharray="1,1"
                initial={{ pathLength: 0 }}
                whileInView={{ pathLength: 1 }}
                viewport={{ once: true }}
                transition={{ delay: idx * 0.15, duration: 0.6 }}
              />
            ))}
          </svg>

          {/* Nodes */}
          <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-7 gap-4">
            {nodes.map((node, idx) => {
              const Icon = node.icon
              return (
                <motion.div
                  key={node.label}
                  initial={{ opacity: 0, y: 15, scale: 0.9 }}
                  whileInView={{ opacity: 1, y: 0, scale: 1 }}
                  viewport={{ once: true }}
                  transition={{ delay: idx * 0.12, duration: 0.4 }}
                  whileHover={{ y: -3, scale: 1.02 }}
                  className="bg-white/[0.04] border border-white/10 rounded-xl p-4 text-center group hover:bg-white/[0.08] hover:border-accent/30 transition-all"
                >
                  <div className="w-10 h-10 rounded-xl bg-accent/10 flex items-center justify-center mx-auto mb-2 group-hover:bg-accent/20 transition-colors">
                    <Icon size={18} className="text-accent" />
                  </div>
                  <p className="text-xs font-medium text-white/80">{node.label}</p>
                  <p className="text-[10px] text-white/30 mt-0.5">{node.sub}</p>
                </motion.div>
              )
            })}
          </div>
        </div>

        {/* Tech stack */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: '-50px' }}
          className="mt-16 grid md:grid-cols-3 gap-6"
        >
          {[
            {
              title: 'AI & Orchestration',
              items: ['Google Gemini', 'LangGraph', 'LangChain', 'Confidence Engine'],
            },
            {
              title: 'Voice & Language',
              items: ['Bhashini API', 'Web Speech API', 'Hindi / Bengali / Tamil TTS', 'Noto Sans Devanagari'],
            },
            {
              title: 'Security & Data',
              items: ['Redis + Vector Memory', 'MPIN + Biometric Gate', 'Pydantic Validation', 'DPDP Compliant Audit'],
            },
          ].map((stack, idx) => (
            <motion.div
              key={idx}
              initial={{ opacity: 0, y: 15 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: idx * 0.1 }}
              className="bg-white/[0.03] border border-white/5 rounded-xl p-5"
            >
              <h3 className="text-sm font-semibold text-white mb-3">{stack.title}</h3>
              <div className="flex flex-wrap gap-2">
                {stack.items.map((item) => (
                  <span
                    key={item}
                    className="px-2.5 py-1 text-[11px] font-medium bg-white/5 text-white/50 rounded-md"
                  >
                    {item}
                  </span>
                ))}
              </div>
            </motion.div>
          ))}
        </motion.div>
      </div>
    </section>
  )
}
