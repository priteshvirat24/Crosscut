"use client";

import Link from "next/link";
import { cn } from "@/lib/utils";
import { usePathname } from "next/navigation";
import { Database } from "lucide-react";

export function Header() {
  const pathname = usePathname();

  const links = [
    { name: "Features", href: "/#features" },
    { name: "How It Works", href: "/#how-it-works" },
    { name: "Docs", href: "/docs" },
  ];

  return (
    <header className="fixed top-0 left-0 right-0 z-50 flex items-center justify-between px-8 lg:px-12 h-16 bg-white border-b border-[#E5E5E2]">
      <div className="flex items-center gap-12">
        <Link href="/" className="flex items-center gap-3">
          <div className="w-8 h-8 bg-[#1E1E1E] rounded flex items-center justify-center">
            <span className="text-white font-bold text-sm">C</span>
          </div>
          <div className="text-[#1E1E1E] font-bold text-lg tracking-tight">Crosscut</div>
        </Link>

        <nav className="hidden md:flex items-center gap-2">
          {links.map((link) => (
            <Link
              key={link.name}
              href={link.href}
              className="text-sm font-medium text-[#8B8D86] hover:text-[#1E1E1E] px-3 py-1.5 rounded transition-colors"
            >
              {link.name}
            </Link>
          ))}
          <Link
            href="/dashboard"
            className={cn(
              "text-sm font-medium px-3 py-1.5 rounded transition-colors",
              pathname.startsWith("/dashboard") 
                ? "bg-[#F4F4F1] text-[#1E1E1E] border border-[#E5E5E2]" 
                : "text-[#8B8D86] hover:text-[#1E1E1E]"
            )}
          >
            Dashboard
          </Link>
        </nav>
      </div>

      <div className="flex items-center gap-6">
        {/* Orbit Mode Indicator */}
        <div className="hidden lg:flex items-center gap-2 px-3 py-1 rounded bg-[#F4F4F1] border border-[#E5E5E2]">
          <Database size={12} className="text-[#C68A3A]" />
          <span className="text-[10px] font-bold text-[#8B8D86] uppercase tracking-widest">Orbit Remote</span>
        </div>

        <Link
          href="/run"
          className="button-primary text-xs px-5 h-9"
        >
          Run Judge Mode
        </Link>
      </div>
    </header>
  );
}
