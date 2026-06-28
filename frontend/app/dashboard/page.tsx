'use client'

import { useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import { useRouter } from 'next/navigation'

import Sidebar from '@/components/shared/Sidebar'
import TopBar from '@/components/shared/TopBar'
import CustomerCard from '@/components/CustomerCard/CustomerCard'
import AgentBadge from '@/components/shared/AgentBadge'

import DashboardHeader from '@/components/dashboard/DashboardHeader'
import FinancialOverview from '@/components/dashboard/FinancialOverview'
import AgentStatusPanel from '@/components/dashboard/AgentStatusPanel'

import VoiceFlow from '@/components/voice/VoiceFlow'
import AIRecommendations from '@/components/dashboard/AIRecommendations'
import RecentTransactions from '@/components/dashboard/RecentTransactions'
import SpendingInsights from '@/components/dashboard/SpendingInsights'
import GovernmentSchemes from '@/components/dashboard/GovernmentSchemes'

import UpcomingTasks from '@/components/dashboard/UpcomingTasks'
import SmartAlerts from '@/components/dashboard/SmartAlerts'
import SecurityCenter from '@/components/dashboard/SecurityCenter'
import ProfileCompletion from '@/components/dashboard/ProfileCompletion'

import { useCustomerStore } from '@/store/useCustomerStore'
import { useAgentStore } from '@/store/useAgentStore'

import { api } from '@/services/api'
import { MOCK_RECOMMENDATIONS } from '@/services/mockData'
import { useT } from '@/services/translations'
import { AgentName } from '@/types/agent'

export default function Dashboard() {
  const customer = useCustomerStore((s) => s.customer)
  const { activeAgent, confidence, reason } = useAgentStore()

  const router = useRouter()
  const _t = useT()

  const [recs, setRecs] = useState<any[]>([])

  useEffect(() => {
    if (!customer) return

    api
      .getRecommendations(customer.id)
      .then((res) => {
        if (res.data.length > 0) {
          setRecs(res.data)
        } else {
          setRecs(MOCK_RECOMMENDATIONS)
        }
      })
      .catch(() => {
        setRecs(MOCK_RECOMMENDATIONS)
      })
  }, [customer])

  if (!customer) {
    return (
      <div className="flex items-center justify-center h-screen">
        Loading Saarthi...
      </div>
    )
  }

  return (
    <div className="flex min-h-screen bg-white">

      {/* SIDEBAR (ONLY HERE NOW) */}
      <Sidebar />

      {/* MAIN CONTENT */}
      <div className="ml-[248px] flex-1 flex flex-col">

        <TopBar title={_t('Dashboard')} />

        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="p-6 bg-slate-50 min-h-screen"
        >

          <DashboardHeader
            greeting={`Good Afternoon, ${customer.name || 'Ramesh'} 👋`}
            subtitle="Salary of ₹45,000 credited yesterday. You are eligible for a Fixed Deposit recommendation."
            lastLogin="Today, 3:45 PM"
          />

          <div className="mt-6">
            <CustomerCard />
          </div>

          <div className="mt-6">
            <FinancialOverview />
          </div>

          <div className="grid grid-cols-1 xl:grid-cols-10 gap-6 mt-6">

            {/* LEFT */}
            <div className="xl:col-span-7 space-y-6">

              <VoiceFlow />
              <AIRecommendations />
              <RecentTransactions />
              <SpendingInsights />
              <GovernmentSchemes />

              <div className="bg-white rounded-xl shadow-sm p-6">
                <h3 className="text-lg font-semibold mb-4">
                  Personalized Recommendations
                </h3>

                <div className="grid md:grid-cols-2 gap-4">
                  {recs.map((rec, idx) => (
                    <div key={rec.id || idx} className="border rounded-lg p-4">
                      <AgentBadge agent={rec.agent as AgentName} size="sm" />

                      <p className="mt-3">{rec.text}</p>

                      <button
                        onClick={() => router.push('/voice-banking')}
                        className="mt-4 text-blue-600 font-medium"
                      >
                        Ask Saarthi →
                      </button>
                    </div>
                  ))}
                </div>
              </div>

            </div>

            {/* RIGHT */}
            <div className="xl:col-span-3 space-y-6">

              <AgentStatusPanel
                activeAgent={activeAgent}
                confidence={confidence}
                reason={reason}
              />

              <UpcomingTasks />
              <SmartAlerts />
              <SecurityCenter />
              <ProfileCompletion />

              <div className="bg-white rounded-xl shadow-sm p-6">
                <h3 className="text-lg font-semibold mb-4">
                  Recent Agent Activity
                </h3>

                <div className="space-y-3">
                  {[
                    {
                      agent: 'margdarshan' as AgentName,
                      action: 'Idle balance detected — FD recommendation generated',
                      time: '2 min ago',
                      status: 'pending',
                    },
                    {
                      agent: 'saathi' as AgentName,
                      action: 'Spending pattern analyzed — no unusual activity',
                      time: '1 day ago',
                      status: 'success',
                    },
                    {
                      agent: 'mitra' as AgentName,
                      action: 'KYC document verification completed',
                      time: '3 days ago',
                      status: 'success',
                    },
                  ].map((a, i) => (
                    <div key={i} className="flex justify-between border p-3 rounded-lg">
                      <AgentBadge agent={a.agent} size="sm" />
                      <span className="text-sm">{a.action}</span>
                    </div>
                  ))}
                </div>
              </div>

            </div>

          </div>
        </motion.div>

      </div>
    </div>
  )
}