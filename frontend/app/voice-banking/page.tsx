'use client'
import { motion } from 'framer-motion'
import AgentChat from '@/components/AgentChat/AgentChat'

const pageVariants = {
  initial: { opacity: 0, y: 16 },
  animate: { opacity: 1, y: 0, transition: { duration: 0.3, ease: [0.22, 1, 0.36, 1] } },
}

export default function VoiceBanking() {
  return (
    <motion.div
      variants={pageVariants}
      initial="initial"
      animate="animate"
      className="flex-1 flex flex-col h-full"
    >
      <AgentChat />
    </motion.div>
  )
}
