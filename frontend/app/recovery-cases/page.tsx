"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import {
  ShieldCheck,
  Search,
  Filter,
  ExternalLink,
  RefreshCw,
  Sparkles,
  ArrowRight,
  GitBranch,
  SlidersHorizontal,
} from "lucide-react";
import { api } from "@/lib/api-client";
import { formatCurrency, formatDate } from "@/lib/utils";
import { StatusBadge } from "@/components/ui/StatusBadge";

export default function RecoveryCasesPage() {
  const [cases, setCases] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [statusFilter, setStatusFilter] = useState("");
  const [riskFilter, setRiskFilter] = useState("");

  const fetchCases = async (isManual = false) => {
    try {
      if (isManual) setIsRefreshing(true);
      else setLoading(true);
      const params = new URLSearchParams();
      if (statusFilter) params.set("status", statusFilter);
      if (riskFilter) params.set("risk_level", riskFilter);

      const res = await api.getRecoveryCases(params.toString());
      setCases(res.items || []);
    } catch (err) {
      console.error("Failed to fetch recovery cases:", err);
    } finally {
      setLoading(false);
      setIsRefreshing(false);
    }
  };

  useEffect(() => {
    fetchCases();
  }, [statusFilter, riskFilter]);

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-2 border-b border-border/40">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[11px] font-medium bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
              <GitBranch className="w-3 h-3 text-emerald-400" />
              POLICY-BOUND PIPELINE
            </span>
            <span className="text-xs text-muted font-mono">{cases.length} active cases</span>
          </div>
          <h1 className="text-2xl lg:text-3xl font-bold tracking-tight text-white">Recovery Cases Pipeline</h1>
          <p className="text-sm text-muted mt-0.5">
            AI diagnostic recommendations evaluated against deterministic merchant policy guardrails.
          </p>
        </div>

        <button
          onClick={() => fetchCases(true)}
          disabled={isRefreshing || loading}
          className="px-3.5 py-2 rounded-xl border border-borderSubtle bg-surfaceSubtle hover:bg-surfaceHover text-slate-300 text-sm font-medium flex items-center gap-2 transition duration-150 active:scale-[0.98] disabled:opacity-50 self-start focus-ring"
        >
          <RefreshCw className={`w-4 h-4 text-slate-400 ${isRefreshing ? "animate-spin text-primary" : ""}`} />
          <span>{isRefreshing ? "Updating..." : "Refresh Pipeline"}</span>
        </button>
      </div>

      {/* Filters */}
      <div className="fintech-card p-4 flex flex-wrap items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2 text-xs text-muted">
            <SlidersHorizontal className="w-3.5 h-3.5" />
            <span>Filter Cases:</span>
          </div>

          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="bg-slate-950/60 border border-borderSubtle rounded-xl px-3 py-2 text-sm text-slate-300 focus-ring transition duration-150 cursor-pointer"
          >
            <option value="">All Pipeline Statuses</option>
            <option value="RECOVERED">RECOVERED</option>
            <option value="WAITING_APPROVAL">WAITING_APPROVAL</option>
            <option value="SCHEDULED">SCHEDULED</option>
            <option value="EXECUTING">EXECUTING</option>
            <option value="STOPPED">STOPPED</option>
            <option value="OPEN">OPEN</option>
          </select>

          <select
            value={riskFilter}
            onChange={(e) => setRiskFilter(e.target.value)}
            className="bg-slate-950/60 border border-borderSubtle rounded-xl px-3 py-2 text-sm text-slate-300 focus-ring transition duration-150 cursor-pointer"
          >
            <option value="">All Risk Levels</option>
            <option value="HIGH">HIGH RISK</option>
            <option value="MEDIUM">MEDIUM RISK</option>
            <option value="LOW">LOW RISK</option>
          </select>
        </div>
      </div>

      {/* Cases Table */}
      <div className="fintech-card overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead className="bg-surfaceSubtle/80 text-muted uppercase text-[10px] font-mono tracking-wider border-b border-borderSubtle">
              <tr>
                <th className="px-5 py-3.5">Case ID</th>
                <th className="px-5 py-3.5">Customer & Amount</th>
                <th className="px-5 py-3.5">Risk Level</th>
                <th className="px-5 py-3.5">AI Diagnosis</th>
                <th className="px-5 py-3.5">Proposed Strategy</th>
                <th className="px-5 py-3.5">AI Confidence</th>
                <th className="px-5 py-3.5">Pipeline Status</th>
                <th className="px-5 py-3.5 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-borderSubtle">
              {loading && cases.length === 0 ? (
                <tr>
                  <td colSpan={8} className="px-5 py-16 text-center text-muted">
                    <div className="flex flex-col items-center justify-center gap-2">
                      <RefreshCw className="w-6 h-6 text-primary animate-spin" />
                      <span className="text-xs text-slate-400">Loading pipeline cases...</span>
                    </div>
                  </td>
                </tr>
              ) : cases.length === 0 ? (
                <tr>
                  <td colSpan={8} className="px-5 py-16 text-center text-muted">
                    <div className="flex flex-col items-center justify-center gap-1.5">
                      <p className="text-sm font-medium text-slate-300">No recovery cases found</p>
                      <p className="text-xs text-slate-500">Cases will populate automatically upon payment failures</p>
                    </div>
                  </td>
                </tr>
              ) : (
                cases.map((c) => (
                  <tr key={c.id} className="hover:bg-surfaceSubtle/50 transition-colors group">
                    <td className="px-5 py-3.5 font-mono text-xs font-medium text-white">
                      <span className="group-hover:text-primary transition-colors">{c.id}</span>
                    </td>
                    <td className="px-5 py-3.5">
                      <div className="font-semibold text-white tabular-nums">
                        {formatCurrency(c.transaction_amount || 0)}
                      </div>
                      <div className="text-[11px] text-muted">{c.customer_name || "Customer"}</div>
                    </td>
                    <td className="px-5 py-3.5">
                      <StatusBadge status={c.risk_level} size="sm" />
                    </td>
                    <td className="px-5 py-3.5 text-xs text-slate-300 max-w-[280px] truncate">
                      {c.diagnosis || <span className="text-slate-500 italic">Awaiting AI diagnosis</span>}
                    </td>
                    <td className="px-5 py-3.5">
                      {c.recommended_action ? (
                        <span className="font-mono text-xs text-primary-light bg-primary/10 px-2 py-0.5 rounded-md border border-primary/20">
                          {c.recommended_action}
                        </span>
                      ) : (
                        <span className="text-slate-600 font-mono">-</span>
                      )}
                    </td>
                    <td className="px-5 py-3.5 font-mono text-xs text-slate-300">
                      {c.confidence ? `${(c.confidence * 100).toFixed(0)}%` : <span className="text-slate-600">-</span>}
                    </td>
                    <td className="px-5 py-3.5">
                      <StatusBadge status={c.status} size="sm" />
                    </td>
                    <td className="px-5 py-3.5 text-right">
                      <Link
                        href={`/recovery-cases/${c.id}`}
                        className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-surfaceSubtle hover:bg-primary/15 text-slate-300 hover:text-white text-xs font-medium border border-borderSubtle hover:border-primary/40 transition active:scale-[0.98]"
                      >
                        <span>Inspect</span>
                        <ArrowRight className="w-3 h-3 text-slate-400 group-hover:text-primary" />
                      </Link>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
