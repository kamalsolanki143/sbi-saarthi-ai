'use client'

import { motion } from 'framer-motion'
import {
  Mic,
  Languages,
  Globe,
  Brain,
  Database,
  Zap,
  ShieldCheck,
  Lock,
  FileCheck,
  Building2,
  BarChart3,
} from 'lucide-react'

export default function ArchitectureSection() {
  return (
    <section
      id="architecture"
      className="relative overflow-hidden bg-[#0D1B2A] py-24"
    >
      <div className="absolute inset-0 bg-grid opacity-20" />

      <div className="relative z-10 mx-auto max-w-7xl px-6">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 25 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="mx-auto mb-16 max-w-4xl text-center"
        >
          <span className="text-sm font-medium uppercase tracking-wider text-blue-400">
            SAARTHI Agent Architecture
          </span>

          <h2 className="mt-4 text-4xl font-bold text-white md:text-5xl">
            How Customer Requests Become Secure Banking Actions
          </h2>

          <p className="mt-6 text-lg text-white/60">
            From voice input to SBI-grade execution, every request passes
            through language processing, agent collaboration, policy
            validation, human approval, and compliance auditing.
          </p>
        </motion.div>

        {/* Voice Layer */}
        <div className="mb-12">
          <h3 className="mb-6 text-center text-2xl font-bold text-white">
            VOICE LAYER
          </h3>

          <div className="grid gap-6 md:grid-cols-3">
            {[
              {
                icon: Mic,
                title: 'Voice Input',
                desc: 'Customer voice & text requests',
              },
              {
                icon: Languages,
                title: 'Bhashini',
                desc: 'Speech-to-Text & Language Detection',
              },
              {
                icon: Globe,
                title: 'Multilingual Layer',
                desc: 'Hindi • Tamil • Bengali • English',
              },
            ].map((item) => {
              const Icon = item.icon

              return (
                <div
                  key={item.title}
                  className="rounded-2xl border border-white/10 bg-white/5 p-6 backdrop-blur-xl"
                >
                  <Icon className="mb-4 h-10 w-10 text-blue-400" />
                  <h4 className="font-semibold text-white">{item.title}</h4>
                  <p className="mt-2 text-sm text-white/60">{item.desc}</p>
                </div>
              )
            })}
          </div>
        </div>

        {/* Orchestration Layer */}
        <div className="mb-12">
          <h3 className="mb-6 text-center text-2xl font-bold text-white">
            ORCHESTRATION LAYER
          </h3>

          <div className="grid gap-6 md:grid-cols-3">
            {[
              {
                icon: Brain,
                title: 'LangGraph',
                desc: 'Routes requests & manages workflows',
              },
              {
                icon: Database,
                title: 'Shared Memory',
                desc: 'Redis + Vector Database',
              },
              {
                icon: Zap,
                title: 'Event Engine',
                desc: 'Triggers intelligent banking actions',
              },
            ].map((item) => {
              const Icon = item.icon

              return (
                <div
                  key={item.title}
                  className="rounded-2xl border border-white/10 bg-white/5 p-6 backdrop-blur-xl"
                >
                  <Icon className="mb-4 h-10 w-10 text-cyan-400" />
                  <h4 className="font-semibold text-white">{item.title}</h4>
                  <p className="mt-2 text-sm text-white/60">{item.desc}</p>
                </div>
              )
            })}
          </div>
        </div>

        {/* Multi-Agent Layer */}
        <div className="mb-16">
          <h3 className="mb-8 text-center text-3xl font-bold text-white">
            MULTI-AGENT LAYER
          </h3>

          <div className="flex flex-col items-center gap-6">
            <div className="w-full max-w-md rounded-3xl bg-gradient-to-r from-blue-600 to-cyan-500 p-8 text-center shadow-xl">
              <div className="text-4xl">🧠</div>
              <h4 className="mt-3 text-2xl font-bold text-white">MITRA</h4>
              <p className="mt-2 text-white/90">Customer Acquisition</p>
            </div>

            <div className="text-3xl text-white/50">↓</div>

            <div className="w-full max-w-md rounded-3xl bg-gradient-to-r from-purple-600 to-pink-500 p-8 text-center shadow-xl">
              <div className="text-4xl">🛡️</div>
              <h4 className="mt-3 text-2xl font-bold text-white">
                MARGDARSHAN
              </h4>
              <p className="mt-2 text-white/90">Policy Intelligence</p>
            </div>

            <div className="text-3xl text-white/50">↓</div>

            <div className="w-full max-w-md rounded-3xl bg-gradient-to-r from-orange-500 to-red-500 p-8 text-center shadow-xl">
              <div className="text-4xl">⚡</div>
              <h4 className="mt-3 text-2xl font-bold text-white">SAATHI</h4>
              <p className="mt-2 text-white/90">Secure Execution</p>
            </div>
          </div>
        </div>

        {/* Security Layer */}
        <div className="mb-12">
          <h3 className="mb-6 text-center text-2xl font-bold text-white">
            SECURITY LAYER
          </h3>

          <div className="grid gap-6 md:grid-cols-3">
            {[
              {
                icon: ShieldCheck,
                title: 'Confidence Engine',
                desc: 'Risk validation & guardrails',
              },
              {
                icon: Lock,
                title: 'MPIN Approval',
                desc: 'Human-in-the-loop confirmation',
              },
              {
                icon: FileCheck,
                title: 'Consent Manager',
                desc: 'Explicit approval workflows',
              },
            ].map((item) => {
              const Icon = item.icon

              return (
                <div
                  key={item.title}
                  className="rounded-2xl border border-white/10 bg-white/5 p-6 backdrop-blur-xl"
                >
                  <Icon className="mb-4 h-10 w-10 text-green-400" />
                  <h4 className="font-semibold text-white">{item.title}</h4>
                  <p className="mt-2 text-sm text-white/60">{item.desc}</p>
                </div>
              )
            })}
          </div>
        </div>

        {/* Execution Layer */}
        <div>
          <h3 className="mb-6 text-center text-2xl font-bold text-white">
            EXECUTION LAYER
          </h3>

          <div className="grid gap-6 md:grid-cols-3">
            {[
              {
                icon: Building2,
                title: 'SBI Core Banking',
                desc: 'FD, Loans, Transfers & Accounts',
              },
              {
                icon: BarChart3,
                title: 'Audit Trail',
                desc: 'Complete decision logging',
              },
              {
                icon: FileCheck,
                title: 'DPDP Compliance',
                desc: 'Privacy & regulatory compliance',
              },
            ].map((item) => {
              const Icon = item.icon

              return (
                <div
                  key={item.title}
                  className="rounded-2xl border border-white/10 bg-white/5 p-6 backdrop-blur-xl"
                >
                  <Icon className="mb-4 h-10 w-10 text-orange-400" />
                  <h4 className="font-semibold text-white">{item.title}</h4>
                  <p className="mt-2 text-sm text-white/60">{item.desc}</p>
                </div>
              )
            })}
          </div>
        </div>
      </div>
    </section>
  )
}