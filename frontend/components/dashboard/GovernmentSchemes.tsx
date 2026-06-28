'use client'

import { useRouter } from 'next/navigation'
import { Shield, ArrowRight } from 'lucide-react'

export default function GovernmentSchemes() {
  const router = useRouter()

  const schemes = [
    'PMJJBY',
    'Atal Pension Yojana',
    'PM Suraksha Bima',
  ]

  return (
    <div className="bg-white rounded-2xl shadow-sm border p-6">
      {/* Header */}
      <div className="flex items-center gap-3 mb-6">
        <div className="p-3 bg-green-100 rounded-xl">
          <Shield className="text-green-600" size={22} />
        </div>

        <div>
          <h2 className="text-lg font-semibold text-slate-800">
            Eligible Schemes
          </h2>

          <p className="text-sm text-gray-500">
            Government benefits available for you
          </p>
        </div>
      </div>

      {/* Schemes List */}
      <div className="space-y-4">
        {schemes.map((scheme, index) => (
          <div
            key={index}
            className="flex items-center gap-3 p-4 rounded-xl bg-green-50 border border-green-100"
          >
            <div className="w-7 h-7 rounded-full bg-green-600 flex items-center justify-center text-white text-sm font-bold">
              ✓
            </div>

            <span className="font-medium text-slate-700">
              {scheme}
            </span>
          </div>
        ))}
      </div>

      {/* CTA Button */}
      <button
        onClick={() => router.push('/voice-banking')}
        className="w-full mt-6 bg-green-600 hover:bg-green-700 text-white py-3 rounded-xl font-medium transition flex items-center justify-center gap-2"
      >
        Check Eligibility
        <ArrowRight size={18} />
      </button>
    </div>
  )
}