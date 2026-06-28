'use client'

import {
  ShieldCheck,
  Smartphone,
  Lock,
  ScanFace,
  AlertCircle,
} from 'lucide-react'

export default function SecurityCenter() {
  const securityItems = [
    {
      title: 'Device Verified',
      icon: Smartphone,
      color: 'text-green-600',
      bg: 'bg-green-100',
    },
    {
      title: 'MPIN Enabled',
      icon: Lock,
      color: 'text-green-600',
      bg: 'bg-green-100',
    },
    {
      title: 'Face Authentication Active',
      icon: ScanFace,
      color: 'text-green-600',
      bg: 'bg-green-100',
    },
  ]

  return (
    <div className="bg-white rounded-2xl shadow-sm border p-6">
      {/* Header */}
      <div className="flex items-center gap-3 mb-6">
        <div className="p-3 bg-blue-100 rounded-xl">
          <ShieldCheck
            className="text-blue-600"
            size={24}
          />
        </div>

        <div>
          <h2 className="text-lg font-semibold text-slate-800">
            Security Center
          </h2>

          <p className="text-sm text-gray-500">
            Your account security status
          </p>
        </div>
      </div>

      {/* Security Features */}
      <div className="space-y-4">
        {securityItems.map((item, index) => {
          const Icon = item.icon

          return (
            <div
              key={index}
              className="flex items-center gap-4 p-4 rounded-xl bg-slate-50"
            >
              <div
                className={`p-2 rounded-lg ${item.bg}`}
              >
                <Icon
                  size={20}
                  className={item.color}
                />
              </div>

              <span className="font-medium text-slate-700">
                ✔ {item.title}
              </span>
            </div>
          )
        })}
      </div>

      {/* Suspicious Activity */}
      <div className="mt-6 p-4 rounded-xl bg-green-50 border border-green-200">
        <div className="flex items-start gap-3">
          <AlertCircle
            className="text-green-600 mt-1"
            size={20}
          />

          <div>
            <h3 className="font-semibold text-slate-800">
              Last Suspicious Activity
            </h3>

            <p className="text-sm text-gray-600 mt-1">
              None detected.
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}