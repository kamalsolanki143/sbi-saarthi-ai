'use client'

import Header from '@/components/Header'
import ImpactSection from '@/components/ImpactSection'
import ArchitectureSection from '@/components/ArchitectureSection/ArchitectureSection'
import ConsentShowcase from '@/components/ConsentShowcase/ConsentShowcase'
import ActionPreviewShowcase from '@/components/ActionPreviewShowcase/ActionPreviewShowcase'
import Features from '@/components/Features'
import SecuritySection from '@/components/SecuritySection/SecuritySection'
import FAQ from '@/components/FAQ'
import CTA from '@/components/CTA'
import Footer from '@/components/Footer'

import { motion } from 'framer-motion'
import { ShieldCheck } from 'lucide-react'

export default function LandingPage() {
  return (
    <main className="min-h-screen bg-gradient-to-b from-slate-950 via-slate-900 to-black text-white">
      <Header />

      {/* HERO SECTION */}
      <section className="px-8 md:px-20 py-20 flex flex-col md:flex-row items-center justify-between">
        
        {/* LEFT SIDE */}
        <div className="max-w-xl space-y-6">
          <div className="flex items-center gap-2 text-green-400 bg-green-950/30 px-4 py-2 rounded-full w-fit">
            <ShieldCheck size={18} />
            <span className="text-sm">
              SBI-Grade Secure Agentic Banking System
            </span>
          </div>

          <h1 className="text-4xl md:text-6xl font-bold leading-tight">
            Banking reimagined with{' '}
            <span className="text-blue-400">Agentic AI</span>
          </h1>

          <p className="text-gray-300 text-lg">
            <span className="text-blue-300 font-semibold">MITRA</span>{' '}
            understands user intent,
            <span className="text-purple-300 font-semibold"> SAATHI</span>{' '}
            executes secure actions,
            <span className="text-green-300 font-semibold">
              {' '}MARGDARSHAN
            </span>{' '}
            ensures policy compliance.
          </p>

          <div className="flex gap-4 pt-4 flex-wrap">
            <button className="bg-blue-500 hover:bg-blue-600 px-6 py-3 rounded-xl font-medium">
              Enter Banking Dashboard
            </button>

            <button className="border border-gray-500 px-6 py-3 rounded-xl hover:bg-white/10">
              View Agent Architecture
            </button>
          </div>
        </div>

        {/* RIGHT SIDE */}
        <motion.div
          className="mt-12 md:mt-0 bg-white/5 border border-white/10 p-6 rounded-2xl w-80"
          animate={{ y: [0, -10, 0] }}
          transition={{ repeat: Infinity, duration: 3 }}
        >
          <div className="flex items-center gap-2 mb-4 text-blue-300">
            <span className="text-xl">🧠</span>
            <span className="font-semibold">Active Agent System</span>
          </div>

          <div className="space-y-3 text-sm">
            <div className="bg-blue-500/10 p-3 rounded-xl border border-blue-500/20">
              MITRA → Intent Understanding Layer
            </div>

            <div className="bg-purple-500/10 p-3 rounded-xl border border-purple-500/20">
              SAATHI → Secure Execution Engine
            </div>

            <div className="bg-green-500/10 p-3 rounded-xl border border-green-500/20">
              MARGDARSHAN → Policy Intelligence Layer
            </div>
          </div>

          <div className="mt-4 text-xs text-gray-400">
            SBI Security Layer Active • Confidence: 94%
          </div>
        </motion.div>
      </section>

      {/* WHY SBI NEEDS SAARTHI */}
      <ImpactSection />

      {/* CONSENT MANAGER */}
      <ConsentShowcase />

      {/* ACTION PREVIEW */}
      <ActionPreviewShowcase />

      {/* FEATURES */}
      <Features />

      {/* SECURITY */}
      <SecuritySection />

      {/* FAQ */}
      <FAQ />

      {/* CTA */}
      <CTA />

      {/* FOOTER */}
      <Footer />
    </main>
  )
}