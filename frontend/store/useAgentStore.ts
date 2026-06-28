import { create } from "zustand"
import { AgentMessage, ActionPayload } from '@/types/agent'

type AgentType = "MITRA" | "SAATHI" | "MARGDARSHAN"

type AgentState = {
  // 🧠 UI State (for dashboard panel)
  activeAgent: AgentType
  confidence: number
  reason: string

  // 💬 Existing system state
  messages: AgentMessage[]
  pendingAction: ActionPayload | null
  awaitingMPIN: boolean
  isProcessing: boolean

  // 🔄 Actions
  setAgent: (data: Partial<AgentState>) => void
  addMessage: (msg: AgentMessage) => void
  setPendingAction: (action: ActionPayload | null) => void
  setAwaitingMPIN: (val: boolean) => void
  setProcessing: (val: boolean) => void
  clearMessages: () => void
}

export const useAgentStore = create<AgentState>((set) => ({
  // 🧠 Dashboard default state
  activeAgent: "MARGDARSHAN",
  confidence: 94,
  reason: "Idle balance detected + salary credit event → FD recommendation triggered",

  // 💬 existing state
  messages: [],
  pendingAction: null,
  awaitingMPIN: false,
  isProcessing: false,

  // 🔄 unified updater (IMPORTANT for dashboard panel)
  setAgent: (data) =>
    set((state) => ({
      ...state,
      ...data,
    })),

  addMessage: (msg) =>
    set((s) => ({ messages: [...s.messages, msg] })),

  setPendingAction: (action) =>
    set({ pendingAction: action }),

  setAwaitingMPIN: (val) =>
    set({ awaitingMPIN: val }),

  setProcessing: (val) =>
    set({ isProcessing: val }),

  clearMessages: () =>
    set({ messages: [] }),
}))