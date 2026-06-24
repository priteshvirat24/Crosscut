"use client";

import { CheckCircle2, ChevronRight, Play } from "lucide-react";

const demoAnalyses = [
  {
    id: "a1", project_name: "platform/payment-library", mr_iid: 342,
    mr_title: "feat: add regional compliance validation", status: "completed",
    total_tests_available: 418, selected_tests_count: 12,
    ci_minutes_saved: 36.0, percentage_reduction: 97.1,
    estimated_original_runtime: "38 min", estimated_optimized_runtime: "2 min",
    created_at: new Date(Date.now() - 1000 * 60 * 12).toISOString(),
    impacted_tests: [
      { test_name: "test_checkout_validates_payment", repository: "checkout-service", reasoning: "Directly calls changed function" },
      { test_name: "test_subscription_validation", repository: "billing-service", reasoning: "Transitive dependency" },
      { test_name: "test_regional_compliance", repository: "payment-sdk-python", reasoning: "SDK wrapper test" },
    ],
    executive_summary: "Crosscut selected 12 tests out of 418 available, reducing execution by 97.1%. Targeted pipeline completed in 2m 0s. All 12 tests passed.",
  },
  {
    id: "a3", project_name: "shared/api-gateway", mr_iid: 89,
    mr_title: "fix: rate limiter configuration", status: "completed",
    total_tests_available: 890, selected_tests_count: 45,
    ci_minutes_saved: 85.0, percentage_reduction: 94.9,
    estimated_original_runtime: "90 min", estimated_optimized_runtime: "5 min",
    created_at: new Date(Date.now() - 1000 * 60 * 45).toISOString(),
    impacted_tests: [
      { test_name: "test_rate_limiter_format", repository: "api-gateway", reasoning: "Direct test for configuration format" },
    ],
    executive_summary: "Crosscut selected 45 tests out of 890 available, reducing execution by 94.9%.",
  },
];

function statusBadge(status: string) {
  if (status === "completed") return <span className="bg-[#F4F4F1] border border-[#E5E5E2] text-[#8B8D86] px-3 py-1 rounded text-[10px] font-bold uppercase tracking-widest flex items-center gap-2 w-max"><CheckCircle2 size={12} className="text-[#10b981]"/> Completed</span>;
  if (status === "running") return <span className="bg-[#F4F4F1] border border-[#E5E5E2] text-[#8B8D86] px-3 py-1 rounded text-[10px] font-bold uppercase tracking-widest flex items-center gap-2 w-max"><span className="w-1.5 h-1.5 bg-[#C68A3A] rounded-full animate-pulse"></span>Running</span>;
  return <span className="bg-[#F4F4F1] border border-[#E5E5E2] text-[#8B8D86] px-3 py-1 rounded text-[10px] font-bold uppercase tracking-widest">{status}</span>;
}

export default function AnalysesPage() {
  return (
    <div className="space-y-12 animate-in fade-in duration-500 text-[#1E1E1E] pb-32 max-w-[1200px] mx-auto">
      <div>
        <h1 className="text-display-md mb-2 text-[#1E1E1E]">Optimization Runs</h1>
        <p className="text-[#8B8D86]">Track ongoing and completed targeted pipelines across your workspace.</p>
      </div>

      <div className="space-y-8">
        {demoAnalyses.map((analysis) => (
          <div key={analysis.id} className="bg-white border border-[#E5E5E2] rounded-xl p-8 relative overflow-hidden group shadow-sm hover:border-[#1E1E1E] transition-colors">
            
            <div className="flex flex-col lg:flex-row justify-between items-start lg:items-center gap-8 mb-8 relative z-10">
              <div>
                <div className="flex items-center gap-4 mb-3">
                  <h3 className="text-2xl font-bold tracking-tight text-[#1E1E1E]">{analysis.project_name}</h3>
                  {statusBadge(analysis.status)}
                </div>
                <div className="flex items-center gap-2 text-[13px] text-[#8B8D86]">
                  <span className="px-2 py-0.5 rounded bg-[#F4F4F1] border border-[#E5E5E2] text-[#1E1E1E] font-mono text-xs">!{analysis.mr_iid}</span>
                  <span className="font-medium">{analysis.mr_title}</span>
                </div>
              </div>

              {analysis.percentage_reduction !== null && (
                <div className="flex gap-10 text-center bg-[#FAFAF8] border border-[#E5E5E2] p-6 rounded-xl">
                  <div>
                    <div className="text-3xl font-bold text-[#E5484D] tracking-tighter">
                      -{analysis.percentage_reduction.toFixed(1)}%
                    </div>
                    <div className="text-[10px] font-bold text-[#8B8D86] uppercase tracking-widest mt-2">Reduction</div>
                  </div>
                  <div className="w-px bg-[#E5E5E2]" />
                  <div>
                    <div className="text-3xl font-bold text-[#1E1E1E] tracking-tighter">
                      {analysis.ci_minutes_saved}m
                    </div>
                    <div className="text-[10px] font-bold text-[#8B8D86] uppercase tracking-widest mt-2">Saved</div>
                  </div>
                  <div className="w-px bg-[#E5E5E2]" />
                  <div>
                    <div className="text-3xl font-bold text-[#1E1E1E] tracking-tighter">
                      {analysis.selected_tests_count} <span className="text-[#8B8D86] text-lg">/ {analysis.total_tests_available}</span>
                    </div>
                    <div className="text-[10px] font-bold text-[#8B8D86] uppercase tracking-widest mt-2">Tests Run</div>
                  </div>
                </div>
              )}
            </div>

            {analysis.impacted_tests.length > 0 && (
              <div className="pt-6 border-t border-[#E5E5E2] relative z-10">
                <div className="flex items-center gap-2 text-[10px] font-bold text-[#8B8D86] uppercase tracking-widest mb-4">
                  <Play size={10} className="text-[#1E1E1E]"/> Sample Impacted Tests
                </div>
                <div className="space-y-2">
                  {analysis.impacted_tests.map((test, i) => (
                    <div key={i} className="flex items-center gap-6 p-4 rounded bg-[#FAFAF8] border border-[#E5E5E2] text-[13px]">
                      <span className="text-[#1E1E1E] font-bold w-40 shrink-0 truncate">{test.repository}</span>
                      <code className="text-[#8B8D86] font-mono px-2 py-1 rounded bg-white border border-[#E5E5E2]">{test.test_name}</code>
                      <span className="text-[#8B8D86] ml-auto truncate max-w-xs text-sm">{test.reasoning}</span>
                    </div>
                  ))}
                  {analysis.selected_tests_count > analysis.impacted_tests.length && (
                    <div className="text-center text-[10px] font-bold text-[#8B8D86] uppercase tracking-widest mt-6">
                      + {analysis.selected_tests_count - analysis.impacted_tests.length} more tests...
                    </div>
                  )}
                </div>
              </div>
            )}

            {analysis.executive_summary && (
              <div className="mt-8 p-6 rounded bg-[#F4F4F1] border border-[#E5E5E2] text-[13px] text-[#1E1E1E] leading-relaxed relative z-10">
                <strong className="text-[#8B8D86] mr-2 uppercase tracking-widest text-[10px]">Pipeline Summary:</strong> 
                {analysis.executive_summary}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
