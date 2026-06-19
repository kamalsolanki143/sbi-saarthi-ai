export type AgentName = 'mitra' | 'margdarshan' | 'saathi'
export type Language = 'hi' | 'bn' | 'ta' | 'en'
export type MessageType = 'agent_message' | 'action_ready' | 'confirmation_required' | 'completed' | 'error'

export interface AgentMessage {
  id: string
  type: MessageType
  agent: AgentName
  content: string
  language: Language
  confidence: number
  timestamp: Date
  action_payload?: ActionPayload
  requires_mpin?: boolean
}

export interface ActionPayload {
  action_type: 'create_fd' | 'open_account' | 'start_sip' | 'send_nudge'
  display_label: string
  amount?: number
  product?: string
  duration?: string
  interest_rate?: number
  risk_level?: 'low' | 'medium' | 'high'
}
