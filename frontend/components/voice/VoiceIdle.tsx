'use client'

import { Mic } from 'lucide-react'

interface Props {
  onStart: () => void
}

export default function VoiceIdle({ onStart }: Props) {
  return (
    <div className="bg-gradient-to-br from-blue-600 to-cyan-500 rounded-3xl p-8 text-white text-center">

      <div className="w-24 h-24 mx-auto rounded-full bg-white/20 flex items-center justify-center">
        <Mic size={40} />
      </div>

      <h2 className="text-2xl font-bold mt-4">
        Voice Banking
      </h2>

      <p className="text-white/80 mt-2">
        Tap & speak your request
      </p>

      <button
        onClick={onStart}
        className="mt-6 px-6 py-3 bg-white text-blue-600 rounded-xl font-semibold"
      >
        Start Listening
      </button>

    </div>
  )
}