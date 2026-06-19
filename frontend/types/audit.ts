import { AgentName } from './agent'

export interface AuditLog {
  id: string
  customer_id: string
  agent: AgentName
  action: string
  status: 'success' | 'rejected' | 'pending'
  timestamp: string
  mpin_verified: boolean
  confidence: number
}
