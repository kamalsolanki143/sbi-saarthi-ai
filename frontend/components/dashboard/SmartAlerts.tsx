'use client'

import {
  AlertTriangle,
  Target,
  Lightbulb,
} from 'lucide-react'

export default function SmartAlerts() {
  const alerts = [
    {
      icon: AlertTriangle,
      title: 'Minimum Balance Alert',
      message:
        'Minimum balance may fall below threshold.',
      bg: 'bg-red-50',
      iconColor: 'text-red-600',
    },
    {
      icon: Target,
      title: 'Government Scheme Eligibility',
      message:
        'You are eligible for PMJJBY Scheme.',
      bg: 'bg-green-50',
      iconColor: 'text-green-600',
    },
    {
      icon: Lightbulb,
      title: 'Idle Balance Detected',
      message:
        'Create FD to earn ₹340 extra per year.',
      bg: 'bg-yellow-50',
      iconColor: 'text-yellow-600',
    },
  ]

  return (
    <div className="bg-white rounded-2xl shadow-sm border p-6">
      {/* Header */}
      <h2 className="text-lg font-semibold text-slate-800 mb-5">
        Smart Alerts
      </h2>

      {/* Alerts List */}
      <div className="space-y-4">
        {alerts.map((alert, index) => {
          const Icon = alert.icon

          return (
            <div
              key={index}
              className={`${alert.bg} rounded-xl p-4 border border-slate-100`}
            >
              <div className="flex items-start gap-3">
                <div className="mt-1">
                  <Icon
                    size={22}
                    className={alert.iconColor}
                  />
                </div>

                <div>
                  <h3 className="font-medium text-slate-800">
                    {alert.title}
                  </h3>

                  <p className="text-sm text-gray-600 mt-1">
                    {alert.message}
                  </p>
                </div>
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}