"use client";

import { useState, useEffect } from "react";
import { Activity, Clock, Database, Network } from "lucide-react";

interface CrosscutResults {
  metrics: {
    total_tests: number;
    selected_tests: number;
    percentage_reduction: number;
  };
  run_full_suite: boolean;
  selected_tests: any[];
  changed_symbols: string[];
  timing?: {
    seconds_saved: number;
    full_suite_seconds: number;
    selected_seconds: number;
  };
}

function statusBadge(status: string) {
  if (status === "completed") return <span className="bg-[#F4F4F1] border border-[#E5E5E2] text-[#8B8D86] px-3 py-1 rounded text-[10px] font-bold uppercase tracking-widest flex items-center gap-2 w-max"><span className="w-1.5 h-1.5 rounded-full bg-[#10b981]"></span>Completed</span>;
  if (status === "running") return <span className="bg-[#F4F4F1] border border-[#E5E5E2] text-[#8B8D86] px-3 py-1 rounded text-[10px] font-bold uppercase tracking-widest flex items-center gap-2 w-max"><span className="w-1.5 h-1.5 rounded-full bg-[#C68A3A] animate-pulse"></span>Running</span>;
  return <span className="bg-[#F4F4F1] border border-[#E5E5E2] text-[#8B8D86] px-3 py-1 rounded text-[10px] font-bold uppercase tracking-widest">{status}</span>;
}

