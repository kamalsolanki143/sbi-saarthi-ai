import { create } from 'zustand'
import { CustomerProfile } from '@/types/customer'
import { Transaction } from '@/types/transaction'
import { api } from '@/services/api'

interface CustomerStore {
  customer: CustomerProfile | null
  transactions: Transaction[]
  loading: boolean
  fetchCustomer: (id: string) => Promise<void>
  setLanguage: (lang: CustomerProfile['language']) => void
}

export const useCustomerStore = create<CustomerStore>((set) => ({
  customer: null,
  transactions: [],
  loading: false,
  fetchCustomer: async (id) => {
    set({ loading: true })
    try {
      const [cRes, tRes] = await Promise.all([api.getCustomer(id), api.getTransactions(id)])
      set({ customer: cRes.data, transactions: tRes.data, loading: false })
    } catch {
      set({ loading: false })
    }
  },
  setLanguage: (lang) => set((s) => s.customer ? { customer: { ...s.customer, language: lang } } : {})
}))
