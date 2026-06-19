'use client'
import { useRef, useEffect } from 'react'

interface Props {
  analyserNode?: AnalyserNode | null
  isRecording: boolean
}

export default function WaveformVisualizer({ analyserNode, isRecording }: Props) {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const animRef = useRef<number>(0)
  const barCount = 32

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return
    const ctx = canvas.getContext('2d')
    if (!ctx) return

    const draw = () => {
      const w = canvas.width
      const h = canvas.height
      ctx.clearRect(0, 0, w, h)

      const barW = w / barCount - 1
      const data = new Uint8Array(barCount)

      if (analyserNode && isRecording) {
        analyserNode.getByteFrequencyData(data)
      }

      for (let i = 0; i < barCount; i++) {
        let barH: number
        if (isRecording && analyserNode) {
          barH = (data[i] / 255) * h
        } else {
          barH = (Math.sin(Date.now() / 800 + i * 0.4) * 0.5 + 0.5) * 6
        }
        barH = Math.max(2, barH)
        const x = i * (barW + 1)
        const y = h - barH
        ctx.fillStyle = '#0F6E56'
        ctx.fillRect(x, y, barW, barH)
      }

      animRef.current = requestAnimationFrame(draw)
    }

    draw()
    return () => cancelAnimationFrame(animRef.current)
  }, [analyserNode, isRecording])

  return (
    <canvas
      ref={canvasRef}
      width={200}
      height={40}
      className="rounded-lg"
    />
  )
}
