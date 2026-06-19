'use client'
import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'

export default function NetworkStatus() {
  const [online, setOnline] = useState(true)
  const [showReconnected, setShowReconnected] = useState(false)

  useEffect(() => {
    const handleOnline = () => {
      setOnline(true)
      setShowReconnected(true)
      setTimeout(() => setShowReconnected(false), 2000)
    }
    const handleOffline = () => setOnline(false)
    window.addEventListener('online', handleOnline)
    window.addEventListener('offline', handleOffline)
    return () => {
      window.removeEventListener('online', handleOnline)
      window.removeEventListener('offline', handleOffline)
    }
  }, [])

  return (
    <div className="flex items-center">
      <AnimatePresence>
        {!online && (
          <motion.div
            initial={{ opacity: 0, x: 10 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: 10 }}
            className="fixed top-0 left-0 right-0 h-8 bg-warning/90 flex items-center justify-center text-white text-xs font-medium z-[60]"
          >
            <span className="w-1.5 h-1.5 bg-white rounded-full mr-2 animate-pulse" />
            Reconnecting to Saarthi servers...
          </motion.div>
        )}
        {showReconnected && (
          <motion.div
            initial={{ opacity: 0, x: 10 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: 10 }}
            className="fixed top-0 left-0 right-0 h-8 bg-accent flex items-center justify-center text-white text-xs font-medium z-[60]"
          >
            Connected
          </motion.div>
        )}
      </AnimatePresence>
      <div className={`w-2 h-2 rounded-full ${online ? 'bg-accent' : 'bg-danger'}`} />
      <span className="ml-1.5 text-xs text-text-muted">{online ? 'Connected' : 'Offline'}</span>
    </div>
  )
}
