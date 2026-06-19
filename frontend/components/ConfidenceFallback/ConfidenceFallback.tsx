'use client'
import { AlertTriangle } from 'lucide-react'

export default function ConfidenceFallback({ confidence }: { confidence: number }) {
  const pct = Math.round(confidence * 100)

  return (
    <div className="mt-2 p-3 rounded-lg bg-gold-light border border-gold/30">
      <div className="flex items-start gap-2">
        <AlertTriangle size={16} className="text-warning shrink-0 mt-0.5" />
        <div>
          <p className="text-xs text-warning font-medium">
            I'm not fully certain about this. Please verify with a branch or call 1800-11-2211 before proceeding.
          </p>
          <div className="flex items-center gap-2 mt-1.5">
            <span className="text-[10px] text-warning/70">Confidence: {pct}%</span>
            <div className="flex-1 max-w-[80px] h-1.5 rounded-full bg-gold/40 overflow-hidden">
              <div
                className="h-full rounded-full transition-all duration-500"
                style={{
                  width: `${pct}%`,
                  background: pct > 50 ? '#0F6E56' : pct > 30 ? '#BA7517' : '#A32D2D',
                }}
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
