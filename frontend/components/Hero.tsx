'use client'
import { motion } from 'framer-motion'
import { ArrowRight, ShieldCheck, Mic, Zap } from 'lucide-react'

interface HeroProps {
  onSignIn: () => void
  onCreateAccount: () => void
}

const floatingCards = [
  { icon: Mic, label: 'Voice Banking', sub: 'Hindi & English', color: '#0F6E56', delay: 0.2, x: '15%', y: '25%' },
  { icon: Zap, label: 'Event Alert', sub: 'Subsidiy Credited', color: '#C9A84C', delay: 0.4, x: '80%', y: '20%' },
  { icon: ShieldCheck, label: 'Secure Action', sub: 'MPIN Verified', color: '#BA7517', delay: 0.6, x: '85%', y: '65%' },
]

export default function Hero({ onSignIn, onCreateAccount }: HeroProps) {
  return (
    <section className="relative min-h-screen flex items-center overflow-hidden bg-[#0A1628]">
      {/* Background gradient */}
      <div className="absolute inset-0">
        <div className="absolute top-[-20%] left-[-10%] w-[60%] h-[60%] rounded-full bg-accent/5 blur-[120px] animate-blob" />
        <div className="absolute bottom-[-20%] right-[-10%] w-[50%] h-[50%] rounded-full bg-primary/20 blur-[100px] animate-blob-delayed" />
        <div className="absolute top-[40%] left-[40%] w-[40%] h-[40%] rounded-full bg-gold/5 blur-[80px] animate-pulse-slow" />
        <div className="absolute inset-0 bg-grid-dark opacity-40" />
      </div>

      {/* Floating cards */}
      {floatingCards.map((card) => {
        const Icon = card.icon
        return (
          <motion.div
            key={card.label}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: card.delay + 0.5, duration: 0.6 }}
            className="hidden lg:block absolute"
            style={{ left: card.x, top: card.y }}
          >
            <motion.div
              animate={{ y: [0, -8, 0] }}
              transition={{ duration: 4, repeat: Infinity, delay: card.delay }}
              className="bg-[rgba(13,27,42,0.7)] backdrop-blur-xl border border-white/10 rounded-xl p-3 shadow-xl shadow-black/20 min-w-[160px]"
            >
              <div className="flex items-center gap-2">
                <div className="w-7 h-7 rounded-lg flex items-center justify-center" style={{ background: `${card.color}20` }}>
                  <Icon size={14} style={{ color: card.color }} />
                </div>
                <div>
                  <p className="text-xs font-medium text-white/90">{card.label}</p>
                  <p className="text-[10px] text-white/50">{card.sub}</p>
                </div>
              </div>
            </motion.div>
          </motion.div>
        )
      })}

      {/* Demo flow card */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 1.2, duration: 0.6 }}
        className="hidden lg:block absolute right-[8%] top-[38%]"
      >
        <motion.div
          animate={{ y: [0, -6, 0] }}
          transition={{ duration: 5, repeat: Infinity, delay: 0.8 }}
          className="bg-[rgba(13,27,42,0.8)] backdrop-blur-xl border border-white/10 rounded-xl p-4 shadow-xl shadow-black/20 min-w-[220px]"
        >
          <div className="flex items-center gap-2 mb-2">
            <span className="w-1.5 h-1.5 rounded-full bg-accent" />
            <span className="text-[10px] text-white/40 font-medium uppercase tracking-wider">Demo Flow</span>
          </div>
          <div className="space-y-2">
            {[
              { label: 'Subsidiy Credited', done: true },
              { label: 'Idle Balance Detected', done: true },
              { label: 'Margdarshan Agent', done: false },
              { label: 'MPIN Confirmation', done: false },
            ].map((step, idx) => (
              <div key={idx} className="flex items-center gap-2">
                <div className={`w-5 h-5 rounded-full flex items-center justify-center text-[9px] font-bold ${
                  step.done ? 'bg-accent text-white' : 'bg-white/10 text-white/30'
                }`}>
                  {step.done ? '✓' : idx + 1}
                </div>
                <span className={`text-xs ${step.done ? 'text-white/70' : 'text-white/30'}`}>
                  {step.label}
                </span>
              </div>
            ))}
          </div>
        </motion.div>
      </motion.div>

      {/* Content */}
      <div className="relative z-10 max-w-7xl mx-auto px-6 pt-32 pb-24">
        <div className="max-w-3xl">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, ease: [0.22, 1, 0.36, 1] }}
          >
            <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-accent/10 border border-accent/20 text-accent text-xs font-medium mb-6">
              <span className="w-1.5 h-1.5 rounded-full bg-accent animate-pulse" />
              SBI Hackathon @ GFF 2026
            </span>
          </motion.div>

          <motion.h1
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.1, ease: [0.22, 1, 0.36, 1] }}
            className="text-4xl md:text-6xl lg:text-7xl font-bold text-white leading-[1.1] tracking-tight"
          >
            From Banking{' '}
            <span className="text-gradient bg-gradient-to-r from-accent via-accent to-gold">Access</span>
            {' '}to{' '}
            <span className="text-gradient bg-gradient-to-r from-gold via-accent to-accent">Banking Success</span>
          </motion.h1>

          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.2, ease: [0.22, 1, 0.36, 1] }}
            className="mt-6 text-lg md:text-xl text-white/50 max-w-2xl leading-relaxed"
          >
            A voice-first, multilingual AI banking companion for SBI.
            SAARTHI understands your intent, recommends services, and
            guides you through banking workflows in your own language
            — with MPIN-secured human approval every step of the way.
          </motion.p>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.35, ease: [0.22, 1, 0.36, 1] }}
            className="mt-8 flex flex-wrap items-center gap-4"
          >
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
            <p className="text-xs text-white/30">Demo · Mock SBI-safe data</p>
          </motion.div>

          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.6, duration: 0.6 }}
            className="mt-10 flex items-center gap-6 text-white/30"
          >
            <div className="flex items-center gap-2">
              <ShieldCheck size={14} />
              <span className="text-xs">DPDP Compliant</span>
            </div>
            <div className="flex items-center gap-2">
              <Mic size={14} />
              <span className="text-xs">Hindi · Bengali · Tamil · English</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="w-1.5 h-1.5 rounded-full bg-accent" />
              <span className="text-xs">Human-in-the-Loop</span>
            </div>
          </motion.div>
        </div>
      </div>

      {/* Bottom gradient fade */}
      <div className="absolute bottom-0 left-0 right-0 h-32 bg-gradient-to-t from-[#0A1628] to-transparent" />
    </section>
  )
}