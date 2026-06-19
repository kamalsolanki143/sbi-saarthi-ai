'use client'
import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Menu, X } from 'lucide-react'

interface NavbarProps {
  onSignIn: () => void
  onCreateAccount: () => void
}

const navLinks = [
  { href: '#features', label: 'Features' },
  { href: '#agents', label: 'Agents' },
  { href: '#architecture', label: 'Architecture' },
  { href: '#security', label: 'Security' },
  { href: '#faq', label: 'FAQ' },
]

export default function Navbar({ onSignIn, onCreateAccount }: NavbarProps) {
  const [scrolled, setScrolled] = useState(false)
  const [mobileOpen, setMobileOpen] = useState(false)

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 40)
    window.addEventListener('scroll', onScroll, { passive: true })
    return () => window.removeEventListener('scroll', onScroll)
  }, [])

  return (
    <header
      className={`fixed top-0 left-0 right-0 z-50 transition-all duration-500 ${
        scrolled
          ? 'bg-[rgba(13,27,42,0.85)] backdrop-blur-xl border-b border-white/5 shadow-lg shadow-black/10'
          : 'bg-transparent'
      }`}
    >
      <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
        <a href="#" className="flex items-center gap-2">
          <span className="text-xl font-bold tracking-tight">
            <span className="text-gold">SAARTHI</span>
            <sup className="text-white/50 text-[10px] ml-0.5">AI</sup>
          </span>
        </a>

        <nav className="hidden md:flex items-center gap-1">
          {navLinks.map((link) => (
            <a
              key={link.href}
              href={link.href}
              className="px-3 py-2 text-sm text-white/60 hover:text-white/90 transition-colors rounded-lg hover:bg-white/5"
            >
              {link.label}
            </a>
          ))}
        </nav>

        <div className="hidden md:flex items-center gap-3">
          <button
            onClick={onSignIn}
            className="h-9 px-4 text-sm text-white/70 hover:text-white transition-colors"
          >
            Sign In
          </button>
          <button
            onClick={onCreateAccount}
            className="h-9 px-5 text-sm font-medium bg-accent text-white rounded-input hover:bg-accent-dark transition-all hover:shadow-lg hover:shadow-accent/25 active:scale-[0.97]"
          >
            Create Account
          </button>
        </div>

        <button
          onClick={() => setMobileOpen(!mobileOpen)}
          className="md:hidden p-2 text-white/60 hover:text-white"
        >
          {mobileOpen ? <X size={20} /> : <Menu size={20} />}
        </button>
      </div>

      <AnimatePresence>
        {mobileOpen && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="md:hidden bg-[rgba(13,27,42,0.95)] backdrop-blur-xl border-t border-white/5 overflow-hidden"
          >
            <div className="px-6 py-4 space-y-2">
              {navLinks.map((link) => (
                <a
                  key={link.href}
                  href={link.href}
                  onClick={() => setMobileOpen(false)}
                  className="block px-3 py-2 text-sm text-white/60 hover:text-white/90 rounded-lg hover:bg-white/5"
                >
                  {link.label}
                </a>
              ))}
              <div className="pt-3 space-y-2">
                <button
                  onClick={() => { onSignIn(); setMobileOpen(false) }}
                  className="w-full h-10 text-sm text-white/70 hover:text-white border border-white/10 rounded-input"
                >
                  Sign In
                </button>
                <button
                  onClick={() => { onCreateAccount(); setMobileOpen(false) }}
                  className="w-full h-10 text-sm font-medium bg-accent text-white rounded-input"
                >
                  Create Account
                </button>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </header>
  )
}
