export interface ConsentRecord {
  id: string
  customer_id: string
  action_type: string
  granted: boolean
  timestamp: string
  expires_at: string
}
