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
} from "lucide-react";
import { cn } from "@/lib/utils";

const NAV_ITEMS = [
  { label: "Dashboard", href: "/dashboard", icon: LayoutDashboard },
  { label: "Transactions", href: "/transactions", icon: ArrowLeftRight },
  { label: "Recovery Cases", href: "/recovery-cases", icon: ShieldCheck },
  { label: "Pending Approvals", href: "/approvals", icon: UserCheck },
  { label: "Recovery Simulation", href: "/simulation", icon: PlayCircle },
  { label: "Audit Logs", href: "/audit-logs", icon: FileText },
  { label: "Analytics & ML", href: "/analytics", icon: BarChart3 },
];

export function AppSidebar() {
  const pathname = usePathname();

  return (
    <aside className="w-64 border-r border-border bg-surface flex flex-col shrink-0">
      {/* Brand Header */}
      <div className="h-16 px-6 border-b border-border flex items-center gap-3">
        <div className="w-9 h-9 rounded-lg bg-blue-600 flex items-center justify-center text-white shadow-lg shadow-blue-500/20">
          <Sparkles className="w-5 h-5 text-white" />
        </div>
        <div>
          <div className="flex items-center gap-1.5">
            <span className="font-bold text-base tracking-tight text-white">RecoverAI</span>
            <span className="text-[10px] uppercase font-semibold tracking-wider px-1.5 py-0.5 rounded bg-blue-500/20 text-blue-400 border border-blue-500/30">
              Agent
            </span>
          </div>
          <p className="text-[11px] text-muted">Razorpay Revenue Recovery</p>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-3 py-4 space-y-1">
        {NAV_ITEMS.map((item) => {
          const Icon = item.icon;
          const isActive = pathname === item.href || (item.href !== "/dashboard" && pathname.startsWith(item.href));
          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all",
                isActive
                  ? "bg-blue-600/15 text-blue-400 border border-blue-500/30 shadow-sm"
                  : "text-slate-400 hover:text-slate-200 hover:bg-surfaceHover"
              )}
            >
              <Icon className={cn("w-4 h-4", isActive ? "text-blue-400" : "text-slate-400")} />
              {item.label}
            </Link>
          );
        })}
      </nav>

      {/* Footer info */}
      <div className="p-4 border-t border-border bg-background/50">
        <div className="flex items-center justify-between text-xs text-muted">
          <span>Policy Engine</span>
          <span className="text-emerald-400 font-mono font-medium">v1.2 Active</span>
        </div>
        <div className="flex items-center justify-between text-xs text-muted mt-1.5">
          <span>Adapter Mode</span>
          <span className="text-blue-400 font-mono">Test / Sim</span>
        </div>
      </div>
    </aside>
  );
}
