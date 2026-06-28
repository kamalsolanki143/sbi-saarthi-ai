'use client'

import { Sun, CloudSun, Clock } from 'lucide-react'

interface DashboardHeaderProps {
  greeting?: string
  subtitle?: string
  lastLogin?: string
}

export default function DashboardHeader({
  greeting = 'Good Afternoon, Ramesh 👋',
  subtitle = 'Salary credited yesterday. You are eligible for new savings options.',
  lastLogin = 'Today, 3:45 PM',
}: DashboardHeaderProps) {
  return (
    <div className="bg-gradient-to-r from-blue-600 via-indigo-600 to-purple-600 rounded-2xl p-8 text-white shadow-lg">
      <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-6">
        {/* Left Section */}
        <div className="flex-1">
          <h1 className="text-3xl font-bold">
            {greeting}
          </h1>

          <p className="mt-3 text-blue-100 text-lg max-w-2xl">
            {subtitle}
          </p>

          <div className="flex items-center gap-2 mt-6 text-sm text-blue-100">
            <Clock size={16} />
            <span>Last login: {lastLogin}</span>
          </div>
        </div>

        {/* Right Section */}
        <div className="bg-white/10 backdrop-blur-md rounded-xl p-5 min-w-[220px]">
          <div className="flex items-center gap-3 mb-3">
            <CloudSun size={28} />
            <div>
              <p className="font-semibold">Meerut</p>
              <p className="text-sm text-blue-100">
                Partly Cloudy
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <Sun size={18} />
            <span className="text-2xl font-bold">34°C</span>
          </div>

          <p className="text-sm text-blue-100 mt-2">
            Perfect day to plan your savings ☀️
          </p>
        </div>
      </div>
    </div>
  )
}