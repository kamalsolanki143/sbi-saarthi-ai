'use client'
import { useState, useRef, useEffect } from 'react'
import { Lock, X } from 'lucide-react'
import { motion } from 'framer-motion'
import { api } from '@/services/api'
import { useCustomerStore } from '@/store/useCustomerStore'

interface Props {
  actionLabel: string
  onSuccess: () => void
  onCancel: () => void
}

export default function MPINVerification({ actionLabel, onSuccess, onCancel }: Props) {
  const customer = useCustomerStore((s) => s.customer)
  const [digits, setDigits] = useState<string[]>(Array(6).fill(''))
  const [activeIdx, setActiveIdx] = useState(0)
  const [error, setError] = useState('')
  const [verifying, setVerifying] = useState(false)
  const [success, setSuccess] = useState(false)
  const inputRefs = useRef<(HTMLInputElement | null)[]>(Array(6).fill(null))

  useEffect(() => {
    inputRefs.current[0]?.focus()
  }, [])

  const handleChange = (idx: number, val: string) => {
    if (verifying || success) return
    if (val.length > 1) val = val.slice(-1)
    if (val && !/^\d$/.test(val)) return

    const newDigits = [...digits]
    newDigits[idx] = val
    setDigits(newDigits)
    setError('')

    if (val && idx < 5) {
      setActiveIdx(idx + 1)
      inputRefs.current[idx + 1]?.focus()
    }
  }

  const handleKeyDown = (idx: number, e: React.KeyboardEvent) => {
    if (e.key === 'Backspace' && !digits[idx] && idx > 0) {
      setActiveIdx(idx - 1)
      inputRefs.current[idx - 1]?.focus()
    }
  }

  useEffect(() => {
    if (digits.every((d) => d !== '') && !verifying && !success) {
      handleVerify()
    }
  }, [digits])

  const handleVerify = async () => {
    setVerifying(true)
    const mpinCode = digits.join('')

    try {
      const res = await api.verifyMPIN(customer?.id || 'CUST001', mpinCode)
      if (res.data.verified) {
        setSuccess(true)
        setTimeout(() => {
          onSuccess()
        }, 1200)
      } else {
        setError('Incorrect MPIN. Try again.')
        setDigits(Array(6).fill(''))
        setActiveIdx(0)
        inputRefs.current[0]?.focus()
        const container = document.getElementById('mpin-boxes')
        container?.classList.add('shake')
        setTimeout(() => container?.classList.remove('shake'), 400)
      }
    } catch {
      setError('Verification failed. Try again.')
    } finally {
      setVerifying(false)
    }
  }

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 z-50 flex items-center justify-center"
      style={{ background: 'rgba(13,27,42,0.55)', backdropFilter: 'blur(4px)' }}
    >
      <motion.div
        initial={{ scale: 0.95, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        exit={{ scale: 0.95, opacity: 0 }}
        transition={{ type: 'spring', stiffness: 300, damping: 30 }}
        className="bg-white rounded-modal w-[380px] p-10 relative shadow-modal"
      >
        <button
          onClick={onCancel}
          className="absolute top-4 right-4 p-1 rounded-lg hover:bg-surface text-text-muted transition-colors"
        >
          <X size={18} />
        </button>

        {success ? (
          <div className="flex flex-col items-center py-8">
            <div className="relative w-16 h-16 mb-4">
              <div className="absolute inset-0 rounded-full bg-accent/20 success-ripple" />
              <div className="relative w-16 h-16 rounded-full bg-accent flex items-center justify-center">
                <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2.5">
                  <motion.path
                    d="M5 13l4 4L19 7"
                    initial={{ pathLength: 0 }}
                    animate={{ pathLength: 1 }}
                    transition={{ duration: 0.6, ease: 'easeInOut' }}
                  />
                </svg>
              </div>
            </div>
            <h3 className="text-lg font-semibold text-primary">Authorized</h3>
            <p className="text-sm text-text-muted mt-1">Action confirmed successfully</p>
          </div>
        ) : (
          <>
            <div className="flex flex-col items-center mb-6">
              <div className="w-12 h-12 rounded-full bg-gold-light flex items-center justify-center mb-4">
                <Lock size={24} className="text-warning" />
              </div>
              <h3 className="text-xl font-semibold text-primary tracking-tight">Confirm with MPIN</h3>
              <p className="text-xs text-danger mt-1.5 text-center max-w-[240px]">
                AI cannot proceed without your explicit authorization
              </p>
              <p className="text-xs text-text-muted mt-2 text-center">{actionLabel}</p>
            </div>

            <div id="mpin-boxes" className="flex justify-center gap-2.5 mb-6">
              {digits.map((d, idx) => (
                <motion.div
                  key={idx}
                  animate={d ? { scale: [1, 1.15, 1], backgroundColor: '#1A3A5C' } : {}}
                  transition={{ duration: 0.15 }}
                  className={`w-12 h-12 rounded-input border-2 flex items-center justify-center transition-colors ${
                    activeIdx === idx && !d ? 'border-primary' : 'border-[rgba(26,58,92,0.15)]'
                  } ${d ? 'bg-primary' : 'bg-white'}`}
                  onClick={() => inputRefs.current[idx]?.focus()}
                >
                  <input
                    ref={(el) => { inputRefs.current[idx] = el }}
                    type="tel"
                    maxLength={1}
                    value={d}
                    onChange={(e) => handleChange(idx, e.target.value)}
                    onKeyDown={(e) => handleKeyDown(idx, e)}
                    onFocus={() => setActiveIdx(idx)}
                    className="w-full h-full bg-transparent text-center text-lg outline-none"
                    style={{
                      color: d ? 'white' : '#0D1B2A',
                      caretColor: '#1A3A5C',
                    }}
                  />
                </motion.div>
              ))}
            </div>

            {error && (
              <p className="text-xs text-danger text-center mb-4">{error}</p>
            )}

            {verifying && (
              <div className="flex items-center justify-center gap-2 mb-4">
                <span className="w-2 h-2 rounded-full bg-accent animate-pulse" />
                <span className="text-xs text-text-muted">Verifying...</span>
              </div>
            )}

            <button
              onClick={onCancel}
              className="w-full text-center text-xs text-text-hover hover:text-primary transition-colors"
            >
              Cancel
            </button>
          </>
        )}
      </motion.div>
    </motion.div>
  )
}
