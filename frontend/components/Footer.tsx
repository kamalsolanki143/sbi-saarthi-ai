'use client'
import { Heart } from 'lucide-react'

export default function Footer() {
  return (
    <footer className="bg-[#060E1A] border-t border-white/5 py-12">
      <div className="max-w-7xl mx-auto px-6">
        <div className="grid md:grid-cols-4 gap-8 mb-8">
          <div className="md:col-span-2">
            <span className="text-lg font-bold text-gold tracking-tight">
              SAARTHI
              <sup className="text-white/30 text-[9px] ml-0.5">AI</sup>
            </span>
            <p className="mt-2 text-sm text-white/40 max-w-sm leading-relaxed">
              From Banking Access to Banking Success. An agentic AI banking companion
              built for SBI Hackathon @ Global Fintech Fest 2026.
            </p>
          </div>
          <div>
            <h4 className="text-xs font-semibold text-white/50 uppercase tracking-wider mb-3">Product</h4>
            <ul className="space-y-2">
              {['Features', 'Agents', 'Architecture', 'Security'].map((link) => (
                <li key={link}>
                  <a href={`#${link.toLowerCase()}`} className="text-sm text-white/40 hover:text-white/70 transition-colors">
                    {link}
                  </a>
                </li>
              ))}
            </ul>
          </div>
          <div>
            <h4 className="text-xs font-semibold text-white/50 uppercase tracking-wider mb-3">Legal</h4>
            <ul className="space-y-2">
              <li><span className="text-sm text-white/40">DPDP Compliant</span></li>
              <li><span className="text-sm text-white/40">Privacy by Design</span></li>
              <li><span className="text-sm text-white/40">Hackathon Project</span></li>
            </ul>
          </div>
        </div>

        <div className="pt-8 border-t border-white/5 flex flex-col md:flex-row items-center justify-between gap-4">
          <p className="text-xs text-white/30">
            &copy; 2026 Team Neural Ninjas. Built for SBI Hackathon @ GFF 2026.
          </p>
          <p className="text-xs text-white/20 flex items-center gap-1">
            Made with <Heart size={10} className="text-danger" /> for financial inclusion
          </p>
        </div>
      </div>
    </footer>
  )
}
