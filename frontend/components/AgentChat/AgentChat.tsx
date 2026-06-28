'use client'
import { useState, useEffect, useRef, useCallback } from 'react'
import { Send, Zap } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'
import { useAgentStore } from '@/store/useAgentStore'
import { useCustomerStore } from '@/store/useCustomerStore'
import { api } from '@/services/api'
import { agentSocket } from '@/services/websocket'
import { useAuditStore } from '@/store/useAuditStore'
import { AgentMessage as AgentMessageType, Language } from '@/types/agent'
import AgentMessage from './AgentMessage'
import AgentTypingIndicator from './AgentTypingIndicator'
import VoiceInput from '@/components/VoiceInput/VoiceInput'
import LanguageSelector from '@/components/LanguageSelector/LanguageSelector'
import ActionPreview from '@/components/ActionPreview/ActionPreview'
import MPINVerification from '@/components/MPINVerification/MPINVerification'
import AgentBadge from '@/components/shared/AgentBadge'

const containerVariants = {
  animate: { transition: { staggerChildren: 0.07 } },
}

export default function AgentChat() {
  const {
    messages,
    addMessage,
    pendingAction,
    setPendingAction,
    awaitingMPIN,
    setAwaitingMPIN,
    activeAgent,
    setActiveAgent,
    isProcessing,
    setProcessing,
    clearMessages,
  } = useAgentStore()

  const customer = useCustomerStore((s) => s.customer)
  const appendLog = useAuditStore((s) => s.appendLog)

  const [textInput, setTextInput] = useState('')
  const [demoTriggered, setDemoTriggered] = useState(false)
  const chatEndRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  useEffect(() => {
    if (!customer) return
    agentSocket.connect(customer.id)

    const unsub = agentSocket.onMessage((msg) => {
      addMessage(msg)
      if (msg.agent) setActiveAgent(msg.agent)
      if (msg.type === 'action_ready' && msg.action_payload) {
        setPendingAction(msg.action_payload)
      }
      if (msg.requires_mpin) {
        setAwaitingMPIN(true)
      }
      if (msg.type === 'completed') {
        appendLog({
          id: 'log_' + Date.now(),
          customer_id: customer.id,
          agent: msg.agent,
          action: msg.action_payload?.display_label || 'Action completed',
          status: 'success',
          timestamp: new Date().toISOString(),
          mpin_verified: true,
          confidence: msg.confidence,
        })
        setPendingAction(null)
        setAwaitingMPIN(false)
      }
    })

    return () => {
      unsub()
      agentSocket.disconnect()
    }
  }, [customer])

  const handleSend = useCallback(async (text: string) => {
    if (!text.trim() || !customer) return
    setProcessing(true)

    const userMsg: AgentMessageType = {
      id: 'user_' + Date.now(),
      type: 'agent_message',
      agent: activeAgent as any || 'margdarshan',
      content: text,
      language: customer.language,
      confidence: -1,
      timestamp: new Date(),
    }
    addMessage(userMsg)
    setTextInput('')

    try {
      await api.processVoice(text, customer.id, customer.language)
    } catch {}
  }, [customer, activeAgent, addMessage, setProcessing])

  const handleTranscription = useCallback((text: string) => {
    handleSend(text)
  }, [handleSend])

  const triggerDemo = useCallback(async () => {
    if (!customer || demoTriggered) return
    setDemoTriggered(true)
    setProcessing(true)

    const welcomeMsg: AgentMessageType = {
      id: 'demo_welcome',
      type: 'agent_message',
      agent: 'margdarshan',
      content: customer.language === 'hi'
        ? 'नमस्ते रामेश्वर जी! आपके खाते में ₹15,000 जमा हुए हैं। क्या आप ₹5,000 को 1 साल की FD में लगाना चाहेंगे? ब्याज दर 6.8% है।'
        : 'Hello Rameshwar ji! Your account has been credited with ₹15,000. Would you like to invest ₹5,000 in a 1-year Fixed Deposit at 6.8% interest?',
      language: customer.language,
      confidence: 0.94,
      timestamp: new Date(),
      action_payload: {
        action_type: 'create_fd',
        display_label: 'Create Fixed Deposit',
        amount: 5000,
        product: 'SBI Fixed Deposit',
        duration: '1 year',
        interest_rate: 6.8,
        risk_level: 'low',
      },
      requires_mpin: true,
    }

    setTimeout(() => {
      addMessage(welcomeMsg)
      setPendingAction(welcomeMsg.action_payload!)
      setAwaitingMPIN(true)
      setProcessing(false)
      setActiveAgent('margdarshan')
    }, 800)

    try {
      await api.triggerEvent(customer.id, 'idle_balance_spike', { amount: 15000 })
    } catch {}
  }, [customer, demoTriggered, addMessage, setPendingAction, setAwaitingMPIN, setProcessing, setActiveAgent])

  const handleMPINSuccess = useCallback(() => {
    const successMsg: AgentMessageType = {
      id: 'success_' + Date.now(),
      type: 'completed',
      agent: (activeAgent as any) || 'margdarshan',
      content: customer?.language === 'hi'
        ? '✅ FD सफलतापूर्वक बनाई गई! आपकी ₹5,000 की FD 1 साल के लिए 6.8% ब्याज दर पर बन गई है।'
        : '✅ Fixed Deposit created successfully! Your ₹5,000 FD for 1 year at 6.8% interest has been set up.',
      language: customer?.language || 'hi',
      confidence: 1,
      timestamp: new Date(),
    }
    addMessage(successMsg)
    appendLog({
      id: 'log_' + Date.now(),
      customer_id: customer?.id || '',
      agent: 'margdarshan',
      action: 'create_fd',
      status: 'success',
      timestamp: new Date().toISOString(),
      mpin_verified: true,
      confidence: 1,
    })
  }, [customer, activeAgent, addMessage, appendLog])

  const handleMPINCancel = useCallback(() => {
    setAwaitingMPIN(false)
    setPendingAction(null)
    setDemoTriggered(false)
  }, [setAwaitingMPIN, setPendingAction])

  const handleDecline = useCallback(() => {
    if (customer) {
      api.recordConsent(customer.id, pendingAction?.action_type || 'unknown', false)
    }
    setPendingAction(null)
    setAwaitingMPIN(false)
  }, [customer, pendingAction, setPendingAction, setAwaitingMPIN])

  return (
    <div className="flex-1 flex flex-col h-full relative">
      {/* Top status strip */}
      <div className="flex items-center justify-between px-6 py-3 border-b border-[rgba(26,58,92,0.08)] bg-white/80">
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2">
            {activeAgent && <AgentBadge agent={activeAgent as any} size="sm" />}
          </div>
          <div className="w-2 h-2 rounded-full bg-accent" />
        </div>
        <LanguageSelector />
      </div>

      {/* Demo trigger banner */}
      {!demoTriggered && (
        <motion.div
          initial={{ opacity: 0, y: -8 }}
          animate={{ opacity: 1, y: 0 }}
          className="mx-6 mt-3 p-3 rounded-lg bg-gold-light border border-gold/30 flex items-center justify-between"
        >
          <div>
            <p className="text-xs font-medium text-warning">Demo Scenario</p>
            <p className="text-[11px] text-warning/70">Click to trigger the idle balance event demo</p>
          </div>
          <motion.button
            onClick={triggerDemo}
            disabled={isProcessing}
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.97 }}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-input bg-warning text-white text-xs font-medium disabled:opacity-45"
          >
            <Zap size={14} />
            Trigger
          </motion.button>
        </motion.div>
      )}

      {/* Chat area */}
      <div className="flex-1 overflow-y-auto px-6 py-4">
        {messages.length === 0 && !isProcessing && (
          <div className="h-full flex flex-col items-center justify-center text-center">
            <div className="w-16 h-16 rounded-full bg-primary-light flex items-center justify-center mb-4">
              <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#1A3A5C" strokeWidth="1.5">
                <path d="M12 2a4 4 0 0 0-4 4v4a4 4 0 0 0 8 0V6a4 4 0 0 0-4-4Z" />
                <path d="M5 11a7 7 0 0 0 14 0" />
                <path d="M8 21h8" />
                <path d="M12 17v4" />
              </svg>
            </div>
            <p className="text-text-muted text-sm max-w-xs">
              Your AI banking companion is ready. Tap the mic to speak or click &quot;Trigger&quot; to start the demo.
            </p>
          </div>
        )}
        <motion.div variants={containerVariants} className="space-y-1">
          <AnimatePresence>
            {messages.map((msg, idx) => (
              <AgentMessage key={msg.id} message={msg} isLatest={idx === messages.length - 1} />
            ))}
          </AnimatePresence>
          {isProcessing && <AgentTypingIndicator agent={(activeAgent as any) || 'margdarshan'} />}
        </motion.div>
        <div ref={chatEndRef} />
      </div>

      {/* Input dock */}
      <div className="border-t border-[rgba(26,58,92,0.08)] bg-white px-6 py-4">
        <div className="flex items-center gap-3">
          <VoiceInput
            onTranscription={handleTranscription}
            language={customer?.language || 'hi'}
            disabled={isProcessing}
          />
          <div className="flex-1 relative">
            <input
              value={textInput}
              onChange={(e) => setTextInput(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSend(textInput)}
              placeholder="Type a message..."
              disabled={isProcessing}
              className="w-full h-11 px-4 bg-surface border border-[rgba(26,58,92,0.15)] rounded-input text-sm text-primary placeholder:text-text-hint focus:border-primary focus:ring-[3px] focus:ring-[rgba(26,58,92,0.12)] transition-all disabled:opacity-45"
            />
          </div>
          <motion.button
            onClick={() => handleSend(textInput)}
            disabled={!textInput.trim() || isProcessing}
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.97 }}
            className="h-11 w-11 rounded-input bg-accent text-white flex items-center justify-center disabled:opacity-45"
          >
            <Send size={16} />
          </motion.button>
        </div>
      </div>

      {/* Action preview panel */}
      <AnimatePresence>
        {pendingAction && !awaitingMPIN && (
          <motion.div
            initial={{ x: 320, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            exit={{ x: 320, opacity: 0 }}
            transition={{ type: 'spring', stiffness: 300, damping: 30 }}
            className="absolute top-0 right-0 h-full w-[380px] bg-white border-l border-[rgba(26,58,92,0.10)] shadow-modal z-40 overflow-y-auto"
          >
            <ActionPreview
              action={pendingAction}
              agent={(activeAgent as any) || 'margdarshan'}
              onAuthorize={() => setAwaitingMPIN(true)}
              onDecline={handleDecline}
            />
          </motion.div>
        )}
      </AnimatePresence>

      {/* MPIN verification modal */}
      <AnimatePresence>
        {awaitingMPIN && pendingAction && (
          <MPINVerification
            actionLabel={pendingAction.display_label}
            onSuccess={handleMPINSuccess}
            onCancel={handleMPINCancel}
          />
        )}
      </AnimatePresence>
    </div>
  )
}
