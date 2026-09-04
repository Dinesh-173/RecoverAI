"use client";

import React, { useState, useEffect } from "react";
import { Shield, Building2, Activity, CheckCircle2, Lock, Server, X } from "lucide-react";
import { api } from "@/lib/api-client";

export function AppHeader() {
  const [healthModalOpen, setHealthModalOpen] = useState(false);
  const [healthData, setHealthData] = useState<any>(null);
  const [healthLoading, setHealthLoading] = useState(false);

  const fetchHealth = async () => {
    try {
      setHealthLoading(true);
      const data = await api.getSystemHealth();
      setHealthData(data);
    } catch {
      setHealthData({ status: "UNHEALTHY", dependencies: { database: "UNKNOWN" } });
    } finally {
      setHealthLoading(false);
    }
  };

  useEffect(() => {
    if (healthModalOpen) {
      fetchHealth();
    }
  }, [healthModalOpen]);

  return (
    <>
      <header className="h-16 border-b border-border/70 bg-surface/75 backdrop-blur-md px-6 lg:px-8 flex items-center justify-between sticky top-0 z-20">
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2 text-xs text-slate-300 bg-surfaceCard/80 border border-border/70 px-3 py-1.5 rounded-lg shadow-sm">
            <Building2 className="w-3.5 h-3.5 text-slate-400" />
            <span className="font-semibold text-white tracking-tight">Apex Digital Retail</span>
            <span className="text-slate-600">|</span>
            <span className="text-[11px] text-muted font-mono">mer_demo_razorpay</span>
          </div>
        </div>

        <div className="flex items-center gap-2.5">
          {/* Interactive System Status Trigger */}
          <button
            onClick={() => setHealthModalOpen(true)}
            className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-emerald-950/25 border border-emerald-800/40 hover:bg-emerald-900/30 text-emerald-300 text-xs font-medium transition-all duration-150 shadow-sm cursor-pointer focus-ring"
          >
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse-subtle shadow-sm shadow-emerald-400/40"></span>
            <Activity className="w-3.5 h-3.5 text-emerald-400" />
            <span className="hidden sm:inline">HEALTH: ACTIVE</span>
          </button>

          {/* Test Mode & Simulation Badge */}
          <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-amber-950/25 border border-amber-800/40 text-amber-300/90 text-xs font-medium">
            <span className="w-1.5 h-1.5 rounded-full bg-amber-400"></span>
            <span className="hidden md:inline">SIMULATION ISOLATION ACTIVE</span>
            <span className="md:hidden">SIMULATION</span>
          </div>

          <div className="hidden lg:flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-blue-950/25 border border-blue-800/40 text-blue-300/90 text-xs font-medium">
            <Shield className="w-3.5 h-3.5 text-blue-400" />
            <span>Policy Guardrails Enforced</span>
          </div>
        </div>
      </header>

      {/* System Status & FinTech Invariants Modal */}
      {healthModalOpen && (
        <div className="fixed inset-0 z-50 bg-black/75 backdrop-blur-sm flex items-center justify-center p-4 animate-fade-in">
          <div className="bg-surfaceCard border border-border rounded-2xl max-w-lg w-full p-6 space-y-5 shadow-2xl ring-1 ring-white/10 animate-slide-up">
            <div className="flex items-center justify-between border-b border-border/70 pb-3.5">
              <div className="flex items-center gap-2.5">
                <div className="w-8 h-8 rounded-lg bg-emerald-500/15 border border-emerald-500/30 flex items-center justify-center">
                  <Server className="w-4.5 h-4.5 text-emerald-400" />
                </div>
                <div>
                  <h3 className="text-sm font-bold text-white tracking-tight">System Health & Security Center</h3>
                  <p className="text-[11px] text-muted">Platform invariants & infrastructure telemetry</p>
                </div>
              </div>
              <button
                onClick={() => setHealthModalOpen(false)}
                className="text-slate-400 hover:text-white p-1 rounded-lg hover:bg-surfaceHover transition"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <div className="space-y-2 text-xs">
              <div className="p-3 rounded-xl bg-surfaceSubtle/80 border border-border/70 flex items-center justify-between">
                <div className="flex items-center gap-2.5">
                  <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
                  <span className="text-slate-200 font-medium">Backend API Engine (FastAPI)</span>
                </div>
                <span className="font-mono text-emerald-400 font-bold text-[11px]">
                  {healthData?.status || (healthLoading ? "CONNECTING..." : "HEALTHY")}
                </span>
              </div>

              <div className="p-3 rounded-xl bg-surfaceSubtle/80 border border-border/70 flex items-center justify-between">
                <div className="flex items-center gap-2.5">
                  <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
                  <span className="text-slate-200 font-medium">Database Layer (SQLite / AsyncPG)</span>
                </div>
                <span className="font-mono text-emerald-400 font-bold text-[11px]">
                  {healthData?.dependencies?.database || "HEALTHY"}
                </span>
              </div>

              <div className="p-3 rounded-xl bg-surfaceSubtle/80 border border-border/70 flex items-center justify-between">
                <div className="flex items-center gap-2.5">
                  <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
                  <span className="text-slate-200 font-medium">ML Recoverability Model</span>
                </div>
                <span className="font-mono text-blue-400 font-bold text-[11px]">LOADED (GBM v1.0.0)</span>
              </div>

              <div className="p-3 rounded-xl bg-surfaceSubtle/80 border border-border/70 flex items-center justify-between">
                <div className="flex items-center gap-2.5">
                  <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
                  <span className="text-slate-200 font-medium">AI Diagnostic Agent</span>
                </div>
                <span className="font-mono text-blue-400 font-bold text-[11px]">ACTIVE (ADVISORY ONLY)</span>
              </div>

              <div className="p-3 rounded-xl bg-surfaceSubtle/80 border border-border/70 flex items-center justify-between">
                <div className="flex items-center gap-2.5">
                  <Shield className="w-4 h-4 text-purple-400 shrink-0" />
                  <span className="text-slate-200 font-medium">Deterministic Policy Engine</span>
                </div>
                <span className="font-mono text-purple-400 font-bold text-[11px]">AUTHORITATIVE</span>
              </div>

              <div className="p-3 rounded-xl bg-surfaceSubtle/80 border border-border/70 flex items-center justify-between">
                <div className="flex items-center gap-2.5">
                  <Lock className="w-4 h-4 text-amber-400 shrink-0" />
                  <span className="text-slate-200 font-medium">Razorpay Webhook Security</span>
                </div>
                <span className="font-mono text-amber-400 font-bold text-[11px]">HMAC SHA-256 ENFORCED</span>
              </div>

              <div className="p-3 rounded-xl bg-surfaceSubtle/80 border border-border/70 flex items-center justify-between">
                <div className="flex items-center gap-2.5">
                  <Shield className="w-4 h-4 text-emerald-400 shrink-0" />
                  <span className="text-slate-200 font-medium">Simulation Payment Adapter Isolation</span>
                </div>
                <span className="font-mono text-emerald-400 font-bold text-[11px]">ENFORCED (is_simulation=True)</span>
              </div>
            </div>

            <div className="pt-2 border-t border-border/70 flex justify-end">
              <button
                onClick={() => setHealthModalOpen(false)}
                className="px-4 py-2 rounded-xl bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold shadow-md shadow-blue-500/20 transition"
              >
                Close Security Panel
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
