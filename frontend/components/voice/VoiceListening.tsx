'use client'

import { Mic } from 'lucide-react'
import { motion } from 'framer-motion'

interface Props {
  onStop: () => void
}

export default function VoiceListening({ onStop }: Props) {
  return (
    <div className="bg-gradient-to-br from-slate-900 to-cyan-900 rounded-3xl p-8 text-white text-center">

      <motion.div
        animate={{
          scale: [1, 1.2, 1]
        }}
        transition={{
          repeat: Infinity,
          duration: 1.5
        }}
        className="w-28 h-28 mx-auto rounded-full bg-cyan-500/20 border border-cyan-400 flex items-center justify-center"
      >
        <Mic size={48} />
      </motion.div>

      <h2 className="text-2xl font-bold mt-5">
        🎤 Listening...
      </h2>

      <p className="text-slate-300 mt-2">
        Please speak now
      </p>

      <button
        onClick={onStop}
        className="mt-6 px-6 py-3 bg-red-500 rounded-xl"
      >
        Stop
      </button>

    </div>
  )
}