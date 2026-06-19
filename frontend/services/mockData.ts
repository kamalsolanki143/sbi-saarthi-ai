import { CustomerProfile } from '@/types/customer'
import { AgentMessage } from '@/types/agent'

export const MOCK_CUSTOMER: CustomerProfile = {
  id: 'CUST001',
  name: 'Rameshwar Prasad',
  name_hindi: 'रामेश्वर प्रसाद',
  account_number: 'XXXX XXXX 4821',
  balance: 15000,
  language: 'hi',
  persona: 'farmer',
  district: 'Varanasi',
  state: 'Uttar Pradesh',
  kyc_status: 'verified',
  yono_active: false,
  active_products: ['Savings Account', 'Kisan Credit Card']
}

export const MOCK_AGENT_MESSAGE: AgentMessage = {
  id: 'msg_001',
  type: 'action_ready',
  agent: 'margdarshan',
  content: 'आपके खाते में ₹15,000 जमा हुए हैं। क्या आप ₹5,000 को 1 साल की FD में लगाना चाहेंगे? ब्याज दर 6.8% है।',
  language: 'hi',
  confidence: 0.94,
  timestamp: new Date(),
  action_payload: {
    action_type: 'create_fd',
    display_label: 'Create Fixed Deposit',
    amount: 5000,
    product: 'SBI Fixed Deposit',
    duration: '1 year',
    interest_rate: 6.8,
    risk_level: 'low'
  },
  requires_mpin: true
}

export const MOCK_RECOMMENDATIONS = [
  {
    id: 'rec_1',
    agent: 'margdarshan',
    text: 'Create a Fixed Deposit of ₹5,000 at 6.8% for 1 year',
    action: 'create_fd'
  },
  {
    id: 'rec_2',
    agent: 'saathi',
    text: 'Education expense pattern detected — consider starting a SIP for your child\'s future',
    action: 'start_sip'
  }
]

export const MOCK_TRANSACTIONS = [
  { id: 'txn_1', date: '2026-06-18', description: 'Idle Balance Credit', amount: 15000, type: 'credit' as const, category: 'deposit' },
  { id: 'txn_2', date: '2026-06-15', description: 'Kisan Credit Card Disbursement', amount: 25000, type: 'credit' as const, category: 'loan' },
  { id: 'txn_3', date: '2026-06-10', description: 'Seed Purchase - Krishi Bhavan', amount: 3400, type: 'debit' as const, category: 'agriculture' },
  { id: 'txn_4', date: '2026-06-05', description: 'Mobile Recharge', amount: 299, type: 'debit' as const, category: 'utilities' },
  { id: 'txn_5', date: '2026-05-28', description: 'PM-KISAN Subsidy Credit', amount: 6000, type: 'credit' as const, category: 'subsidy' }
]
