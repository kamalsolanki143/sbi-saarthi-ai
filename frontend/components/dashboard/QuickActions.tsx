'use client'

import { useRouter } from "next/navigation"
import { QUICK_ACTIONS, ActionType } from "@/lib/quickActions"

export default function QuickActions() {
  const router = useRouter()

  const handleAction = (type: ActionType) => {
    const action = QUICK_ACTIONS[type]

    // 🔐 Store selected action for next screens
    localStorage.setItem("activeAction", JSON.stringify(action))

    // 🔵 NO CONSENT FLOW (instant execution)
    if (!action.requiresConsent) {
      router.push("/success")
      return
    }

    // 🔴 CONSENT FLOW (secure path)
    router.push("/action-preview")
  }

  const actions = Object.values(QUICK_ACTIONS)

  return (
    <div className="bg-white rounded-2xl p-5 border border-slate-200 shadow-sm">
      <h3 className="font-semibold mb-4">
        Quick Actions
      </h3>

      <div className="grid grid-cols-3 gap-3">
        {actions.map((action) => (
          <button
            key={action.type}
            onClick={() => handleAction(action.type)}
            className="bg-slate-100 rounded-xl p-4 hover:bg-slate-200 transition text-left active:scale-[0.98]"
          >
            <h4 className="font-semibold text-sm">
              {action.title}
            </h4>

            <p className="text-xs text-slate-500 mt-1">
              {action.description}
            </p>
          </button>
        ))}
      </div>
    </div>
  )
}