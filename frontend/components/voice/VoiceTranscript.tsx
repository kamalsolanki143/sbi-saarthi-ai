'use client'

interface Props {
  transcript: string
  onRetry: () => void
  onContinue: () => void
}

export default function VoiceTranscript({
  transcript,
  onRetry,
  onContinue,
}: Props) {
  return (
    <div className="bg-white rounded-3xl p-8 shadow-lg">

      <h2 className="text-xl font-bold mb-4">
        Recognized Speech
      </h2>

      <div className="bg-slate-100 p-4 rounded-xl">
        "{transcript}"
      </div>

      <div className="flex gap-3 mt-6">

        <button
          onClick={onRetry}
          className="flex-1 border rounded-xl py-3"
        >
          Retry
        </button>

        <button
          onClick={onContinue}
          className="flex-1 bg-blue-600 text-white rounded-xl py-3"
        >
          Continue
        </button>

      </div>

    </div>
  )
}