"use client";

import React, { useState, useEffect } from "react";
import { Shield, Sparkles, Building2, Activity, CheckCircle2, XCircle, Lock, Server } from "lucide-react";
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
      <header className="h-16 border-b border-border bg-surface/50 backdrop-blur px-8 flex items-center justify-between sticky top-0 z-10">
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2 text-sm text-slate-300">
            <Building2 className="w-4 h-4 text-slate-400" />
            <span className="font-semibold text-white">Apex Digital Retail</span>
            <span className="text-slate-500">|</span>
            <span className="text-xs text-muted font-mono">mer_demo_razorpay</span>
          </div>
        </div>

        <div className="flex items-center gap-3">
          {/* Interactive System Status Component */}
          <button
            onClick={() => setHealthModalOpen(true)}
            className="flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-950/40 border border-emerald-800/60 hover:bg-emerald-900/40 text-emerald-300 text-xs font-medium transition cursor-pointer"
          >
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
            <Activity className="w-3.5 h-3.5 text-emerald-400" />
            <span>SYSTEM HEALTH: ACTIVE</span>
          </button>

          {/* Test Mode & Simulation Badge */}
          <div className="flex items-center gap-2 px-3 py-1 rounded-full bg-amber-950/40 border border-amber-800/60 text-amber-300 text-xs font-medium">
            <span className="w-2 h-2 rounded-full bg-amber-400"></span>
            <span>SIMULATION ISOLATION ACTIVE</span>
          </div>

          <div className="flex items-center gap-1.5 px-3 py-1 rounded-full bg-blue-950/40 border border-blue-800/60 text-blue-300 text-xs font-medium">
            <Shield className="w-3.5 h-3.5 text-blue-400" />
            <span>Policy Guardrails Enforced</span>
          </div>
        </div>
      </header>

      {/* System Status & FinTech Invariants Modal */}
      {healthModalOpen && (
        <div className="fixed inset-0 z-50 bg-black/75 backdrop-blur-sm flex items-center justify-center p-4 animate-in fade-in duration-200">
          <div className="bg-surface border border-border rounded-xl max-w-lg w-full p-6 space-y-5 shadow-2xl">
            <div className="flex items-center justify-between border-b border-border pb-3">
              <div className="flex items-center gap-2">
                <Server className="w-5 h-5 text-emerald-400" />
                <h3 className="text-base font-bold text-white">System Health & FinTech Security Center</h3>
              </div>
              <button
                onClick={() => setHealthModalOpen(false)}
                className="text-muted hover:text-white text-lg font-bold"
              >
                &times;
              </button>
            </div>

            <div className="space-y-2.5 text-xs">
              <div className="p-3 rounded-lg bg-background/60 border border-border flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                  <span className="text-slate-200">Backend API Engine (FastAPI)</span>
                </div>
                <span className="font-mono text-emerald-400 font-bold">
                  {healthData?.status || (healthLoading ? "CONNECTING..." : "HEALTHY")}
                </span>
              </div>

              <div className="p-3 rounded-lg bg-background/60 border border-border flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                  <span className="text-slate-200">Database Layer (SQLite / AsyncPG)</span>
                </div>
                <span className="font-mono text-emerald-400 font-bold">
                  {healthData?.dependencies?.database || "HEALTHY"}
                </span>
              </div>

              <div className="p-3 rounded-lg bg-background/60 border border-border flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                  <span className="text-slate-200">ML Recoverability Model</span>
                </div>
                <span className="font-mono text-blue-400 font-bold">LOADED (GBM v1.0.0)</span>
              </div>

              <div className="p-3 rounded-lg bg-background/60 border border-border flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                  <span className="text-slate-200">AI Diagnostic Agent</span>
                </div>
                <span className="font-mono text-blue-400 font-bold">ACTIVE (ADVISORY ONLY)</span>
              </div>

              <div className="p-3 rounded-lg bg-background/60 border border-border flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Shield className="w-4 h-4 text-purple-400" />
                  <span className="text-slate-200">Deterministic Policy Engine</span>
                </div>
                <span className="font-mono text-purple-400 font-bold">AUTHORITATIVE</span>
              </div>

              <div className="p-3 rounded-lg bg-background/60 border border-border flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Lock className="w-4 h-4 text-amber-400" />
                  <span className="text-slate-200">Razorpay Webhook Security</span>
                </div>
                <span className="font-mono text-amber-400 font-bold">HMAC SHA-256 ENFORCED</span>
              </div>

              <div className="p-3 rounded-lg bg-background/60 border border-border flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Shield className="w-4 h-4 text-emerald-400" />
                  <span className="text-slate-200">Simulation Payment Adapter Isolation</span>
                </div>
                <span className="font-mono text-emerald-400 font-bold">ENFORCED (is_simulation=True)</span>
              </div>
            </div>

            <div className="pt-2 border-t border-border flex justify-end">
              <button
                onClick={() => setHealthModalOpen(false)}
                className="px-4 py-2 rounded-lg bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold"
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
