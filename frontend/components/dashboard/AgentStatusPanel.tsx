'use client'

interface AgentStatusPanelProps {
  confidence?: number
}

export default function AgentStatusPanel({
  confidence = 94,
}: AgentStatusPanelProps) {
  return (
    <div className="bg-white rounded-2xl shadow-sm border p-6">

      {/* SIMPLE HEADER */}
      <h2 className="text-lg font-semibold text-slate-800 mb-4">
        AI Agent Status
      </h2>

      {/* ONLY STATUS (NO FULL ARCHITECTURE) */}
      <div className="space-y-2 text-sm text-slate-600">

        <div className="flex justify-between">
          <span>MITRA</span>
          <span className="text-green-600">Active</span>
        </div>

        <div className="flex justify-between">
          <span>MARGDARSHAN</span>
          <span className="text-green-600">Active</span>
        </div>

        <div className="flex justify-between">
          <span>SAATHI</span>
          <span className="text-green-600">Active</span>
        </div>

      </div>

      {/* TRUST SCORE */}
      <div className="mt-6">
        <div className="flex justify-between text-sm mb-2">
          <span>Trust Score</span>
          <span className="font-semibold text-green-600">
            {confidence}%
          </span>
        </div>

        <div className="w-full bg-gray-200 rounded-full h-2">
          <div
            className="bg-green-500 h-2 rounded-full"
            style={{ width: `${confidence}%` }}
          />
        </div>
      </div>

    </div>
  )
}