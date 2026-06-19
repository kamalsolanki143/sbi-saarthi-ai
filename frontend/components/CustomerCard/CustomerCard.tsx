'use client'
import { useCustomerStore } from '@/store/useCustomerStore'

export default function CustomerCard({ compact = false }: { compact?: boolean }) {
  const customer = useCustomerStore((s) => s.customer)

  if (!customer) return null

  const initials = customer.name.split(' ').map((n) => n[0]).join('').slice(0, 2)

  const personaColors: Record<string, { bg: string; text: string }> = {
    farmer: { bg: '#E1F5EE', text: '#085041' },
    merchant: { bg: '#E6F1FB', text: '#0C447C' },
    salaried: { bg: '#FBF5E6', text: '#854F0B' },
    student: { bg: '#FAECE7', text: '#712B13' },
  }

  const pColor = personaColors[customer.persona] || personaColors.farmer

  if (compact) {
    return (
      <div className="flex items-center gap-3">
        <div className="w-9 h-9 rounded-full bg-primary-light flex items-center justify-center text-primary font-semibold text-sm shrink-0">
          {initials}
        </div>
        <div className="min-w-0 flex-1">
          <div className="text-white text-sm font-medium truncate">{customer.name}</div>
          <div className="flex items-center gap-2 mt-0.5">
            <span className="text-[10px] px-1.5 py-0.5 rounded-badge font-medium" style={{ background: pColor.bg, color: pColor.text }}>
              {customer.persona}
            </span>
            <span className={`w-1.5 h-1.5 rounded-full ${customer.kyc_status === 'verified' ? 'bg-accent' : customer.kyc_status === 'pending' ? 'bg-warning' : 'bg-danger'}`} />
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="bg-white rounded-card shadow-card p-5 border border-[rgba(26,58,92,0.10)]">
      <div className="flex items-center gap-4">
        <div className="w-12 h-12 rounded-full bg-primary-light flex items-center justify-center text-primary font-semibold text-lg shrink-0">
          {initials}
        </div>
        <div>
          <div className="text-lg font-semibold text-primary">{customer.name}</div>
          {customer.name_hindi && (
            <div className="text-devanagari text-sm text-text-muted">{customer.name_hindi}</div>
          )}
          <div className="flex items-center gap-2 mt-1.5">
            <span className="text-xs px-2 py-0.5 rounded-badge font-medium" style={{ background: pColor.bg, color: pColor.text }}>
              {customer.persona}
            </span>
            <span className={`text-xs px-2 py-0.5 rounded-badge font-medium ${customer.kyc_status === 'verified' ? 'bg-accent-light text-accent-dark' : 'bg-gold-light text-warning'}`}>
              KYC {customer.kyc_status}
            </span>
            {!customer.yono_active && (
              <span className="text-xs px-2 py-0.5 rounded-badge font-medium bg-gold-light text-warning">
                YONO inactive
              </span>
            )}
          </div>
        </div>
      </div>
      <div className="mt-4 pt-4 border-t border-[rgba(26,58,92,0.08)]">
        <div className="flex justify-between items-center">
          <span className="text-xs text-text-muted uppercase tracking-wider">Account</span>
          <span className="text-sm font-mono text-primary">{customer.account_number}</span>
        </div>
        <div className="flex justify-between items-center mt-2">
          <span className="text-xs text-text-muted uppercase tracking-wider">District</span>
          <span className="text-sm text-primary">{customer.district}, {customer.state}</span>
        </div>
        <div className="flex justify-between items-center mt-2">
          <span className="text-xs text-text-muted uppercase tracking-wider">Products</span>
          <span className="text-sm text-primary">{customer.active_products.join(', ')}</span>
        </div>
      </div>
    </div>
  )
}
