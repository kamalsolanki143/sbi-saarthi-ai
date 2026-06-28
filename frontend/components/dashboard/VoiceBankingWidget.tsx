'use client'

import { Mic } from 'lucide-react'
import { motion } from 'framer-motion'

export default function VoiceBankingWidget() {
  return (
    <div className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-slate-900 via-blue-900 to-cyan-900 p-8 text-white">

      {/* Glow */}
      <div className="absolute inset-0 bg-cyan-500/10 blur-3xl" />

      <div className="relative z-10 flex flex-col items-center">

        <motion.div
          animate={{
            scale: [1, 1.08, 1]
          }}
          transition={{
            repeat: Infinity,
            duration: 2
          }}
          className="w-28 h-28 rounded-full bg-cyan-500/20 border border-cyan-400 flex items-center justify-center"
        >
          <Mic size={44} />
        </motion.div>

        <h2 className="mt-5 text-2xl font-bold">
          Voice Banking
        </h2>

        <span className="mt-2 px-3 py-1 rounded-full bg-cyan-500/20 text-sm">
          Hindi & English
        </span>

        <p className="mt-3 text-slate-300">
          Tap and speak your request
        </p>

        <button className="mt-6 px-6 py-3 rounded-xl bg-cyan-500 hover:bg-cyan-400 transition">
          Start Listening
        </button>

      </div>
    </div>
  )
}