"use client";

import { useState } from "react";
import { 
  GitCommit, Activity, Database, Network, Search, 
  PlayCircle, Zap, Code2, UploadCloud,
  CheckCircle2, Box, ArrowRight, Play, Server
} from "lucide-react";

export default function PlatformPage() {
  const [activeStep, setActiveStep] = useState(0);
  const [activeQuery, setActiveQuery] = useState(0);

  const eventSteps = [
    { icon: GitCommit, title: "MR Opened", desc: "!342 Triggered" },
    { icon: Zap, title: "Flow Triggered", desc: "Agent Start" },
    { icon: Database, title: "Orbit Query", desc: "Traversal DSL" },
    { icon: Network, title: "Traversal", desc: "Graph Walk" },
    { icon: Search, title: "Discovery", desc: "Tests Mapped" },
    { icon: PlayCircle, title: "Pipeline Gen", desc: "CI Created" },
    { icon: CheckCircle2, title: "Results", desc: "MR Updated" }
  ];

  const querySteps = [
    { title: "Changed Symbol", detail: "validate_payment()", meta: "Function Node" },
    { title: "Traversal Query", detail: "Incoming Calls", meta: "Max Depth: 5" },
    { title: "Repos Traversed", detail: "14 Discovered", meta: "checkout-service" },
    { title: "Impacted Tests", detail: "12 Tests Identified", meta: "From 418" },
  ];

  return (
    <div className="w-full min-h-screen bg-[#FAFAF8] text-[#1E1E1E] pb-32">
      
      {/* Header */}
      <header className="px-8 lg:px-16 py-8 border-b border-[#E5E5E2] bg-white mb-16">
        <div className="max-w-[1400px] mx-auto">
          <div className="inline-flex items-center gap-2 px-3 py-1 bg-[#F4F4F1] border border-[#E5E5E2] rounded-full mb-4">
            <Database size={12} className="text-[#8B8D86]" />
            <span className="text-[10px] font-bold uppercase tracking-widest text-[#8B8D86]">System Architecture</span>
          </div>
          <h1 className="text-display-md mb-2">Platform Integration</h1>
          <p className="text-lg text-[#8B8D86] max-w-2xl">Crosscut is fundamentally a GitLab Duo Agent Platform Flow. This dashboard visualizes the execution architecture and Orbit integration.</p>
        </div>
      </header>

      <div className="max-w-[1400px] mx-auto px-8 lg:px-16 space-y-16">

        {/* SECTION 1: Architecture Overview */}
        <section>
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-sm font-bold uppercase tracking-widest text-[#8B8D86]">Macro Architecture</h2>
          </div>
          <div className="glass-panel p-16">
            <div className="flex flex-col md:flex-row items-center justify-between gap-4">
              {[
                { icon: Server, title: "GitLab", color: "text-[#1E1E1E]", bg: "bg-[#F4F4F1]" },
                { icon: Database, title: "Orbit Graph", color: "text-white", bg: "bg-[#C68A3A]" },
                { icon: Box, title: "Crosscut Flow", color: "text-white", bg: "bg-[#1E1E1E]" },
                { icon: Play, title: "GitLab CI", color: "text-[#1E1E1E]", bg: "bg-[#F4F4F1]" },
                { icon: GitCommit, title: "MR Comment", color: "text-white", bg: "bg-[#E5484D]" }
              ].map((node, i) => (
                <div key={i} className="flex items-center gap-4">
                  <div className={`w-32 h-32 rounded-2xl flex flex-col items-center justify-center ${node.bg} transition-transform hover:-translate-y-2 shadow-sm`}>
                    <node.icon size={28} className={`${node.color} mb-4`} />
                    <span className={`text-sm font-semibold ${node.color}`}>{node.title}</span>
                  </div>
                  {i < 4 && <ArrowRight className="hidden md:block text-[#E5E5E2]" />}
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* SECTION 2: Event Flow */}
        <section>
          <h2 className="text-sm font-bold uppercase tracking-widest text-[#8B8D86] mb-6">Execution Flow</h2>
          <div className="glass-panel p-12">
            <div className="flex justify-between relative">
              <div className="absolute top-6 left-8 right-8 h-px bg-[#E5E5E2] -z-10" />
              <div 
                className="absolute top-6 left-8 h-px bg-[#1E1E1E] transition-all duration-500 -z-10"
                style={{ width: `calc(${(activeStep / (eventSteps.length - 1)) * 100}% - 4rem)` }}
              />
              
              {eventSteps.map((step, i) => (
                <div 
                  key={i} 
                  onClick={() => setActiveStep(i)}
                  className={`flex flex-col items-center text-center cursor-pointer group w-24 ${activeStep === i ? 'opacity-100' : 'opacity-40 hover:opacity-100'} transition-opacity`}
                >
                  <div className={`w-12 h-12 rounded-full flex items-center justify-center mb-4 transition-colors ${activeStep >= i ? 'bg-[#1E1E1E] text-white' : 'bg-white text-[#8B8D86] border border-[#E5E5E2]'}`}>
                    <step.icon size={18} />
                  </div>
                  <div className={`text-[10px] font-bold uppercase tracking-widest mb-1 ${activeStep >= i ? 'text-[#1E1E1E]' : 'text-[#8B8D86]'}`}>{step.title}</div>
                </div>
              ))}
            </div>
          </div>
        </section>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12">
          
          {/* SECTION 3: Orbit Context */}
          <section>
            <h2 className="text-sm font-bold uppercase tracking-widest text-[#8B8D86] mb-6">Orbit Query Context</h2>
            <div className="glass-panel p-8 grid grid-cols-2 gap-6 h-[400px] content-start">
              {querySteps.map((step, i) => (
                <div 
                  key={i} 
                  onMouseEnter={() => setActiveQuery(i)}
                  className={`p-6 rounded-xl border transition-all cursor-pointer ${activeQuery === i ? 'bg-[#FAFAF8] border-[#1E1E1E] shadow-sm scale-[1.02]' : 'bg-white border-[#E5E5E2]'}`}
                >
                  <div className="text-[10px] font-bold uppercase tracking-widest text-[#8B8D86] mb-3">{step.title}</div>
                  <div className={`text-xl font-bold mb-3 ${activeQuery === i ? 'text-[#1E1E1E]' : 'text-[#1E1E1E]'}`}>{step.detail}</div>
                  <div className="text-[11px] font-mono font-medium text-[#8B8D86] bg-[#F4F4F1] px-2 py-1 rounded inline-block">{step.meta}</div>
                </div>
              ))}
            </div>
          </section>

          {/* SECTION 4: Agent Engine */}
          <section>
            <h2 className="text-sm font-bold uppercase tracking-widest text-[#8B8D86] mb-6">Agent State Machine</h2>
            <div className="glass-panel p-8 h-[400px] flex flex-col justify-between">
              <div className="space-y-6">
                <div className="grid grid-cols-3 gap-6">
                  <div className="p-6 rounded-xl bg-[#F4F4F1] border border-[#E5E5E2] text-center">
                    <div className="text-2xl font-bold text-[#1E1E1E] mb-2">Diff</div>
                    <div className="text-[10px] font-bold uppercase tracking-widest text-[#8B8D86]">Input</div>
                  </div>
                  <div className="p-6 rounded-xl bg-[#FAFAF8] border border-[#C68A3A] text-center shadow-[0_0_15px_rgba(198,138,58,0.1)] relative">
                    <div className="absolute top-0 right-0 p-2"><Database size={12} className="text-[#C68A3A]"/></div>
                    <div className="text-2xl font-bold text-[#C68A3A] mb-2">Orbit</div>
                    <div className="text-[10px] font-bold uppercase tracking-widest text-[#C68A3A]">Context</div>
                  </div>
                  <div className="p-6 rounded-xl bg-[#FAFAF8] border border-[#E5484D] text-center shadow-[0_0_15px_rgba(229,72,77,0.1)] relative">
                    <div className="absolute top-0 right-0 p-2"><CheckCircle2 size={12} className="text-[#E5484D]"/></div>
                    <div className="text-2xl font-bold text-[#E5484D] mb-2">12 Tests</div>
                    <div className="text-[10px] font-bold uppercase tracking-widest text-[#E5484D]">Output</div>
                  </div>
                </div>
                <div className="p-8 rounded-xl bg-[#1E1E1E] text-center">
                  <div className="text-lg text-white mb-3 font-medium">Decision: Bypass 406 irrelevant tests.</div>
                  <div className="text-xs text-[#8B8D86] font-mono">Execution Time: 1.2s • Confidence: High</div>
                </div>
              </div>
            </div>
          </section>

        </div>

      </div>
    </div>
  );
}
