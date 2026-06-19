'use client'
import { useState } from 'react'
import { Languages, Check } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'
import { Language } from '@/types/agent'
import { useCustomerStore } from '@/store/useCustomerStore'

const languages: { code: Language; label: string; native: string }[] = [
  { code: 'hi', label: 'Hindi', native: 'हिंदी' },
  { code: 'bn', label: 'Bengali', native: 'বাংলা' },
  { code: 'ta', label: 'Tamil', native: 'தமிழ்' },
  { code: 'en', label: 'English', native: 'English' },
]

export default function LanguageSelector() {
  const [open, setOpen] = useState(false)
  const currentLang = useCustomerStore((s) => s.customer?.language || 'en')
  const setLanguage = useCustomerStore((s) => s.setLanguage)

  const selected = languages.find((l) => l.code === currentLang)

  return (
    <div className="relative">
      <button
        onClick={() => setOpen(!open)}
        className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg hover:bg-primary-light transition-colors text-text-muted hover:text-primary text-xs font-medium"
      >
        <Languages size={14} />
        <span>{selected?.native || 'English'}</span>
      </button>
      <AnimatePresence>
        {open && (
          <motion.div
            initial={{ opacity: 0, y: -4 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -4 }}
            transition={{ duration: 0.15 }}
            className="absolute right-0 top-full mt-1 w-44 bg-white rounded-card shadow-modal border border-[rgba(26,58,92,0.10)] py-1 z-50"
          >
            {languages.map((lang) => {
              const isActive = lang.code === currentLang
              return (
                <button
                  key={lang.code}
                  onClick={() => { setLanguage(lang.code); setOpen(false) }}
                  className={`w-full flex items-center justify-between px-3 py-2 text-sm transition-colors ${
                    isActive ? 'text-primary font-medium bg-primary-light' : 'text-text-muted hover:bg-surface'
                  }`}
                >
                  <span>{lang.native}</span>
                  {isActive && <Check size={14} className="text-accent" />}
                </button>
              )
            })}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}
