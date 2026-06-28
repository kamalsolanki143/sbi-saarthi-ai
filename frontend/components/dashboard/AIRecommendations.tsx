'use client'

import { useRouter } from 'next/navigation'
import {
  PiggyBank,
  ArrowRight,
  MessageCircle,
} from 'lucide-react'

export default function AIRecommendations() {
  const router = useRouter()

  const recommendations = [
    {
      title: 'Fixed Deposit Recommendation',
      amount: '₹5,000',
      interest: '6.8%',
      returns: '₹5,340',
      description:
        'Idle balance detected. Invest safely and earn higher returns.',
    },
    {
      title: 'Recurring Deposit Plan',
      amount: '₹2,000/month',
      interest: '6.5%',
      returns: '₹25,800',
      description:
        'Build disciplined savings through monthly deposits.',
    },
  ]

  return (
    <div className="bg-white rounded-2xl shadow-sm border p-6">
      <div className="flex items-center gap-3 mb-6">
        <PiggyBank className="text-blue-600" size={24} />

        <h2 className="text-lg font-semibold text-slate-800">
          AI Recommendations
        </h2>
      </div>

      <div className="grid md:grid-cols-2 gap-6">
        {recommendations.map((rec, index) => (
          <div
            key={index}
            className="border rounded-2xl p-5 hover:shadow-md transition-all bg-slate-50"
          >
            <h3 className="text-lg font-semibold text-slate-800">
              {rec.title}
            </h3>

            <p className="text-gray-600 text-sm mt-2">
              {rec.description}
            </p>

            <div className="mt-5 space-y-3">
              <div className="flex justify-between">
                <span className="text-gray-500">
                  Invest Amount
                </span>
                <span className="font-semibold">
                  {rec.amount}
                </span>
              </div>

              <div className="flex justify-between">
                <span className="text-gray-500">
                  Interest Rate
                </span>
                <span className="font-semibold text-green-600">
                  {rec.interest}
                </span>
              </div>

              <div className="flex justify-between">
                <span className="text-gray-500">
                  Expected Returns
                </span>
                <span className="font-semibold text-blue-600">
                  {rec.returns}
                </span>
              </div>
            </div>

            <div className="flex gap-3 mt-6">
              <button
                className="flex-1 bg-blue-600 hover:bg-blue-700 text-white py-2.5 rounded-xl font-medium transition"
              >
                Create FD
              </button>

              <button
                onClick={() => router.push('/voice-banking')}
                className="flex items-center justify-center gap-2 border border-slate-300 hover:bg-slate-100 px-4 py-2.5 rounded-xl transition"
              >
                <MessageCircle size={18} />
                Ask Saarthi
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}