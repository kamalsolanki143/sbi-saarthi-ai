export type ActionType =
  | "BALANCE"
  | "FD"
  | "TRANSFER"
  | "LOANS"
  | "CARDS"
  | "SCHEMES"

export interface Action {
  type: ActionType
  title: string
  description: string
  requiresConsent: boolean
}

export const QUICK_ACTIONS: Record<ActionType, Action> = {
  BALANCE: {
    type: "BALANCE",
    title: "Check Balance",
    description: "View your account balance instantly",
    requiresConsent: false,
  },

  FD: {
    type: "FD",
    title: "Fixed Deposit",
    description: "Create FD with ₹5000 minimum investment",
    requiresConsent: true,
  },

  TRANSFER: {
    type: "TRANSFER",
    title: "Money Transfer",
    description: "Send money to any account securely",
    requiresConsent: true,
  },

  LOANS: {
    type: "LOANS",
    title: "Loan Services",
    description: "Apply or check loan eligibility",
    requiresConsent: true,
  },

  CARDS: {
    type: "CARDS",
    title: "Card Management",
    description: "Manage debit/credit cards",
    requiresConsent: true,
  },

  SCHEMES: {
    type: "SCHEMES",
    title: "Government Schemes",
    description: "Explore eligible schemes and benefits",
    requiresConsent: false,
  },
}