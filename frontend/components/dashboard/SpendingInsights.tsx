'use client'

import { TrendingDown, PieChart } from 'lucide-react'

export default function SpendingInsights() {
  const spendingData = [
    {
      category: 'Food',
      amount: '₹4,200',
    },
    {
      category: 'Bills',
      amount: '₹2,300',
    },
    {
      category: 'Travel',
      amount: '₹1,500',
    },
  ]

  return (
    <div className="bg-white rounded-2xl shadow-sm border p-6">
      {/* Header */}
      <div className="flex items-center gap-3 mb-6">
        <div className="p-3 bg-blue-100 rounded-xl">
          <PieChart className="text-blue-600" size={22} />
        </div>

        <div>
          <h2 className="text-lg font-semibold text-slate-800">
            Spending Insights
          </h2>

          <p className="text-sm text-gray-500">
            This Month
          </p>
        </div>
      </div>

      {/* Spending Categories */}
      <div className="space-y-4">
        {spendingData.map((item, index) => (
          <div
            key={index}
            className="flex justify-between items-center p-3 rounded-xl bg-slate-50"
          >
            <span className="text-slate-700">
              {item.category}
            </span>

            <span className="font-semibold text-slate-900">
              {item.amount}
            </span>
          </div>
        ))}
      </div>

      {/* Savings Rate */}
      <div className="mt-6 p-4 rounded-xl bg-green-50 border border-green-100">
        <div className="flex justify-between items-center">
          <span className="font-medium text-slate-700">
            Savings Rate
          </span>

          <span className="font-bold text-green-600">
            28%
          </span>
        </div>

        <div className="w-full bg-green-200 rounded-full h-2 mt-3">
          <div
            className="bg-green-600 h-2 rounded-full"
            style={{ width: '28%' }}
          />
        </div>
      </div>

      {/* AI Insight */}
      <div className="mt-6 p-4 rounded-xl bg-blue-50 border border-blue-100">
        <div className="flex items-start gap-3">
          <TrendingDown
            className="text-blue-600 mt-1"
            size={20}
          />

          <div>
            <h3 className="font-semibold text-slate-800">
              AI Insight
            </h3>

            <p className="text-sm text-gray-600 mt-1">
              "Your spending reduced by 12% this month."
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}