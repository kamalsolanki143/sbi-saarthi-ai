import { create } from 'zustand'
import { AuditLog } from '@/types/audit'
import { auditService } from '@/services/audit'

interface AuditStore {
  logs: AuditLog[]
  loading: boolean
  fetchLogs: (customerId: string) => Promise<void>
  appendLog: (log: AuditLog) => void
}

export const useAuditStore = create<AuditStore>((set) => ({
  logs: [],
  loading: false,
  fetchLogs: async (customerId) => {
    set({ loading: true })
    try {
      const logs = await auditService.getLogs(customerId)
      set({ logs, loading: false })
    } catch {
      set({ loading: false })
    }
  },
  appendLog: (log) => set((s) => ({ logs: [log, ...s.logs] }))
}))
