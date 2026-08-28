"use client";

import React from "react";
import { Shield, Sparkles, Building2 } from "lucide-react";

export function AppHeader() {
  return (
    <header className="h-16 border-b border-border bg-surface/50 backdrop-blur px-8 flex items-center justify-between sticky top-0 z-10">
      <div className="flex items-center gap-4">
        <div className="flex items-center gap-2 text-sm text-slate-300">
          <Building2 className="w-4 h-4 text-slate-400" />
          <span className="font-semibold text-white">Apex Digital Retail</span>
          <span className="text-slate-500">|</span>
          <span className="text-xs text-muted">Merchant ID: mer_apex_digital_01</span>
        </div>
      </div>

      <div className="flex items-center gap-3">
        {/* Clearly labeled Test Mode Badge */}
        <div className="flex items-center gap-2 px-3 py-1 rounded-full bg-amber-950/40 border border-amber-800/60 text-amber-300 text-xs font-medium">
          <span className="w-2 h-2 rounded-full bg-amber-400 animate-pulse"></span>
          <span>RAZORPAY TEST MODE & SIMULATION</span>
        </div>

        <div className="flex items-center gap-1.5 px-3 py-1 rounded-full bg-blue-950/40 border border-blue-800/60 text-blue-300 text-xs font-medium">
          <Shield className="w-3.5 h-3.5 text-blue-400" />
          <span>Policy Guardrails Enforced</span>
        </div>
      </div>
    </header>
  );
}
