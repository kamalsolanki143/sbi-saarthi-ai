import { api } from './api'
import { AuditLog } from '@/types/audit'

export const auditService = {
  getLogs: async (customerId: string): Promise<AuditLog[]> => {
    const res = await api.getAuditLogs(customerId)
    return res.data
  },
  logClientAction: (action: string, agent: string, customerId: string) => {
    api.recordConsent(customerId, `client:${action}:${agent}`, true).catch(() => {})
  }
}
