'use client'

import { ArrowRight, ArrowDownLeft, ArrowUpRight } from 'lucide-react'

export default function RecentTransactions() {
  const transactions = [
    {
      title: 'Salary Credit',
      amount: '+₹45,000',
      type: 'credit',
      date: 'Yesterday',
    },
    {
      title: 'Electricity Bill',
      amount: '-₹2,300',
      type: 'debit',
      date: 'Today',
    },
    {
      title: 'UPI Transfer',
      amount: '-₹500',
      type: 'debit',
      date: 'Today',
    },
    {
      title: 'ATM Withdrawal',
      amount: '-₹5,000',
      type: 'debit',
      date: '2 days ago',
    },
  ]

  return (
    <div className="bg-white rounded-2xl shadow-sm border p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-lg font-semibold text-slate-800">
          Recent Transactions
        </h2>

        <button className="text-blue-600 hover:text-blue-700 text-sm font-medium flex items-center gap-1">
          View All
          <ArrowRight size={16} />
        </button>
      </div>

      {/* Transactions */}
      <div className="space-y-4">
        {transactions.map((transaction, index) => (
          <div
            key={index}
            className="flex items-center justify-between p-4 rounded-xl hover:bg-slate-50 transition"
          >
            <div className="flex items-center gap-4">
              <div
                className={`p-3 rounded-full ${
                  transaction.type === 'credit'
                    ? 'bg-green-100'
                    : 'bg-red-100'
                }`}
              >
                {transaction.type === 'credit' ? (
                  <ArrowDownLeft
                    size={18}
                    className="text-green-600"
                  />
                ) : (
                  <ArrowUpRight
                    size={18}
                    className="text-red-600"
                  />
                )}
              </div>

              <div>
                <p className="font-medium text-slate-800">
                  {transaction.title}
                </p>

                <p className="text-sm text-gray-500">
                  {transaction.date}
                </p>
              </div>
            </div>

            <span
              className={`font-semibold ${
                transaction.type === 'credit'
                  ? 'text-green-600'
                  : 'text-red-600'
              }`}
            >
              {transaction.amount}
            </span>
          </div>
        ))}
      </div>
    </div>
  )
}