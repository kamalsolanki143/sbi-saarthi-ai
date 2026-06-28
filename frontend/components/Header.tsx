'use client'
import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { motion, AnimatePresence } from 'framer-motion'
import { X, CheckCircle2, Loader2 } from 'lucide-react'
import Navbar from '@/components/Navbar'
import Hero from '@/components/Hero'
import WhyUs from '@/components/WhyUs'
import Features from '@/components/Features'
import AgentShowcase from '@/components/AgentShowcase'
import AgentsSection from '@/components/AgentsSection/AgentsSection'
import ArchitectureSection from '@/components/ArchitectureSection/ArchitectureSection'
import SecuritySection from '@/components/SecuritySection/SecuritySection'
import FAQ from '@/components/FAQ'
import CTA from '@/components/CTA'
import Footer from '@/components/Footer'
import { useCustomerStore } from '@/store/useCustomerStore'

const DEMO_CREDENTIALS: Record<string, string> = {
  'rameshwar@demo.com': 'demo1234',
  'farmer@demo.com': 'demo1234',
  'merchant@demo.com': 'demo1234',
  'test@demo.com': 'test1234',
}

const DEMO_ACCOUNTS: Record<string, string> = {
  'rameshwar@demo.com': 'Rameshwar Prasad',
  'farmer@demo.com': 'Rameshwar Prasad',
  'merchant@demo.com': 'Priya Sharma',
  'test@demo.com': 'Test User',
}

