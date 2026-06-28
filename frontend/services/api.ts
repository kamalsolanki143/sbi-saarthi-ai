import axios from 'axios'
import { MOCK_CUSTOMER, MOCK_AGENT_MESSAGE } from './mockData'

const client = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  headers: { 'Content-Type': 'application/json' }
})

const useMock = () => process.env.NEXT_PUBLIC_USE_MOCK === 'true'

export const api = {
  getCustomer: async (id: string) => {
    if (useMock()) return { data: MOCK_CUSTOMER }
    return client.get(`/customers/${id}`)
  },
  getTransactions: async (id: string) => {
  return { data: [] }
  },
  processVoice: async (text: string, customerId: string, language: string) => {
    if (useMock()) return { data: { message_id: 'mock_' + Date.now() } }
    return client.post('/api/v1/voice/process', { text, customer_id: customerId, language })
  },
  transcribeAudio: async (audioBase64: string, language: string) => {
    if (useMock()) return { data: { text: 'नमस्ते, मैं FD खोलना चाहता हूँ' } }
    return client.post('/api/v1/voice/transcribe', { audio_base64: audioBase64, language })
  },
  recordConsent: async (customerId: string, actionType: string, granted: boolean) => {
    if (useMock()) return { data: { id: 'consent_' + Date.now() } }
    return client.post('/api/v1/consent/record', { customer_id: customerId, action_type: actionType, granted })
  },
  getConsent: async (customerId: string) => {
    if (useMock()) return { data: [] }
    return client.get(`/consent/${customerId}`)
  },
  triggerEvent: async (customerId: string, eventType: string, payload: object) => {
    if (useMock()) return { data: { triggered: true } }
    return client.post('/api/v1/event/trigger', { customer_id: customerId, event_type: eventType, payload })
  },
  getRecommendations: async (id: string) => {
    if (useMock()) return { data: [{ id: 'rec_1', agent: 'margdarshan', text: 'Create a Fixed Deposit of ₹5,000 at 6.8% for 1 year', action: 'create_fd' }] }
    return client.get(`/recommendations/${id}`)
  },
  getAuditLogs: async (id: string) => {
    if (useMock()) return { data: [] }
    return client.get(`/api/v1/audit/${id}`)
  },
  verifyMPIN: async (customerId: string, mpin: string) => {
    if (useMock()) {
      const demoMPIN = process.env.NEXT_PUBLIC_DEMO_MPIN || '123456'
      return { data: { verified: mpin === demoMPIN } }
    }
    return client.post('/api/v1/security/mpin/verify', { customer_id: customerId, mpin })
  },
  clearMemory: async (customerId: string) => {
    if (useMock()) return { data: { cleared: true } }
    return client.delete(`/api/v1/customer/${customerId}/memory`)
  }
}