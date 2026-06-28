'use client'

interface Props {
  onModify: () => void
  onContinue: () => void
}

export default function VoiceUnderstanding({
  onModify,
  onContinue,
}: Props) {
  return (
    <div className="bg-white rounded-3xl p-8 shadow-lg">

      <h2 className="text-xl font-bold">
        SAARTHI understood:
      </h2>

      <div className="mt-5 space-y-4">

        <div>
          <p className="text-sm text-slate-500">
            Action
          </p>

          <p className="font-semibold">
            Create FD
          </p>
        </div>

        <div>
          <p className="text-sm text-slate-500">
            Amount
          </p>

          <p className="font-semibold">
            ₹5000
          </p>
        </div>

        <div>
          <p className="text-sm text-slate-500">
            Tenure
          </p>

          <p className="font-semibold">
            1 Year
          </p>
        </div>

      </div>

      <div className="flex gap-3 mt-6">

        <button
          onClick={onModify}
          className="flex-1 border rounded-xl py-3"
        >
          Modify
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