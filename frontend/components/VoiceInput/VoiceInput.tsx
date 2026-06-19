'use client'
import { useState, useRef, useCallback } from 'react'
import { Mic, Square } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'
import { api } from '@/services/api'
import { Language } from '@/types/agent'
import WaveformVisualizer from './WaveformVisualizer'

interface Props {
  onTranscription: (text: string) => void
  language: Language
  disabled?: boolean
}

export default function VoiceInput({ onTranscription, language, disabled }: Props) {
  const [isRecording, setIsRecording] = useState(false)
  const [duration, setDuration] = useState(0)
  const [transcribing, setTranscribing] = useState(false)
  const [transcriptPreview, setTranscriptPreview] = useState('')
  const mediaRecorderRef = useRef<MediaRecorder | null>(null)
  const analyserRef = useRef<AnalyserNode | null>(null)
  const audioCtxRef = useRef<AudioContext | null>(null)
  const chunksRef = useRef<Blob[]>([])
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null)

  const startRecording = useCallback(async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      const mediaRecorder = new MediaRecorder(stream)
      mediaRecorderRef.current = mediaRecorder

      const audioCtx = new AudioContext()
      audioCtxRef.current = audioCtx
      const source = audioCtx.createMediaStreamSource(stream)
      const analyser = audioCtx.createAnalyser()
      analyser.fftSize = 64
      source.connect(analyser)
      analyserRef.current = analyser

      chunksRef.current = []
      mediaRecorder.ondataavailable = (e) => {
        if (e.data.size > 0) chunksRef.current.push(e.data)
      }

      mediaRecorder.onstop = async () => {
        setTranscribing(true)
        stream.getTracks().forEach((t) => t.stop())
        audioCtx.close()

        const blob = new Blob(chunksRef.current, { type: 'audio/webm' })
        const reader = new FileReader()
        reader.onloadend = async () => {
          const base64 = (reader.result as string).split(',')[1]
          try {
            const res = await api.transcribeAudio(base64, language)
            const text = res.data.text
            setTranscriptPreview(text)
            setTimeout(() => {
              onTranscription(text)
              setTranscriptPreview('')
            }, 1500)
          } catch {
            setTranscriptPreview('')
          } finally {
            setTranscribing(false)
          }
        }
        reader.readAsDataURL(blob)
        setDuration(0)
      }

      mediaRecorder.start()
      setIsRecording(true)
      const startTime = Date.now()
      timerRef.current = setInterval(() => {
        setDuration(Math.floor((Date.now() - startTime) / 1000))
      }, 200)
    } catch {
      // mic permission denied
    }
  }, [language, onTranscription])

  const stopRecording = useCallback(() => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop()
      setIsRecording(false)
      if (timerRef.current) clearInterval(timerRef.current)
    }
  }, [isRecording])

  return (
    <div className="flex items-center gap-3">
      <AnimatePresence>
        {transcriptPreview && (
          <motion.div
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 8 }}
            className="absolute bottom-full mb-2 left-0 right-0 bg-white rounded-card shadow-card border border-[rgba(26,58,92,0.10)] p-3 text-sm"
          >
            {transcriptPreview}
          </motion.div>
        )}
      </AnimatePresence>

      <div className="relative">
        {isRecording && (
          <>
            <div className="absolute -inset-3 rounded-full border-2 border-accent/30 animate-sonar-1" />
            <div className="absolute -inset-3 rounded-full border-2 border-accent/20 animate-sonar-2" />
          </>
        )}
        <motion.button
          onClick={isRecording ? stopRecording : startRecording}
          disabled={disabled || transcribing}
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          className={`relative w-12 h-12 rounded-full flex items-center justify-center transition-colors ${
            isRecording
              ? 'bg-danger text-white'
              : 'bg-white border-2 border-accent text-accent hover:bg-accent-light'
          } disabled:opacity-45`}
        >
          {isRecording ? <Square size={16} /> : <Mic size={20} />}
        </motion.button>
      </div>

      {isRecording && (
        <div className="flex items-center gap-2">
          <WaveformVisualizer analyserNode={analyserRef.current} isRecording={isRecording} />
          <span className="text-xs font-mono text-text-muted w-10">
            {String(Math.floor(duration / 60)).padStart(2, '0')}:{String(duration % 60).padStart(2, '0')}
          </span>
        </div>
      )}

      {transcribing && (
        <div className="flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-accent animate-pulse" />
          <span className="text-xs text-text-muted">Transcribing...</span>
        </div>
      )}
    </div>
  )
}
