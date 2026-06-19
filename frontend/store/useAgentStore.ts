import { create } from 'zustand'
import { AgentMessage, ActionPayload } from '@/types/agent'

interface AgentStore {
  messages: AgentMessage[]
  pendingAction: ActionPayload | null
  awaitingMPIN: boolean
  activeAgent: string
  isProcessing: boolean
  addMessage: (msg: AgentMessage) => void
  setPendingAction: (action: ActionPayload | null) => void
  setAwaitingMPIN: (val: boolean) => void
  setActiveAgent: (agent: string) => void
  setProcessing: (val: boolean) => void
  clearMessages: () => void
}

export const useAgentStore = create<AgentStore>((set) => ({
  messages: [],
  pendingAction: null,
  awaitingMPIN: false,
  activeAgent: '',
  isProcessing: false,
  addMessage: (msg) => set((s) => ({ messages: [...s.messages, msg] })),
  setPendingAction: (action) => set({ pendingAction: action }),
  setAwaitingMPIN: (val) => set({ awaitingMPIN: val }),
  setActiveAgent: (agent) => set({ activeAgent: agent }),
  setProcessing: (val) => set({ isProcessing: val }),
  clearMessages: () => set({ messages: [] })
}))
