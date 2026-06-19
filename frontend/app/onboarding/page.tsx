'use client'
import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Check, Upload, Mic } from 'lucide-react'
import { useRouter } from 'next/navigation'
import TopBar from '@/components/shared/TopBar'
import LanguageSelector from '@/components/LanguageSelector/LanguageSelector'
import VoiceInput from '@/components/VoiceInput/VoiceInput'
import { useCustomerStore } from '@/store/useCustomerStore'
import { useT } from '@/services/translations'

const steps = [
  { title: 'Language', title_hi: 'भाषा चुनें' },
  { title: 'Voice KYC', title_hi: 'आवाज़ KYC' },
  { title: 'Documents', title_hi: 'दस्तावेज़' },
  { title: 'Account Type', title_hi: 'खाता प्रकार' },
]

const pageVariants = {
  initial: { opacity: 0, y: 16 },
  animate: { opacity: 1, y: 0, transition: { duration: 0.3, ease: [0.22, 1, 0.36, 1] } },
}

export default function Onboarding() {
  const [step, setStep] = useState(0)
  const router = useRouter()
  const language = useCustomerStore((s) => s.customer?.language || 'hi')
  const [transcript, setTranscript] = useState('')
  const _t = useT()
  const isHindi = language === 'hi' || language === 'bn'

  const handleTranscription = (text: string) => {
    setTranscript(text)
  }

  const renderStep = () => {
    switch (step) {
      case 0:
        return (
          <div className="text-center max-w-md mx-auto">
            <h3 className="text-3xl font-bold text-primary mb-2 text-devanagari">
              आपका स्वागत है
            </h3>
            <p className="text-text-muted text-sm mb-8">Choose your preferred language</p>
            <div className="flex justify-center">
              <LanguageSelector />
            </div>
          </div>
        )
      case 1:
        return (
          <div className="max-w-md mx-auto text-center">
            <div className="w-16 h-16 rounded-full bg-primary-light flex items-center justify-center mx-auto mb-4">
              <Mic size={28} className="text-primary" />
            </div>
            <h3 className="text-xl font-semibold text-primary mb-2">
              {_t('Please say your name and village')}
            </h3>
            <div className="flex justify-center mt-6">
              <VoiceInput onTranscription={handleTranscription} language={language as any} />
            </div>
            {transcript && (
              <motion.p
                initial={{ opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                className="mt-4 text-sm text-text-muted bg-surface p-3 rounded-card"
              >
                {transcript}
              </motion.p>
            )}
          </div>
        )
      case 2:
        return (
          <div className="max-w-md mx-auto text-center">
            <div className="w-16 h-16 rounded-full bg-primary-light flex items-center justify-center mx-auto mb-4">
              <Upload size={28} className="text-primary" />
            </div>
            <h3 className="text-xl font-semibold text-primary mb-2">
              {_t('Upload your documents')}
            </h3>
            <p className="text-text-muted text-sm mb-6">Aadhaar / PAN Card photo</p>
            <div className="border-2 border-dashed border-[rgba(26,58,92,0.15)] rounded-card p-8 hover:border-primary/30 transition-colors cursor-pointer bg-surface/50">
              <Upload size={24} className="mx-auto text-text-hint mb-2" />
              <p className="text-xs text-text-muted">Tap to upload or drag & drop</p>
              <p className="text-[10px] text-text-hint mt-1">JPG, PNG or PDF (max 5MB)</p>
            </div>
          </div>
        )
      case 3:
        return (
          <div className="max-w-lg mx-auto">
            <h3 className="text-xl font-semibold text-primary text-center mb-6">
              {_t('Select Account Type')}
            </h3>
            <div className="grid grid-cols-2 gap-4">
              {[
                { title: 'Savings', desc: 'Daily banking & savings', icon: '🏦' },
                { title: 'Current', desc: 'Business & trade', icon: '💼' },
                { title: 'Mudra Loan', desc: 'Small business loan', icon: '🌱' },
                { title: 'Fixed Deposit', desc: 'Term investment', icon: '📈' },
              ].map((item) => (
                <motion.button
                  key={item.title}
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.97 }}
                  className="p-5 bg-white rounded-card border border-[rgba(26,58,92,0.10)] shadow-card text-left hover:border-accent/30 transition-colors"
                >
                  <span className="text-2xl">{item.icon}</span>
                  <h4 className="text-sm font-semibold text-primary mt-2">{item.title}</h4>
                  <p className="text-xs text-text-muted mt-0.5">{item.desc}</p>
                </motion.button>
              ))}
            </div>
          </div>
        )
    }
  }

  return (
    <>
      <TopBar title={_t('Onboarding')} />
      <motion.div
        variants={pageVariants}
        initial="initial"
        animate="animate"
        className="flex-1 overflow-y-auto p-8"
      >
        {/* Stepper */}
        <div className="flex items-center justify-center gap-2 mb-10">
          {steps.map((s, idx) => (
            <div key={idx} className="flex items-center gap-2">
              <div className={`flex items-center gap-2 px-3 py-1.5 rounded-badge text-xs font-medium transition-colors ${
                idx === step ? 'bg-primary text-white' : idx < step ? 'bg-accent-light text-accent-dark' : 'bg-surface text-text-muted'
              }`}>
                {idx < step ? <Check size={12} /> : <span>{idx + 1}</span>}
                <span>            {isHindi ? s.title_hi : _t(s.title)}</span>
              </div>
              {idx < steps.length - 1 && (
                <div className={`w-8 h-px ${idx < step ? 'bg-accent' : 'bg-[rgba(26,58,92,0.10)]'}`} />
              )}
            </div>
          ))}
        </div>

        <AnimatePresence mode="wait">
          <motion.div
            key={step}
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            transition={{ duration: 0.2 }}
          >
            {renderStep()}
          </motion.div>
        </AnimatePresence>

        {/* Navigation buttons */}
        <div className="flex items-center justify-center gap-4 mt-10">
          {step > 0 && (
            <button
              onClick={() => setStep(step - 1)}
              className="h-11 px-6 rounded-input border border-[rgba(26,58,92,0.20)] text-primary text-sm font-medium hover:bg-primary-light transition-colors"
            >
              {isHindi ? 'पीछे' : 'Back'}
            </button>
          )}
          {step < steps.length - 1 ? (
            <button
              onClick={() => setStep(step + 1)}
              className="h-11 px-6 rounded-input bg-accent text-white text-sm font-medium hover:bg-accent-dark transition-colors"
            >
              {isHindi ? 'अगला' : 'Next'}
            </button>
          ) : (
            <button
              onClick={() => router.push('/dashboard')}
              className="h-11 px-6 rounded-input bg-accent text-white text-sm font-medium hover:bg-accent-dark transition-colors"
            >
              {isHindi ? 'समाप्त' : 'Finish'}
            </button>
          )}
        </div>
      </motion.div>
    </>
  )
}
