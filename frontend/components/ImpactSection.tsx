'use client'

import { motion } from 'framer-motion'

const impactMetrics = [
  {
    icon: '👥',
    value: '500M+',
    label: 'Potential SBI Customers',
  },
  {
    icon: '🌏',
    value: '22+',
    label: 'Indian Languages Expandable',
  },
  {
    icon: '⚡',
    value: '70%',
    label: 'Faster Customer Assistance',
  },
  {
    icon: '🏦',
    value: '24/7',
    label: 'AI Banking Availability',
  },
]

const inclusionMetrics = [
  {
    icon: '📈',
    value: '35%',
    label: 'Higher Product Discovery',
  },
  {
    icon: '🎤',
    value: '100%',
    label: 'Voice-First Accessibility',
  },
  {
    icon: '🛡️',
    value: '0',
    label: 'Autonomous Transactions',
  },
  {
    icon: '📊',
    value: '100%',
    label: 'Auditable Decisions',
  },
]

const challenges = [
  'Language barriers',
  'Low digital literacy',
  'Branch dependency',
  'High support workload',
  'Limited financial awareness',
]

const solutions = [
  'Multilingual voice banking',
  'Natural language interaction',
  'AI-guided self-service',
  'Automated customer assistance',
  'Personalized recommendations',
]

const roiCards = [
  '📞 Reduced Call Center Load',
  '🏦 Increased Product Adoption',
  '😊 Better Customer Experience',
  '🌍 Greater Rural Reach',
]

export default function ImpactSection() {
  return (
    <section className="relative overflow-hidden bg-slate-950 py-24">
      <div className="mx-auto max-w-7xl px-6">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 25 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="mx-auto mb-16 max-w-4xl text-center"
        >
          <span className="text-sm font-medium uppercase tracking-wider text-blue-400">
            Why SBI Needs SAARTHI
          </span>

          <h2 className="mt-4 text-4xl font-bold text-white md:text-5xl">
            Transforming Banking Access for Bharat at Scale
          </h2>

          <p className="mt-6 text-lg text-white/60">
            SAARTHI helps SBI reach underserved customers, reduce operational
            costs, increase product adoption, and provide inclusive banking
            experiences across India&apos;s linguistic and digital divide.
          </p>
        </motion.div>

        {/* Metrics Row 1 */}
        <div className="mb-6 grid gap-6 md:grid-cols-4">
          {impactMetrics.map((item) => (
            <div
              key={item.label}
              className="rounded-2xl border border-white/10 bg-white/5 p-6 text-center backdrop-blur-xl"
            >
              <div className="text-4xl">{item.icon}</div>
              <div className="mt-3 text-3xl font-bold text-white">
                {item.value}
              </div>
              <div className="mt-2 text-sm text-white/60">
                {item.label}
              </div>
            </div>
          ))}
        </div>

        {/* Metrics Row 2 */}
        <div className="mb-16 grid gap-6 md:grid-cols-4">
          {inclusionMetrics.map((item) => (
            <div
              key={item.label}
              className="rounded-2xl border border-white/10 bg-white/5 p-6 text-center backdrop-blur-xl"
            >
              <div className="text-4xl">{item.icon}</div>
              <div className="mt-3 text-3xl font-bold text-white">
                {item.value}
              </div>
              <div className="mt-2 text-sm text-white/60">
                {item.label}
              </div>
            </div>
          ))}
        </div>

        {/* Challenges vs Solutions */}
        <div className="mb-16 grid gap-8 md:grid-cols-2">
          <div className="rounded-3xl border border-red-500/20 bg-red-500/5 p-8">
            <h3 className="mb-6 text-2xl font-bold text-white">
              Current Challenges
            </h3>

            <ul className="space-y-4">
              {challenges.map((item) => (
                <li key={item} className="text-white/70">
                  • {item}
                </li>
              ))}
            </ul>
          </div>

          <div className="rounded-3xl border border-green-500/20 bg-green-500/5 p-8">
            <h3 className="mb-6 text-2xl font-bold text-white">
              SAARTHI Solutions
            </h3>

            <ul className="space-y-4">
              {solutions.map((item) => (
                <li key={item} className="text-white/70">
                  • {item}
                </li>
              ))}
            </ul>
          </div>
        </div>

        {/* Financial Inclusion */}
        <div className="mb-16 rounded-3xl border border-blue-500/20 bg-blue-500/5 p-10 text-center">
          <h3 className="mb-6 text-3xl font-bold text-white">
            Financial Inclusion Impact
          </h3>

          <p className="mx-auto max-w-3xl text-lg leading-relaxed text-white/70">
            A farmer in Uttar Pradesh, a pensioner in Tamil Nadu, or a student
            in West Bengal can access SBI services using their own language and
            voice.
          </p>

          <div className="mt-10 grid gap-4 md:grid-cols-4">
            <div className="rounded-xl bg-white/5 p-4">🎤 Voice First</div>
            <div className="rounded-xl bg-white/5 p-4">🌐 Multilingual</div>
            <div className="rounded-xl bg-white/5 p-4">📱 Low Bandwidth</div>
            <div className="rounded-xl bg-white/5 p-4">🏦 Rural Friendly</div>
          </div>
        </div>

        {/* ROI Section */}
        <div>
          <h3 className="mb-8 text-center text-3xl font-bold text-white">
            Business Impact for SBI
          </h3>

          <div className="grid gap-6 md:grid-cols-4">
            {roiCards.map((item) => (
              <div
                key={item}
                className="rounded-2xl border border-white/10 bg-white/5 p-6 text-center"
              >
                <div className="font-medium text-white">{item}</div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  )
}