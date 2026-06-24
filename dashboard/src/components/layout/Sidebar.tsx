"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { LayoutDashboard, Activity, Network, Settings, Database } from "lucide-react";

const navItems = [
  { href: "/dashboard", label: "Overview", icon: LayoutDashboard },
  { href: "/dashboard/platform", label: "Platform Integration", icon: Database },
  { href: "/dashboard/analyses", label: "Active Analyses", icon: Activity },
  { href: "/dashboard/explorer", label: "Impact Explorer", icon: Network },
];

const settingsItems = [
  { href: "/dashboard/settings", label: "Settings", icon: Settings },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="w-[260px] h-full bg-[#FAFAF8] border-r border-[#E5E5E2] flex flex-col shrink-0 pt-16">
      <nav className="flex-1 p-6 flex flex-col gap-1 mt-4">
        <div className="text-[10px] font-bold text-[#8B8D86] uppercase tracking-widest mb-4 px-3">Workspace</div>
        {navItems.map((item) => {
          const isActive = pathname === item.href;
          return (
            <Link
              key={item.href}
              href={item.href}
              className={`flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all ${
                isActive 
                  ? "bg-[#FFFFFF] text-[#1E1E1E] border border-[#E5E5E2] shadow-sm" 
                  : "text-[#8B8D86] hover:bg-[#F4F4F1] hover:text-[#1E1E1E] border border-transparent"
              }`}
            >
              <item.icon size={16} className={isActive ? "text-[#1E1E1E]" : "text-[#8B8D86]"} />
              {item.label}
            </Link>
          );
        })}

        <div className="text-[10px] font-bold text-[#8B8D86] uppercase tracking-widest mb-4 mt-8 px-3">Configuration</div>
        {settingsItems.map((item) => {
          const isActive = pathname === item.href;
          return (
            <Link
              key={item.href}
              href={item.href}
              className={`flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all ${
                isActive 
                  ? "bg-[#FFFFFF] text-[#1E1E1E] border border-[#E5E5E2] shadow-sm" 
                  : "text-[#8B8D86] hover:bg-[#F4F4F1] hover:text-[#1E1E1E] border border-transparent"
              }`}
            >
              <item.icon size={16} className={isActive ? "text-[#1E1E1E]" : "text-[#8B8D86]"} />
              {item.label}
            </Link>
          );
        })}
      </nav>

      <div className="p-5 mx-6 mb-6 bg-white border border-[#E5E5E2] rounded-xl shadow-sm">
        <div className="flex items-center gap-2 mb-2">
          <div className="w-2 h-2 rounded-full bg-[#10b981]" />
          <div className="text-[11px] font-bold uppercase tracking-widest text-[#1E1E1E]">Crosscut Live</div>
        </div>
        <div className="text-xs text-[#8B8D86] leading-relaxed">
          Powered by GitLab Orbit Knowledge Graph.
        </div>
      </div>
    </aside>
  );
}
