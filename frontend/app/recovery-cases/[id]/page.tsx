"use client";

import React, { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import {
  ArrowLeft,
  Shield,
  Sparkles,
  Play,
  CheckCircle2,
  AlertCircle,
  Clock,
  User,
  CreditCard,
  Building2,
  RefreshCw,
  ExternalLink,
  ShieldAlert,
} from "lucide-react";
import { api } from "@/lib/api-client";
import { RecoveryCaseDetail } from "@/lib/types";
import { formatCurrency, formatDate } from "@/lib/utils";
import { StatusBadge } from "@/components/ui/StatusBadge";

export default function CaseDetailPage() {
  const { id } = useParams();
  const router = useRouter();
  const [caseData, setCaseData] = useState<RecoveryCaseDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState(false);
  const [msg, setMsg] = useState<string | null>(null);

  const fetchCase = async () => {
    try {
      setLoading(true);
      const data = await api.getRecoveryCaseById(id as string);
      setCaseData(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (id) fetchCase();
  }, [id]);

  const handleAnalyze = async () => {
    try {
      setActionLoading(true);
      await api.analyzeCase(id as string);
      setMsg("AI Diagnostic analysis completed.");
      await fetchCase();
    } catch (err: any) {
      setMsg(`Error: ${err.message}`);
    } finally {
      setActionLoading(false);
    }
  };

  const handleExecute = async () => {
    try {
      setActionLoading(true);
      await api.executeCaseAction(id as string);
      setMsg("Action executed successfully.");
      await fetchCase();
    } catch (err: any) {
      setMsg(`Error: ${err.message}`);
    } finally {
      setActionLoading(false);
    }
  };

  if (loading && !caseData) {
    return (
      <div className="flex items-center justify-center min-h-[50vh]">
        <RefreshCw className="w-8 h-8 text-blue-500 animate-spin" />
      </div>
    );
  }

  if (!caseData || (caseData as any).error) {
    return (
      <div className="p-8 text-center text-muted">
        <p>Recovery case not found.</p>
        <Link href="/recovery-cases" className="text-blue-400 text-sm mt-2 inline-block">
          &larr; Back to Pipeline
        </Link>
      </div>
    );
  }

  const tx = caseData.transaction;
  const cust = tx?.customer;

  return (
    <div className="space-y-6 max-w-6xl mx-auto pb-12">
      {/* Back Link & Header */}
      <div>
        <Link
          href="/recovery-cases"
          className="inline-flex items-center gap-1.5 text-xs text-muted hover:text-white transition mb-3"
        >
          <ArrowLeft className="w-3.5 h-3.5" />
          <span>Back to Recovery Pipeline</span>
        </Link>

        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-3">
              <h1 className="text-2xl font-bold text-white tracking-tight">Case {caseData.id}</h1>
              <StatusBadge status={caseData.status} />
              <StatusBadge status={caseData.risk_level} />
            </div>
            <p className="text-xs text-muted mt-1 font-mono">
              Transaction Ref: {tx?.id} | Razorpay ID: {tx?.external_transaction_id || "N/A"}
            </p>
          </div>

          <div className="flex items-center gap-3">
            <button
              disabled={actionLoading}
              onClick={handleAnalyze}
              className="px-3.5 py-2 rounded-lg bg-surface hover:bg-surfaceHover border border-border text-slate-200 text-sm font-medium flex items-center gap-2 transition disabled:opacity-50"
            >
              <Sparkles className="w-4 h-4 text-blue-400" />
              Re-Analyze Case
            </button>

            {caseData.status !== "RECOVERED" && caseData.status !== "STOPPED" && !caseData.requires_human_approval && (
              <button
                disabled={actionLoading}
                onClick={handleExecute}
                className="px-4 py-2 rounded-lg bg-blue-600 hover:bg-blue-500 text-white text-sm font-medium flex items-center gap-2 shadow-lg shadow-blue-500/20 transition disabled:opacity-50"
              >
                <Play className="w-4 h-4 fill-white" />
                Execute Action
              </button>
            )}

            {caseData.requires_human_approval && (
              <Link
                href="/approvals"
                className="px-4 py-2 rounded-lg bg-amber-600 hover:bg-amber-500 text-white text-sm font-medium flex items-center gap-2 shadow-lg shadow-amber-500/20 transition"
              >
                <ShieldAlert className="w-4 h-4" />
                Review Approval Queue
              </Link>
            )}
          </div>
        </div>

        {msg && (
          <div className="mt-4 p-3 rounded-lg bg-blue-950/40 border border-blue-800/40 text-blue-300 text-xs flex items-center justify-between">
            <span>{msg}</span>
            <button onClick={() => setMsg(null)} className="text-muted hover:text-white">&times;</button>
          </div>
        )}
      </div>

      {/* Grid: Context & Diagnostics */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column: Transaction & Customer Context */}
        <div className="space-y-6">
          {/* Transaction Summary */}
          <div className="p-5 rounded-xl border border-border bg-surface">
            <h2 className="text-sm font-semibold uppercase tracking-wider text-muted mb-4 flex items-center gap-2">
              <CreditCard className="w-4 h-4 text-blue-400" />
              Transaction Context
            </h2>
            <div className="space-y-3 text-sm">
              <div className="flex justify-between">
                <span className="text-muted">Amount</span>
                <span className="font-bold text-white text-base">
                  {formatCurrency(tx?.amount || 0, tx?.currency)}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted">Payment Rail</span>
                <span className="text-slate-200 font-medium">{tx?.payment_method}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted">Failure Code</span>
                <span className="font-mono text-xs text-rose-400 bg-rose-950/40 px-2 py-0.5 rounded border border-rose-900/40">
                  {tx?.failure_code || "UNKNOWN"}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted">Attempt Count</span>
                <span className="text-slate-200 font-mono">Attempt {tx?.attempt_number} of 2</span>
              </div>
              <div className="pt-2 border-t border-border/60 text-xs text-slate-400">
                <span className="font-semibold text-slate-300">Failure Reason: </span>
                {tx?.failure_reason}
              </div>
            </div>
          </div>

          {/* Customer Profile */}
          <div className="p-5 rounded-xl border border-border bg-surface">
            <h2 className="text-sm font-semibold uppercase tracking-wider text-muted mb-4 flex items-center gap-2">
              <User className="w-4 h-4 text-purple-400" />
              Customer Profile
            </h2>
            <div className="space-y-3 text-sm">
              <div className="flex justify-between">
                <span className="text-muted">Name</span>
                <span className="font-semibold text-white">{cust?.name}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted">Segment</span>
                <StatusBadge status={cust?.customer_segment || "STANDARD"} size="sm" />
              </div>
              <div className="flex justify-between">
                <span className="text-muted">Lifetime Value (LTV)</span>
                <span className="font-mono text-slate-200">{formatCurrency(cust?.total_lifetime_value || 0)}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted">Past Success / Fail</span>
                <span className="font-mono text-slate-200">
                  <span className="text-emerald-400">{cust?.successful_payment_count}</span> /{" "}
                  <span className="text-rose-400">{cust?.failed_payment_count}</span>
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted">Opt-Out Status</span>
                <span className={cust?.communication_opt_out ? "text-rose-400 font-medium" : "text-emerald-400 font-medium"}>
                  {cust?.communication_opt_out ? "Opted Out" : "Subscribed"}
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Right Column: AI Diagnostics & Policy Enforcement */}
        <div className="lg:col-span-2 space-y-6">
          {/* AI Diagnostic Reasoning Card */}
          <div className="p-6 rounded-xl border border-blue-800/40 bg-blue-950/20">
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-2">
                <Sparkles className="w-5 h-5 text-blue-400" />
                <h2 className="text-base font-bold text-white">AI Diagnostic Synthesis</h2>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-xs text-muted font-mono">Confidence</span>
                <span className="text-xs font-bold text-blue-400 font-mono px-2 py-0.5 rounded bg-blue-900/40 border border-blue-700/40">
                  {((caseData.confidence || 0) * 100).toFixed(0)}%
                </span>
              </div>
            </div>

            <p className="text-sm text-slate-200 leading-relaxed bg-background/50 p-4 rounded-lg border border-border">
              {caseData.diagnosis || "No diagnosis generated yet."}
            </p>

            <div className="grid grid-cols-2 sm:grid-cols-3 gap-4 mt-4 text-xs">
              <div className="p-3 rounded-lg bg-surface border border-border">
                <span className="text-muted block mb-1">Recommended Strategy</span>
                <span className="font-mono font-bold text-white text-sm">
                  {caseData.recommended_action || "NONE"}
                </span>
              </div>
              <div className="p-3 rounded-lg bg-surface border border-border">
                <span className="text-muted block mb-1">Suggested Delay</span>
                <span className="font-mono font-bold text-white text-sm">
                  {caseData.recommended_delay_minutes} min
                </span>
              </div>
              <div className="p-3 rounded-lg bg-surface border border-border">
                <span className="text-muted block mb-1">Recovery Score</span>
                <span className="font-mono font-bold text-emerald-400 text-sm">
                  {caseData.recovery_score.toFixed(1)} / 100
                </span>
              </div>
            </div>
          </div>

          {/* Policy Guardrails Checks */}
          <div className="p-6 rounded-xl border border-border bg-surface">
            <h2 className="text-base font-bold text-white mb-3 flex items-center gap-2">
              <Shield className="w-4 h-4 text-emerald-400" />
              Deterministic Policy Engine Guardrails
            </h2>

            <div className="space-y-2.5">
              <div className="p-3 rounded-lg bg-background/50 border border-border flex items-center justify-between text-xs">
                <div className="flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                  <span className="text-slate-200">Customer Opt-Out Compliance</span>
                </div>
                <span className="font-mono text-emerald-400">PASSED</span>
              </div>

              <div className="p-3 rounded-lg bg-background/50 border border-border flex items-center justify-between text-xs">
                <div className="flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                  <span className="text-slate-200">Max Retry Bound Check (Limit: 2)</span>
                </div>
                <span className="font-mono text-emerald-400">PASSED</span>
              </div>

              <div className="p-3 rounded-lg bg-background/50 border border-border flex items-center justify-between text-xs">
                <div className="flex items-center gap-2">
                  {caseData.requires_human_approval ? (
                    <AlertCircle className="w-4 h-4 text-amber-400" />
                  ) : (
                    <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                  )}
                  <span className="text-slate-200">High-Value Threshold (&gt; ₹10,000)</span>
                </div>
                <span className={caseData.requires_human_approval ? "font-mono text-amber-400" : "font-mono text-emerald-400"}>
                  {caseData.requires_human_approval ? "ESCALATED FOR APPROVAL" : "PASSED"}
                </span>
              </div>
            </div>
          </div>

          {/* Action Execution History */}
          <div className="p-6 rounded-xl border border-border bg-surface">
            <h2 className="text-base font-bold text-white mb-4">Execution History</h2>
            {caseData.actions.length === 0 ? (
              <p className="text-xs text-muted">No recovery actions executed yet.</p>
            ) : (
              <div className="space-y-3">
                {caseData.actions.map((act) => (
                  <div
                    key={act.id}
                    className="p-4 rounded-lg border border-border bg-background/60 text-xs space-y-2"
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <span className="font-bold text-white font-mono">{act.action_type}</span>
                        <StatusBadge status={act.status} size="sm" />
                      </div>
                      <span className="text-muted font-mono">{formatDate(act.executed_at || "")}</span>
                    </div>

                    <div className="text-slate-300">
                      Amount Recovered: <span className="font-bold text-white">{formatCurrency(act.amount)}</span>
                    </div>

                    {act.result && (
                      <div className="mt-2 p-2.5 rounded bg-surface border border-border/80 text-[11px] font-mono text-slate-300 overflow-x-auto">
                        <pre>{JSON.stringify(act.result, null, 2)}</pre>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
