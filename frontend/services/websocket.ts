import { AgentMessage } from '@/types/agent'
import { MOCK_AGENT_MESSAGE } from './mockData'

type MessageHandler = (msg: AgentMessage) => void

class AgentWebSocket {
  private ws: WebSocket | null = null
  private handlers: MessageHandler[] = []
  private reconnectTimer: ReturnType<typeof setTimeout> | null = null
  private mockMode = false

  connect(customerId: string) {
    if (process.env.NEXT_PUBLIC_USE_MOCK === 'true') {
      this.mockMode = true
      return
    }
    const url = `${process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000'}/ws/agent?customer_id=${customerId}`
    this.ws = new WebSocket(url)
    this.ws.onmessage = (e) => {
      try {
        const msg: AgentMessage = { ...JSON.parse(e.data), timestamp: new Date() }
        this.handlers.forEach(h => h(msg))
      } catch {}
    }
    this.ws.onclose = () => {
      this.reconnectTimer = setTimeout(() => this.connect(customerId), 3000)
    }
  }

  simulateMessage(msg: AgentMessage) {
    if (this.mockMode) {
      this.handlers.forEach(h => h(msg))
    }
  }

  send(payload: object) {
    if (this.mockMode) return
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(payload))
    }
  }

  onMessage(handler: MessageHandler) {
    this.handlers.push(handler)
    return () => { this.handlers = this.handlers.filter(h => h !== handler) }
  }

  disconnect() {
    if (this.reconnectTimer) clearTimeout(this.reconnectTimer)
    this.ws?.close()
  }
}

export const agentSocket = new AgentWebSocket()
