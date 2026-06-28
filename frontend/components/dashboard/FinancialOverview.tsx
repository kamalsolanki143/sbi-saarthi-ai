'use client'

import {
  Wallet,
  PiggyBank,
  ShieldCheck,
  Gift,
  TrendingUp,
} from 'lucide-react'

export default function FinancialOverview() {
  const cards = [
    {
      title: 'Available Balance',
      value: '₹56,700',
      subtitle: '↑ 12% from last month',
      icon: Wallet,
      bg: 'bg-blue-50',
      iconBg: 'bg-blue-100',
      iconColor: 'text-blue-600',
    },
    {
      title: 'Savings Goal',
      value: '68%',
      subtitle: '₹34,000 of ₹50,000 achieved',
      icon: PiggyBank,
      bg: 'bg-green-50',
      iconBg: 'bg-green-100',
      iconColor: 'text-green-600',
      progress: 68,
    },
    {
      title: 'Credit Score',
      value: '742',
      subtitle: 'AI Estimated • Excellent',
      icon: ShieldCheck,
      bg: 'bg-purple-50',
      iconBg: 'bg-purple-100',
      iconColor: 'text-purple-600',
    },
    {
      title: 'Rewards Points',
      value: '2,450',
      subtitle: '350 points earned this month',
      icon: Gift,
      bg: 'bg-orange-50',
      iconBg: 'bg-orange-100',
      iconColor: 'text-orange-600',
    },
  ]

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-6">
      {cards.map((card, index) => {
        const Icon = card.icon

        return (
          <div
            key={index}
            className={`${card.bg} rounded-2xl p-6 shadow-sm border hover:shadow-md transition-all duration-300`}
          >
            <div className="flex justify-between items-start">
              <div>
                <p className="text-sm text-gray-500 font-medium">
                  {card.title}
                </p>

                <h3 className="text-3xl font-bold mt-3 text-gray-900">
                  {card.value}
                </h3>

                <p className="mt-2 text-sm text-green-600 flex items-center gap-1">
                  <TrendingUp size={14} />
                  {card.subtitle}
                </p>
              </div>

              <div
                className={`${card.iconBg} p-3 rounded-xl`}
              >
                <Icon
                  className={card.iconColor}
                  size={24}
                />
              </div>
            </div>

            {card.progress && (
              <div className="mt-5">
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-green-600 h-2 rounded-full"
                    style={{
                      width: `${card.progress}%`,
                    }}
                  />
                </div>

                <p className="text-xs text-gray-500 mt-2">
                  Goal Progress
                </p>
              </div>
            )}
          </div>
        )
      })}
    </div>
  )
}