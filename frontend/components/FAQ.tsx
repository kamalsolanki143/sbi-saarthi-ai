'use client'
import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { ChevronDown } from 'lucide-react'

const faqs = [
  {
    q: 'What is SAARTHI AI?',
    a: 'SAARTHI AI is an agentic AI banking companion built for SBI. It uses three specialized AI agents — Mitra (acquisition), Margdarshan (adoption), and Saathi (engagement) — to help customers discover, use, and benefit from digital banking services through voice conversations in Hindi, Bengali, and Tamil.',
  },
  {
    q: 'Does SAARTHI move money automatically?',
    a: 'No. SAARTHI cannot execute any transaction autonomously. It generates recommendations and prepares action previews, but every action requires explicit MPIN or biometric confirmation from the customer. This is a hard architectural constraint, not a preference.',
  },
  {
    q: 'Which languages are supported?',
    a: 'Currently Hindi, Bengali, and Tamil with English fallback. The voice interface uses Bhashini API for speech recognition and synthesis. More Indian languages are being added.',
  },
  {
    q: 'How does SAARTHI protect my data?',
    a: 'SAARTHI is built in compliance with DPDP Act principles. Explicit consent is required for voice processing, memory storage, and personalization. All decisions are logged in an immutable audit trail. Customers can revoke consent and clear conversation memory at any time.',
  },
  {
    q: 'What is the confidence engine?',
    a: 'Every agent recommendation includes a confidence score (0-100%). If confidence drops below 85%, SAARTHI displays a fallback notice advising the customer to verify with a branch or call the SBI helpline before proceeding.',
  },
  {
    q: 'Can I try the demo?',
    a: 'Yes! Click "Create Account" or "Sign In" to access the demo dashboard. It uses mock data simulating a farmer customer from Varanasi. The demo showcases the Margdarshan agent detecting an idle balance and recommending a Fixed Deposit — the full flow from trigger to MPIN confirmation.',
  },
  {
    q: 'What technology powers SAARTHI?',
    a: 'Backend: FastAPI + Python 3.11. AI Layer: Google Gemini + LangGraph + LangChain. Voice: Bhashini API. Frontend: Next.js 14 + TypeScript + Tailwind CSS. Memory: Redis + Vector DB. Validation: Pydantic.',
  },
  {
    q: 'Is SAARTHI a real SBI product?',
    a: 'SAARTHI AI is a hackathon project built for the SBI Hackathon at Global Fintech Fest 2026. It demonstrates the potential of agentic AI for digital banking inclusion. It is not currently a live SBI product.',
  },
]

export default function FAQ() {
  const [openIdx, setOpenIdx] = useState<number | null>(null)

  return (
    <section id="faq" className="py-24 bg-[#0D1B2A] relative overflow-hidden">
      <div className="absolute inset-0 bg-grid opacity-20" />
      <div className="relative z-10 max-w-3xl mx-auto px-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: '-100px' }}
          transition={{ duration: 0.5 }}
          className="text-center mb-12"
        >
          <span className="text-accent text-sm font-medium tracking-wider uppercase">FAQ</span>
          <h2 className="text-3xl md:text-4xl font-bold text-white mt-3 tracking-tight">
            Common Questions
          </h2>
        </motion.div>

        <div className="space-y-2">
          {faqs.map((faq, idx) => {
            const isOpen = openIdx === idx
            return (
              <motion.div
                key={idx}
                initial={{ opacity: 0, y: 8 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true, margin: '-30px' }}
                transition={{ delay: idx * 0.03 }}
                className="bg-white/[0.03] border border-white/5 rounded-xl overflow-hidden"
              >
                <button
                  onClick={() => setOpenIdx(isOpen ? null : idx)}
                  className="w-full flex items-center justify-between px-5 py-4 text-left"
                >
                  <span className="text-sm font-medium text-white/80">{faq.q}</span>
                  <ChevronDown
                    size={16}
                    className={`text-white/30 transition-transform duration-200 ${
                      isOpen ? 'rotate-180' : ''
                    }`}
                  />
                </button>
                <AnimatePresence>
                  {isOpen && (
                    <motion.div
                      initial={{ height: 0, opacity: 0 }}
                      animate={{ height: 'auto', opacity: 1 }}
                      exit={{ height: 0, opacity: 0 }}
                      transition={{ duration: 0.2 }}
                      className="overflow-hidden"
                    >
                      <p className="px-5 pb-4 text-sm text-white/50 leading-relaxed">{faq.a}</p>
                    </motion.div>
                  )}
                </AnimatePresence>
              </motion.div>
            )
          })}
        </div>
      </div>
    </section>
  )
}
