'use client'
import { motion } from 'framer-motion'
import { ArrowRight, Sparkles } from 'lucide-react'

interface CTAProps {
  onSignIn: () => void
  onCreateAccount: () => void
}

export default function CTA({ onSignIn, onCreateAccount }: CTAProps) {
  return (
    <section className="py-24 bg-[#0A1628] relative overflow-hidden">
      <div className="absolute inset-0">
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[60%] h-[60%] rounded-full bg-accent/5 blur-[120px]" />
        <div className="absolute inset-0 bg-grid-dark opacity-20" />
      </div>

      <div className="relative z-10 max-w-3xl mx-auto px-6 text-center">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: '-100px' }}
          transition={{ duration: 0.5 }}
        >
          <div className="w-14 h-14 rounded-2xl bg-accent/10 flex items-center justify-center mx-auto mb-6">
            <Sparkles size={28} className="text-accent" />
          </div>

          <h2 className="text-3xl md:text-5xl font-bold text-white tracking-tight">
            Ready to Experience{' '}
            <span className="text-gradient bg-gradient-to-r from-accent to-gold">Banking Reimagined</span>
          </h2>

          <p className="mt-4 text-lg text-white/50 max-w-xl mx-auto leading-relaxed">
            See how agentic AI can transform banking for India&apos;s billion-plus customers.
            The demo uses mock data — no real account needed.
          </p>

          <div className="mt-8 flex flex-wrap items-center justify-center gap-4">
            <button
              onClick={onCreateAccount}
              className="group h-12 px-8 bg-accent text-white font-medium rounded-input hover:bg-accent-dark transition-all hover:shadow-xl hover:shadow-accent/25 active:scale-[0.98] flex items-center gap-2"
            >
              Create Account
              <ArrowRight size={16} className="group-hover:translate-x-0.5 transition-transform" />
            </button>
            <button
              onClick={onSignIn}
              className="h-12 px-8 border border-white/15 text-white/70 hover:text-white hover:border-white/30 rounded-input transition-all"
            >
              Sign In
            </button>
          </div>

          <p className="mt-4 text-xs text-white/30">
            Demo environment powered by mock SBI-safe data. No real transactions.
          </p>
        </motion.div>
      </div>
    </section>
  )
}
