"use client";

import { OrbitReactor } from "@/components/3d/OrbitReactor";
import { ArrowRight, Database, GitCommit, Play, Box, Network } from "lucide-react";
import Link from "next/link";

export default function Home() {
  return (
    <div className="flex flex-col w-full min-h-screen bg-[#FAFAF8] text-[#1E1E1E] overflow-x-hidden">
      
      {/* 1. The Problem & Headline */}
      <section className="pt-32 pb-16 px-8 lg:px-16 max-w-[1200px] mx-auto w-full text-center">
        <div className="inline-flex items-center gap-2 px-3 py-1 bg-[#F4F4F1] border border-[#E5E5E2] rounded-full mb-8">
          <Database size={12} className="text-[#C68A3A]" />
          <span className="text-[11px] font-bold uppercase tracking-widest text-[#8B8D86]">Powered by GitLab Orbit</span>
        </div>
        
        <h1 className="text-[72px] leading-[1.1] font-bold tracking-tighter text-[#1E1E1E] mb-6">
          A single code change.<br />
          <span className="text-[#8B8D86]">Why run the whole suite?</span>
        </h1>

        <p className="text-xl text-[#8B8D86] leading-relaxed max-w-2xl mx-auto mb-12">
          Traditional CI runs the entire test suite because it lacks dependency intelligence. Crosscut uses the GitLab Orbit graph to traverse dependencies and execute only the exact tests impacted by your change.
        </p>

        <p className="text-[11px] uppercase tracking-widest text-[#8B8D86] mb-10">
          Illustrative — figures below are measured by Crosscut indexing its own repository with Orbit Local.
        </p>

        <div className="flex justify-center items-center gap-6 text-left">
          <div className="bg-white border border-[#E5E5E2] p-6 rounded-xl flex items-center gap-4 shadow-sm">
            <div className="w-10 h-10 bg-[#F4F4F1] rounded-full flex items-center justify-center text-[#1E1E1E]">
              <GitCommit size={16} />
            </div>
            <div>
              <div className="text-[10px] font-bold uppercase tracking-widest text-[#8B8D86]">The Trigger</div>
              <div className="font-bold">MR: _fmt()</div>
            </div>
          </div>
          <ArrowRight className="text-[#8B8D86]" />
          <div className="bg-white border border-[#E5E5E2] p-6 rounded-xl flex items-center gap-4 shadow-sm">
            <div className="w-10 h-10 bg-[#F4F4F1] rounded-full flex items-center justify-center text-[#E5484D]">
              <Box size={16} />
            </div>
            <div>
              <div className="text-[10px] font-bold uppercase tracking-widest text-[#E5484D]">The Waste</div>
              <div className="font-bold">78 Suite Tests</div>
            </div>
          </div>
        </div>
      </section>

      {/* 2. Orbit Traversal (The 3D Engine) */}
      <section className="w-full bg-white border-y border-[#E5E5E2] py-24 relative overflow-hidden">
        <div className="max-w-[1600px] mx-auto px-8 lg:px-16 flex flex-col lg:flex-row items-center gap-16">
          <div className="flex-1 space-y-8">
            <h2 className="text-display-md text-[#1E1E1E]">
              Orbit traverses<br />the call graph.
            </h2>
            <p className="text-lg text-[#8B8D86] leading-relaxed">
              When an MR is opened, Crosscut queries GitLab Orbit. Orbit analyzes the incoming call relationships across all repositories, discovering exactly which microservices depend on the changed function.
            </p>
            <div className="space-y-4">
              <div className="flex items-center gap-3 text-sm font-bold text-[#C68A3A] bg-[#FAFAF8] border border-[#E5E5E2] p-4 rounded">
                <Database size={16} /> Depth-first Traversal
              </div>
              <div className="flex items-center gap-3 text-sm font-bold text-[#1E1E1E] bg-[#FAFAF8] border border-[#E5E5E2] p-4 rounded">
                <Network size={16} /> Cross-Repository Edges
              </div>
            </div>
          </div>
          
          <div className="flex-1 w-full h-[500px] relative bg-[#FAFAF8] border border-[#E5E5E2] rounded-2xl overflow-hidden shadow-sm">
            <div className="absolute top-6 left-6 z-10 text-[10px] font-bold uppercase tracking-widest text-[#8B8D86] bg-white px-3 py-1.5 rounded shadow-sm border border-[#E5E5E2]">
              Interactive Graph Engine
            </div>
            <OrbitReactor currentStage={-1} />
          </div>
        </div>
      </section>

      {/* 3. Test Selection & Results */}
      <section className="py-24 px-8 lg:px-16 max-w-[1200px] mx-auto w-full text-center">
        <h2 className="text-display-md text-[#1E1E1E] mb-16">
          78 tests reduced to 8.
        </h2>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-16 text-left">
          <div className="bg-white border border-[#E5E5E2] p-8 rounded-xl shadow-sm">
            <div className="text-[10px] font-bold uppercase tracking-widest text-[#8B8D86] mb-2">Full Suite</div>
            <div className="text-4xl font-bold tracking-tighter text-[#1E1E1E] mb-2">0.50<span className="text-xl text-[#8B8D86] ml-1">s</span></div>
            <div className="text-sm font-medium text-[#8B8D86]">78 tests (1 repo, Orbit Local)</div>
          </div>
          <div className="bg-white border border-[#E5E5E2] p-8 rounded-xl shadow-sm border-t-4 border-t-[#C68A3A]">
            <div className="text-[10px] font-bold uppercase tracking-widest text-[#C68A3A] mb-2">Orbit Selection</div>
            <div className="text-4xl font-bold tracking-tighter text-[#1E1E1E] mb-2">8<span className="text-xl text-[#8B8D86] ml-1">impacted</span></div>
            <div className="text-sm font-medium text-[#8B8D86]">Transitive callers of the change</div>
          </div>
          <div className="bg-white border border-[#E5E5E2] p-8 rounded-xl shadow-sm border-t-4 border-t-[#E5484D]">
            <div className="text-[10px] font-bold uppercase tracking-widest text-[#E5484D] mb-2">Targeted Pipeline</div>
            <div className="text-4xl font-bold tracking-tighter text-[#E5484D] mb-2">0.24<span className="text-xl text-[#8B8D86] ml-1">s</span></div>
            <div className="text-sm font-medium text-[#8B8D86]">90% fewer tests</div>
          </div>
        </div>

        {/* 4. The Demo CTA */}
        <div className="bg-[#1E1E1E] rounded-2xl p-12 text-center text-white relative overflow-hidden shadow-xl">
          <div className="absolute inset-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-20 mix-blend-overlay"></div>
          <h2 className="text-3xl font-bold tracking-tight mb-4 relative z-10">See the platform in action.</h2>
          <p className="text-[#8B8D86] mb-8 max-w-lg mx-auto relative z-10">
            Watch the automated GitLab Duo Agent Platform Flow traverse the graph and generate the child pipeline in real-time.
          </p>
          <Link href="/run?autoplay=true" className="button-vermilion px-8 py-4 text-base relative z-10 inline-flex items-center gap-3 group">
            <Play size={16} fill="currentColor" />
            Launch Run Mode
            <ArrowRight size={16} className="group-hover:translate-x-1 transition-transform" />
          </Link>
        </div>
      </section>

    </div>
  );
}

