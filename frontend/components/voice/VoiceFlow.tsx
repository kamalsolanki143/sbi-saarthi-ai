'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'

import VoiceIdle from './VoiceIdle'
import VoiceListening from './VoiceListening'
import VoiceTranscript from './VoiceTranscript'
import VoiceUnderstanding from './VoiceUnderstanding'

type VoiceStep =
  | 'idle'
  | 'listening'
  | 'transcript'
  | 'understanding'

export default function VoiceFlow() {
  const router = useRouter()

  const [step, setStep] = useState<VoiceStep>('idle')

  const [transcript, setTranscript] = useState(
    'I want to create an FD of ₹5000'
  )

  const handleStartListening = () => {
    setStep('listening')
  }

  const handleStopListening = () => {
    setTranscript('I want to create an FD of ₹5000')
    setStep('transcript')
  }

  const handleRetry = () => {
    setStep('listening')
  }

  const handleContinueToUnderstanding = () => {
    setStep('understanding')
  }

  const handleModify = () => {
    setStep('transcript')
  }

  const handleFinalContinue = () => {
    router.push('/consent')
  }

  return (
    <div className="w-full">
      {step === 'idle' && (
        <VoiceIdle onStart={handleStartListening} />
      )}

      {step === 'listening' && (
        <VoiceListening onStop={handleStopListening} />
      )}

      {step === 'transcript' && (
        <VoiceTranscript
          transcript={transcript}
          onRetry={handleRetry}
          onContinue={handleContinueToUnderstanding}
        />
      )}

      {step === 'understanding' && (
        <VoiceUnderstanding
          onModify={handleModify}
          onContinue={handleFinalContinue}
        />
      )}
    </div>
  )
}