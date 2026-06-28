'use client'

import { ArrowRight, CheckSquare } from 'lucide-react'

export default function UpcomingTasks() {
  const tasks = [
    'Complete Nominee Details',
    'Activate YONO',
    'Review FD Recommendation',
    'Update Aadhaar',
  ]

  return (
    <div className="bg-white rounded-2xl shadow-sm border p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-lg font-semibold text-slate-800">
          Upcoming Tasks
        </h2>

        <button className="text-blue-600 hover:text-blue-700 text-sm font-medium flex items-center gap-1">
          View All
          <ArrowRight size={16} />
        </button>
      </div>

      {/* Tasks List */}
      <div className="space-y-4">
        {tasks.map((task, index) => (
          <div
            key={index}
            className="flex items-center gap-3 p-4 rounded-xl hover:bg-slate-50 transition"
          >
            <CheckSquare
              size={20}
              className="text-blue-600"
            />

            <span className="text-slate-700">
              {task}
            </span>
          </div>
        ))}
      </div>
    </div>
  )
}