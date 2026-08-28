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
} from "lucide-react";
import { api } from "@/lib/api-client";
import { formatCurrency, formatDate } from "@/lib/utils";
import { StatusBadge } from "@/components/ui/StatusBadge";

export default function RecoveryCasesPage() {
  const [cases, setCases] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState("");
  const [riskFilter, setRiskFilter] = useState("");

  const fetchCases = async () => {
    try {
      setLoading(true);
      const params = new URLSearchParams();
      if (statusFilter) params.set("status", statusFilter);
      if (riskFilter) params.set("risk_level", riskFilter);

      const res = await api.getRecoveryCases(params.toString());
      setCases(res.items || []);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCases();
  }, [statusFilter, riskFilter]);

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-white">Recovery Cases Pipeline</h1>
          <p className="text-sm text-muted mt-0.5">
            Diagnostic insights, AI proposed strategies, and deterministic policy decisions.
          </p>
        </div>

        <button
          onClick={fetchCases}
          className="px-3.5 py-2 rounded-lg border border-border bg-surface hover:bg-surfaceHover text-slate-300 text-sm font-medium flex items-center gap-2 transition self-start"
        >
          <RefreshCw className={loading ? "w-4 h-4 animate-spin" : "w-4 h-4"} />
          Refresh Pipeline
        </button>
      </div>

      {/* Filters */}
      <div className="p-4 rounded-xl border border-border bg-surface flex items-center gap-3">
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          className="bg-background border border-border rounded-lg px-3 py-2 text-sm text-slate-300 focus:outline-none focus:border-blue-500"
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
          className="bg-background border border-border rounded-lg px-3 py-2 text-sm text-slate-300 focus:outline-none focus:border-blue-500"
        >
          <option value="">All Risk Levels</option>
          <option value="HIGH">HIGH RISK</option>
          <option value="MEDIUM">MEDIUM RISK</option>
          <option value="LOW">LOW RISK</option>
        </select>
      </div>

      {/* Cases Table */}
      <div className="rounded-xl border border-border bg-surface overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead className="bg-surfaceHover/60 text-muted uppercase text-[11px] font-semibold border-b border-border">
              <tr>
                <th className="px-5 py-3.5">Case ID</th>
                <th className="px-5 py-3.5">Customer & Amount</th>
                <th className="px-5 py-3.5">Risk Level</th>
                <th className="px-5 py-3.5">AI Diagnosis</th>
                <th className="px-5 py-3.5">Strategy</th>
                <th className="px-5 py-3.5">AI Confidence</th>
                <th className="px-5 py-3.5">Status</th>
                <th className="px-5 py-3.5 text-right">Details</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {cases.length === 0 ? (
                <tr>
                  <td colSpan={8} className="px-5 py-12 text-center text-muted">
                    No recovery cases found.
                  </td>
                </tr>
              ) : (
                cases.map((c) => (
                  <tr key={c.id} className="hover:bg-surfaceHover/40 transition">
                    <td className="px-5 py-3.5 font-mono text-xs font-medium text-white">
                      {c.id}
                    </td>
                    <td className="px-5 py-3.5">
                      <div className="font-semibold text-white">
                        {formatCurrency(c.transaction_amount || 0)}
                      </div>
                      <div className="text-[11px] text-muted">{c.customer_name}</div>
                    </td>
                    <td className="px-5 py-3.5">
                      <StatusBadge status={c.risk_level} size="sm" />
                    </td>
                    <td className="px-5 py-3.5 text-xs text-slate-300 max-w-[280px] truncate">
                      {c.diagnosis || "Awaiting diagnosis"}
                    </td>
                    <td className="px-5 py-3.5">
                      {c.recommended_action ? (
                        <span className="font-mono text-xs text-blue-400 bg-blue-950/40 px-2 py-0.5 rounded border border-blue-800/40">
                          {c.recommended_action}
                        </span>
                      ) : (
                        "-"
                      )}
                    </td>
                    <td className="px-5 py-3.5 font-mono text-xs text-slate-300">
                      {c.confidence ? `${(c.confidence * 100).toFixed(0)}%` : "-"}
                    </td>
                    <td className="px-5 py-3.5">
                      <StatusBadge status={c.status} size="sm" />
                    </td>
                    <td className="px-5 py-3.5 text-right">
                      <Link
                        href={`/recovery-cases/${c.id}`}
                        className="inline-flex items-center gap-1 px-2.5 py-1 rounded bg-surfaceHover hover:bg-blue-600/20 text-blue-400 hover:text-blue-300 text-xs font-medium border border-border hover:border-blue-500/40 transition"
                      >
                        <span>Inspect</span>
                        <ArrowRight className="w-3 h-3" />
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