export default function DashboardOverviewPage() {
  const [filter, setFilter] = useState<string>("all");
  const [results, setResults] = useState<CrosscutResults | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('/api/results')
      .then(r => r.json())
      .then(data => {
        if (!data.error) setResults(data);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  if (loading) return <div className="p-8 text-[#8B8D86] animate-pulse">Loading authentic data from engine...</div>;
  if (!results) return (
    <div className="p-12 text-center border-2 border-dashed border-[#E5E5E2] rounded-xl bg-[#FAFAF8] mt-8">
      <Network className="mx-auto mb-4 text-[#C68A3A] opacity-50" size={32} />
      <h3 className="text-[#1E1E1E] font-bold mb-2">Waiting for analysis...</h3>
      <p className="text-[#8B8D86] text-sm">Run the Crosscut CLI to generate results.</p>
    </div>
  );

  const stats = {
    ci_minutes_saved: results.timing ? (results.timing.seconds_saved / 60).toFixed(1) : "0",
    avg_reduction_percentage: results.metrics.percentage_reduction.toFixed(1),
    orbit_queries_today: 1,
    avg_traversal_depth: results.selected_tests.length > 0 
      ? Math.round(results.selected_tests.reduce((a, b) => a + (b.depth || 0), 0) / results.selected_tests.length)
      : 0,
  };

  const recentAnalyses = [
    {
      id: "latest", 
      project_name: "Crosscut Local", 
      mr_iid: "CLI",
      mr_title: results.changed_symbols.length > 0 ? `Changed: ${results.changed_symbols.join(", ")}` : "No symbols changed", 
      status: "completed",
      total_tests_available: results.metrics.total_tests, 
      selected_tests_count: results.metrics.selected_tests,
      percentage_reduction: results.metrics.percentage_reduction, 
      ci_minutes_saved: results.timing ? results.timing.seconds_saved / 60 : 0,
    }
  ];

  const filteredAnalyses = filter === "all" ? recentAnalyses : recentAnalyses.filter((a) => a.status === filter);

  return (
    <div className="space-y-12 animate-in fade-in duration-500 text-[#1E1E1E] pb-32 max-w-[1600px]">
      
      <div>
        <h1 className="text-display-md mb-2">Overview</h1>
        <p className="text-[#8B8D86]">Monitor Crosscut optimizations across your workspace.</p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-white border border-[#E5E5E2] p-8 flex flex-col justify-between group rounded-xl shadow-sm hover:border-[#1E1E1E] transition-colors">
          <div className="flex items-center gap-3 mb-6">
            <div className="p-2 rounded bg-[#F4F4F1] text-[#1E1E1E]"><Clock size={16} /></div>
            <div className="text-[10px] font-bold text-[#8B8D86] uppercase tracking-widest">CI Minutes Saved</div>
          </div>
          <div className="text-3xl font-bold text-[#1E1E1E] tracking-tighter">{stats.ci_minutes_saved}</div>
        </div>
        <div className="bg-white border border-[#E5E5E2] p-8 flex flex-col justify-between group rounded-xl shadow-sm hover:border-[#1E1E1E] transition-colors">
          <div className="flex items-center gap-3 mb-6">
            <div className="p-2 rounded bg-[#F4F4F1] text-[#1E1E1E]"><Database size={16} /></div>
            <div className="text-[10px] font-bold text-[#8B8D86] uppercase tracking-widest">Orbit Queries Today</div>
          </div>
          <div className="text-3xl font-bold text-[#1E1E1E] tracking-tighter">{stats.orbit_queries_today}</div>
        </div>
        <div className="bg-white border border-[#E5E5E2] p-8 flex flex-col justify-between group rounded-xl shadow-sm hover:border-[#E5484D] transition-colors">
          <div className="flex items-center gap-3 mb-6">
            <div className="p-2 rounded bg-[#F4F4F1] text-[#E5484D]"><Activity size={16} /></div>
            <div className="text-[10px] font-bold text-[#E5484D] uppercase tracking-widest">Avg Reduction</div>
          </div>
          <div className="text-3xl font-bold text-[#E5484D] tracking-tighter">-{stats.avg_reduction_percentage}%</div>
        </div>
        <div className="bg-white border border-[#E5E5E2] p-8 flex flex-col justify-between group rounded-xl shadow-sm hover:border-[#C68A3A] transition-colors">
          <div className="flex items-center gap-3 mb-6">
            <div className="p-2 rounded bg-[#F4F4F1] text-[#C68A3A]"><Network size={16} /></div>
            <div className="text-[10px] font-bold text-[#C68A3A] uppercase tracking-widest">Avg Traversal Depth</div>
          </div>
          <div className="text-3xl font-bold text-[#C68A3A] tracking-tighter">{stats.avg_traversal_depth}</div>
        </div>
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-3 gap-8">
        
        {/* Table Area */}
        <div className="xl:col-span-2 space-y-6">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-bold tracking-tight">Recent Optimizations</h2>
            <div className="flex gap-2 bg-[#F4F4F1] p-1 rounded border border-[#E5E5E2]">
              {["all", "running", "completed"].map((f) => (
                <button
                  key={f}
                  onClick={() => setFilter(f)}
                  className={`px-3 py-1.5 rounded text-[10px] font-bold uppercase tracking-widest transition-all ${filter === f ? "bg-white text-[#1E1E1E] shadow-sm border border-[#E5E5E2]" : "text-[#8B8D86] hover:text-[#1E1E1E] border border-transparent"}`}
                >
                  {f}
                </button>
              ))}
            </div>
          </div>

          <div className="bg-white border border-[#E5E5E2] rounded-xl overflow-hidden shadow-sm">
            <table className="w-full text-left text-sm">
              <thead className="bg-[#F4F4F1] border-b border-[#E5E5E2]">
                <tr>
                  <th className="px-6 py-4 font-bold text-[10px] uppercase tracking-widest text-[#8B8D86]">Project / MR</th>
                  <th className="px-6 py-4 font-bold text-[10px] uppercase tracking-widest text-[#8B8D86]">Status</th>
                  <th className="px-6 py-4 font-bold text-[10px] uppercase tracking-widest text-[#8B8D86] text-right">Tests</th>
                  <th className="px-6 py-4 font-bold text-[10px] uppercase tracking-widest text-[#8B8D86] text-right">Reduction</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#E5E5E2]">
                {filteredAnalyses.map((a) => (
                  <tr key={a.id} className="hover:bg-[#FAFAF8] transition-colors group cursor-pointer">
                    <td className="px-6 py-4">
                      <div className="font-bold text-[#1E1E1E] mb-1">{a.project_name}</div>
                      <div className="text-[12px] font-medium text-[#8B8D86]">!{a.mr_iid} · {a.mr_title}</div>
                    </td>
                    <td className="px-6 py-4">{statusBadge(a.status)}</td>
                    <td className="px-6 py-4 text-right">
                      {a.selected_tests_count !== null ? (
                        <span className="font-mono text-[13px] text-[#1E1E1E] bg-[#F4F4F1] px-2 py-1 rounded border border-[#E5E5E2]">{a.selected_tests_count} <span className="text-[#8B8D86]">/ {a.total_tests_available}</span></span>
                      ) : <span className="text-[#8B8D86]">-</span>}
                    </td>
                    <td className="px-6 py-4 text-right">
                      {a.percentage_reduction !== null ? (
                        <span className="text-[#E5484D] font-mono text-[14px] font-bold">-{a.percentage_reduction.toFixed(1)}%</span>
                      ) : <span className="text-[#8B8D86]">-</span>}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Sidebar Activity */}
        <div className="space-y-6">
          <h2 className="text-lg font-bold tracking-tight">Activity Feed</h2>
          <div className="bg-white border border-[#E5E5E2] rounded-xl p-6 space-y-6 shadow-sm">
            <div className="flex gap-4 group">
              <div className="w-8 h-8 rounded bg-[#F4F4F1] border border-[#E5E5E2] flex items-center justify-center flex-shrink-0 text-[#1E1E1E] transition-colors shadow-sm">
                ✂️
              </div>
              <div>
                <div className="text-[13px] font-medium text-[#1E1E1E] leading-relaxed">
                  Selected {results.metrics.selected_tests} of {results.metrics.total_tests} tests ({results.metrics.percentage_reduction.toFixed(1)}% fewer)
                </div>
                <div className="text-[10px] font-bold text-[#8B8D86] uppercase tracking-widest mt-1">Just now</div>
              </div>
            </div>
          </div>
        </div>

      </div>
    </div>
  );
}