export default function Header() {
  const [authOpen, setAuthOpen] = useState(false)
  const [authMode, setAuthMode] = useState<'signin' | 'create'>('signin')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [name, setName] = useState('')
  const [loading, setLoading] = useState(false)
  const [done, setDone] = useState(false)
  const [error, setError] = useState('')
  const router = useRouter()
  const fetchCustomer = useCustomerStore((s) => s.fetchCustomer)

  const openSignIn = () => {
    setAuthMode('signin')
    setAuthOpen(true)
  }

  const openCreate = () => {
    setAuthMode('create')
    setAuthOpen(true)
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')

    if (authMode === 'signin') {
      const expectedPassword = DEMO_CREDENTIALS[email.toLowerCase()]
      if (!expectedPassword || password !== expectedPassword) {
        setError('Invalid email or password. Try rameshwar@demo.com / demo1234')
        return
      }
    }

    setLoading(true)
    await new Promise((r) => setTimeout(r, 1200))
    setLoading(false)
    setDone(true)
    await fetchCustomer(process.env.NEXT_PUBLIC_DEMO_CUSTOMER_ID || 'CUST001')
    setTimeout(() => {
      setAuthOpen(false)
      setDone(false)
      setEmail('')
      setPassword('')
      setName('')
      setError('')
      router.push('/dashboard')
    }, 600)
  }

  return (
    <>
      <Navbar onSignIn={openSignIn} onCreateAccount={openCreate} />
      <Hero onSignIn={openSignIn} onCreateAccount={openCreate} />
      <WhyUs />
      <Features />
      <AgentShowcase />
      <AgentsSection />
      <ArchitectureSection />
      <SecuritySection />
      <FAQ />
      <CTA onSignIn={openSignIn} onCreateAccount={openCreate} />
      <Footer />

      {/* Auth Modal */}
      <AnimatePresence>
        {authOpen && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-[60] flex items-center justify-center p-4"
            style={{ background: 'rgba(6,14,26,0.8)', backdropFilter: 'blur(8px)' }}
          >
            <motion.div
              initial={{ scale: 0.95, opacity: 0, y: 10 }}
              animate={{ scale: 1, opacity: 1, y: 0 }}
              exit={{ scale: 0.95, opacity: 0, y: 10 }}
              transition={{ type: 'spring', stiffness: 300, damping: 30 }}
              className="bg-[#0D1B2A] border border-white/10 rounded-2xl w-full max-w-md p-8 shadow-2xl"
            >
              {done ? (
                <div className="text-center py-6">
                  <div className="w-16 h-16 rounded-full bg-accent/20 flex items-center justify-center mx-auto mb-4">
                    <CheckCircle2 size={32} className="text-accent" />
                  </div>
                  <h3 className="text-xl font-bold text-white">Welcome to SAARTHI</h3>
                  <p className="text-sm text-white/50 mt-1">Redirecting to your dashboard...</p>
                </div>
              ) : (
                <>
                  <div className="flex items-center justify-between mb-6">
                    <h3 className="text-xl font-bold text-white">
                      {authMode === 'signin' ? 'Sign In' : 'Create Account'}
                    </h3>
                    <button
                      onClick={() => setAuthOpen(false)}
                      className="p-1 rounded-lg hover:bg-white/5 text-white/40 hover:text-white/70"
                    >
                      <X size={18} />
                    </button>
                  </div>

                  <form onSubmit={handleSubmit} className="space-y-4">
                    {authMode === 'create' && (
                      <div>
                        <label className="text-xs text-white/50 block mb-1.5">Full Name</label>
                        <input
                          value={name}
                          onChange={(e) => setName(e.target.value)}
                          placeholder="Rameshwar Prasad"
                          required
                          className="w-full h-11 px-4 bg-white/5 border border-white/10 rounded-input text-sm text-white placeholder:text-white/20 focus:border-accent/50 focus:ring-2 focus:ring-accent/10 transition-all"
                        />
                      </div>
                    )}
                    <div>
                      <label className="text-xs text-white/50 block mb-1.5">Email</label>
                      <input
                        type="email"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        placeholder="rameshwar@demo.com"
                        required
                        className="w-full h-11 px-4 bg-white/5 border border-white/10 rounded-input text-sm text-white placeholder:text-white/20 focus:border-accent/50 focus:ring-2 focus:ring-accent/10 transition-all"
                      />
                    </div>
                    <div>
                      <label className="text-xs text-white/50 block mb-1.5">Password</label>
                      <input
                        type="password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        placeholder="demo1234"
                        required
                        className="w-full h-11 px-4 bg-white/5 border border-white/10 rounded-input text-sm text-white placeholder:text-white/20 focus:border-accent/50 focus:ring-2 focus:ring-accent/10 transition-all"
                      />
                    </div>

                    {error && (
                      <p className="text-xs text-danger bg-danger/10 px-3 py-2 rounded-lg">{error}</p>
                    )}

                    <button
                      type="submit"
                      disabled={loading}
                      className="w-full h-11 bg-accent text-white font-medium rounded-input hover:bg-accent-dark transition-all disabled:opacity-50 flex items-center justify-center gap-2"
                    >
                      {loading ? (
                        <>
                          <Loader2 size={16} className="animate-spin" />
                          Please wait...
                        </>
                      ) : authMode === 'signin' ? (
                        'Sign In'
                      ) : (
                        'Create Account'
                      )}
                    </button>
                  </form>

                  <div className="mt-4 text-center space-y-1">
                    <p className="text-xs text-white/30">
                      Demo environment &middot; Mock SBI-safe data
                    </p>
                    <p className="text-xs text-white/20">
                      Try: <span className="text-accent/60">rameshwar@demo.com</span> / <span className="text-accent/60">demo1234</span>
                    </p>
                  </div>

                  {authMode === 'signin' ? (
                    <p className="mt-4 text-center text-sm text-white/40">
                      No account?{' '}
                      <button onClick={() => setAuthMode('create')} className="text-accent hover:text-accent/80">
                        Create one
                      </button>
                    </p>
                  ) : (
                    <p className="mt-4 text-center text-sm text-white/40">
                      Already have an account?{' '}
                      <button onClick={() => setAuthMode('signin')} className="text-accent hover:text-accent/80">
                        Sign in
                      </button>
                    </p>
                  )}
                </>
              )}
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  )
}