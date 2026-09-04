"use client";

import React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  ArrowLeftRight,
  ShieldCheck,
  UserCheck,
  PlayCircle,
  FileText,
  BarChart3,
  Sparkles,
  ChevronRight,
  Shield,
  Activity,
} from "lucide-react";
import { cn } from "@/lib/utils";

const NAV_GROUPS = [
  {
    title: "CORE",
    items: [
      { label: "Overview", href: "/dashboard", icon: LayoutDashboard },
      { label: "Transactions", href: "/transactions", icon: ArrowLeftRight },
      { label: "Recovery Cases", href: "/recovery-cases", icon: ShieldCheck },
    ],
  },
  {
    title: "OPERATIONS",
    items: [
      { label: "Pending Approvals", href: "/approvals", icon: UserCheck },
      { label: "Simulation Sandbox", href: "/simulation", icon: PlayCircle },
    ],
  },
  {
    title: "INTELLIGENCE",
    items: [
      { label: "Analytics & ML", href: "/analytics", icon: BarChart3 },
      { label: "Audit Ledger", href: "/audit-logs", icon: FileText },
    ],
  },
];

export function AppSidebar() {
  const pathname = usePathname();

  return (
    <aside className="w-64 border-r border-border/80 bg-surface flex flex-col shrink-0 select-none">
      {/* Brand Header */}
      <div className="h-16 px-5 border-b border-border/70 flex items-center gap-3">
        <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-blue-600 to-indigo-600 flex items-center justify-center text-white shadow-md shadow-blue-500/20 ring-1 ring-white/15">
          <Sparkles className="w-4.5 h-4.5 text-white" />
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-1.5">
            <span className="font-bold text-sm tracking-tight text-white">RecoverAI</span>
            <span className="text-[10px] uppercase font-bold tracking-wider px-1.5 py-0.5 rounded-full bg-blue-500/15 text-blue-400 border border-blue-500/30">
              Agent
            </span>
          </div>
          <p className="text-[11px] text-muted truncate font-medium">Revenue Recovery Engine</p>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-3 py-4 space-y-5 overflow-y-auto">
        {NAV_GROUPS.map((group) => (
          <div key={group.title} className="space-y-1">
            <div className="px-3 pb-1 text-[10px] font-bold uppercase tracking-wider text-slate-500">
              {group.title}
            </div>
            {group.items.map((item) => {
              const Icon = item.icon;
              const isActive =
                pathname === item.href ||
                (item.href !== "/dashboard" && pathname.startsWith(item.href));
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={cn(
                    "group flex items-center justify-between px-3 py-2 rounded-lg text-xs font-medium transition-all duration-150 focus-ring",
                    isActive
                      ? "bg-blue-600/10 text-blue-400 border border-blue-500/25 shadow-sm font-semibold"
                      : "text-slate-400 hover:text-slate-200 hover:bg-white/[0.03] border border-transparent"
                  )}
                >
                  <div className="flex items-center gap-2.5 min-w-0">
                    <Icon
                      className={cn(
                        "w-4 h-4 transition-colors shrink-0",
                        isActive ? "text-blue-400" : "text-slate-400 group-hover:text-slate-200"
                      )}
                    />
                    <span className="truncate">{item.label}</span>
                  </div>
                  {isActive && (
                    <span className="w-1.5 h-1.5 rounded-full bg-blue-400 shrink-0 shadow-sm shadow-blue-400/40" />
                  )}
                </Link>
              );
            })}
          </div>
        ))}
      </nav>

      {/* Footer Info */}
      <div className="p-3.5 border-t border-border/70 bg-surfaceSubtle/60 space-y-2">
        <div className="flex items-center justify-between text-[11px] text-muted">
          <span className="flex items-center gap-1.5">
            <Shield className="w-3 h-3 text-emerald-400" />
            <span>Policy Engine</span>
          </span>
          <span className="text-emerald-400 font-mono font-medium text-[10px]">v1.2 Active</span>
        </div>
        <div className="flex items-center justify-between text-[11px] text-muted">
          <span className="flex items-center gap-1.5">
            <Activity className="w-3 h-3 text-blue-400" />
            <span>Adapter Mode</span>
          </span>
          <span className="text-blue-400 font-mono text-[10px]">Test / Sim</span>
        </div>
      </div>
    </aside>
  );
}
