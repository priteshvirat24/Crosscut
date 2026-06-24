"use client";

import { useState } from "react";
import { Activity, Clock, Database, Network } from "lucide-react";

const demoStats = {
  total_analyses: 342,
  active_analyses: 3,
  ci_minutes_saved: 12450.5,
  avg_reduction_percentage: 94.2,
  orbit_queries_today: 142,
  avg_traversal_depth: 4,
};

const demoRecentAnalyses = [
  {
    id: "a1", project_name: "platform/payment-library", mr_iid: 342,
    mr_title: "feat: add regional compliance validation", status: "completed",
    total_tests_available: 418, selected_tests_count: 12,
    percentage_reduction: 97.1, ci_minutes_saved: 36.0,
    created_at: new Date(Date.now() - 1000 * 60 * 12).toISOString(),
  },
  {
    id: "a2", project_name: "platform/auth-service", mr_iid: 156,
    mr_title: "refactor: update token validation logic", status: "running",
    total_tests_available: 156, selected_tests_count: null,
    percentage_reduction: null, ci_minutes_saved: null,
    created_at: new Date(Date.now() - 1000 * 60 * 5).toISOString(),
  },
  {
    id: "a3", project_name: "shared/api-gateway", mr_iid: 89,
    mr_title: "fix: rate limiter configuration", status: "completed",
    total_tests_available: 890, selected_tests_count: 45,
    percentage_reduction: 94.9, ci_minutes_saved: 85.0,
    created_at: new Date(Date.now() - 1000 * 60 * 45).toISOString(),
  },
];

const demoActivity = [
  { icon: "✂️", title: "Saved 36 minutes on payment-library MR !342", time: "12 min ago" },
  { icon: "🔍", title: "Optimization started for auth-service MR !156", time: "5 min ago" },
  { icon: "📉", title: "Reduced 890 tests to 45 in api-gateway MR !89", time: "45 min ago" },
];

function statusBadge(status: string) {
  if (status === "completed") return <span className="bg-[#F4F4F1] border border-[#E5E5E2] text-[#8B8D86] px-3 py-1 rounded text-[10px] font-bold uppercase tracking-widest flex items-center gap-2 w-max"><span className="w-1.5 h-1.5 rounded-full bg-[#10b981]"></span>Completed</span>;
  if (status === "running") return <span className="bg-[#F4F4F1] border border-[#E5E5E2] text-[#8B8D86] px-3 py-1 rounded text-[10px] font-bold uppercase tracking-widest flex items-center gap-2 w-max"><span className="w-1.5 h-1.5 rounded-full bg-[#C68A3A] animate-pulse"></span>Running</span>;
  return <span className="bg-[#F4F4F1] border border-[#E5E5E2] text-[#8B8D86] px-3 py-1 rounded text-[10px] font-bold uppercase tracking-widest">{status}</span>;
}

export default function DashboardOverviewPage() {
  const [filter, setFilter] = useState<string>("all");

  const filteredAnalyses = filter === "all" ? demoRecentAnalyses : demoRecentAnalyses.filter((a) => a.status === filter);

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
          <div className="text-3xl font-bold text-[#1E1E1E] tracking-tighter">{demoStats.ci_minutes_saved.toLocaleString()}</div>
        </div>
        <div className="bg-white border border-[#E5E5E2] p-8 flex flex-col justify-between group rounded-xl shadow-sm hover:border-[#1E1E1E] transition-colors">
          <div className="flex items-center gap-3 mb-6">
            <div className="p-2 rounded bg-[#F4F4F1] text-[#1E1E1E]"><Database size={16} /></div>
            <div className="text-[10px] font-bold text-[#8B8D86] uppercase tracking-widest">Orbit Queries Today</div>
          </div>
          <div className="text-3xl font-bold text-[#1E1E1E] tracking-tighter">{demoStats.orbit_queries_today}</div>
        </div>
        <div className="bg-white border border-[#E5E5E2] p-8 flex flex-col justify-between group rounded-xl shadow-sm hover:border-[#E5484D] transition-colors">
          <div className="flex items-center gap-3 mb-6">
            <div className="p-2 rounded bg-[#F4F4F1] text-[#E5484D]"><Activity size={16} /></div>
            <div className="text-[10px] font-bold text-[#E5484D] uppercase tracking-widest">Avg Reduction</div>
          </div>
          <div className="text-3xl font-bold text-[#E5484D] tracking-tighter">-{demoStats.avg_reduction_percentage}%</div>
        </div>
        <div className="bg-white border border-[#E5E5E2] p-8 flex flex-col justify-between group rounded-xl shadow-sm hover:border-[#C68A3A] transition-colors">
          <div className="flex items-center gap-3 mb-6">
            <div className="p-2 rounded bg-[#F4F4F1] text-[#C68A3A]"><Network size={16} /></div>
            <div className="text-[10px] font-bold text-[#C68A3A] uppercase tracking-widest">Avg Traversal Depth</div>
          </div>
          <div className="text-3xl font-bold text-[#C68A3A] tracking-tighter">{demoStats.avg_traversal_depth}</div>
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
            {demoActivity.map((activity, i) => (
              <div key={i} className="flex gap-4 group">
                <div className="w-8 h-8 rounded bg-[#F4F4F1] border border-[#E5E5E2] flex items-center justify-center flex-shrink-0 text-[#1E1E1E] transition-colors shadow-sm">
                  {activity.icon}
                </div>
                <div>
                  <div className="text-[13px] font-medium text-[#1E1E1E] leading-relaxed">{activity.title}</div>
                  <div className="text-[10px] font-bold text-[#8B8D86] uppercase tracking-widest mt-1">{activity.time}</div>
                </div>
              </div>
            ))}
          </div>
        </div>

      </div>
    </div>
  );
}
