import { Language } from './agent'

export interface CustomerProfile {
  id: string
  name: string
  name_hindi?: string
  account_number: string
  balance: number
  language: Language
  persona: 'farmer' | 'merchant' | 'salaried' | 'student'
  district: string
  state: string
  kyc_status: 'verified' | 'pending' | 'incomplete'
  yono_active: boolean
  active_products: string[]
}
