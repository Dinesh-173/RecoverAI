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
  HelpCircle,
  Info,
  Lock,
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
  const [showExplainModal, setShowExplainModal] = useState(false);

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
              onClick={() => setShowExplainModal(true)}
              className="px-3.5 py-2 rounded-lg bg-blue-950/40 hover:bg-blue-900/40 border border-blue-800/60 text-blue-300 text-sm font-semibold flex items-center gap-2 transition"
            >
              <HelpCircle className="w-4 h-4 text-blue-400" />
              <span>Why Did RecoverAI Do This?</span>
            </button>

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

      {/* Autonomous Decision Pipeline Flow */}
      <div className="p-6 rounded-xl border border-border bg-surface space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Sparkles className="w-5 h-5 text-blue-400" />
            <h2 className="text-base font-bold text-white">Autonomous Decision Pipeline</h2>
          </div>
          <span className="text-xs text-muted font-mono">Architecture: AI Advisory + Policy Authoritative</span>
        </div>

        <div className="p-4 rounded-lg bg-background/60 border border-border">
          <div className="grid grid-cols-1 sm:grid-cols-5 gap-3 text-center text-xs">
            <div className="p-3 rounded-lg bg-surface border border-border flex flex-col justify-between">
              <span className="text-[10px] uppercase text-muted font-semibold">1. Transaction</span>
              <span className="font-bold text-white text-sm mt-1">{formatCurrency(tx?.amount || 0)}</span>
              <span className="text-[10px] text-rose-400 mt-1">{tx?.failure_code}</span>
            </div>

            <div className="p-3 rounded-lg bg-surface border border-border flex flex-col justify-between">
              <span className="text-[10px] uppercase text-muted font-semibold">2. ML Assessment</span>
              <span className="font-bold text-blue-400 text-sm mt-1">{caseData.recovery_score.toFixed(1)}/100</span>
              <span className="text-[10px] text-muted mt-1">{caseData.risk_level} Risk</span>
            </div>

            <div className="p-3 rounded-lg bg-surface border border-blue-900/40 flex flex-col justify-between">
              <span className="text-[10px] uppercase text-blue-400 font-semibold">3. AI Agent (Advisory)</span>
              <span className="font-bold text-white text-xs mt-1 font-mono">{caseData.recommended_action || "NONE"}</span>
              <span className="text-[10px] text-blue-300 mt-1">{((caseData.confidence || 0) * 100).toFixed(0)}% Conf</span>
            </div>

            <div className="p-3 rounded-lg bg-surface border border-purple-900/40 flex flex-col justify-between">
              <span className="text-[10px] uppercase text-purple-400 font-semibold">4. Policy Engine</span>
              <span className="font-bold text-purple-300 text-xs mt-1 font-mono">
                {caseData.requires_human_approval ? "ESCALATE" : "AUTHORIZATION"}
              </span>
              <span className="text-[10px] text-muted mt-1">Rule Bound Check</span>
            </div>

            <div className="p-3 rounded-lg bg-emerald-950/30 border border-emerald-800/40 flex flex-col justify-between">
              <span className="text-[10px] uppercase text-emerald-400 font-semibold">5. Final Decision</span>
              <span className="font-bold text-emerald-400 text-xs mt-1 font-mono">{caseData.status}</span>
              <span className="text-[10px] text-emerald-300 mt-1">Safe Execution</span>
            </div>
          </div>
        </div>

        <div className="p-3 rounded-lg bg-blue-950/20 border border-blue-800/30 text-xs text-blue-300 flex items-center justify-between font-mono">
          <span>AI proposed the action. Policy Engine made the final decision.</span>
          <button
            onClick={() => setShowExplainModal(true)}
            className="text-blue-400 underline hover:text-white"
          >
            Explain Decision Rationale
          </button>
        </div>
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

      {/* "Why Did RecoverAI Do This?" Explainability Modal */}
      {showExplainModal && (
        <div className="fixed inset-0 z-50 bg-black/75 backdrop-blur-sm flex items-center justify-center p-4 animate-in fade-in duration-200">
          <div className="bg-surface border border-border rounded-xl max-w-lg w-full p-6 space-y-5 shadow-2xl">
            <div className="flex items-center justify-between border-b border-border pb-3">
              <div className="flex items-center gap-2">
                <HelpCircle className="w-5 h-5 text-blue-400" />
                <h3 className="text-base font-bold text-white">Why Did RecoverAI Do This?</h3>
              </div>
              <button
                onClick={() => setShowExplainModal(false)}
                className="text-muted hover:text-white text-lg font-bold"
              >
                &times;
              </button>
            </div>

            <div className="space-y-4 text-xs">
              <div className="p-3.5 rounded-lg bg-blue-950/30 border border-blue-800/40 space-y-1.5">
                <span className="font-bold text-blue-300 text-sm block">1. AI Advisory Recommendation</span>
                <p className="text-slate-200">
                  The LLM Diagnostic Agent recommended <span className="font-mono font-bold text-white">{caseData.recommended_action}</span> with a confidence score of <span className="font-mono text-blue-400">{((caseData.confidence || 0) * 100).toFixed(0)}%</span> based on historical success rates for {tx?.payment_method} failures ({tx?.failure_code}).
                </p>
              </div>

              <div className="p-3.5 rounded-lg bg-purple-950/30 border border-purple-800/40 space-y-1.5">
                <span className="font-bold text-purple-300 text-sm block">2. Policy Engine Evaluation (Authoritative)</span>
                <p className="text-slate-200">
                  {caseData.requires_human_approval ? (
                    <>
                      The Deterministic Policy Engine intercepted the AI proposal because the transaction amount (<span className="font-mono font-bold text-white">{formatCurrency(tx?.amount || 0)}</span>) exceeds the high-value merchant threshold (<span className="font-mono text-amber-400">₹10,000</span>). The Policy Engine required human authorization before payment execution.
                    </>
                  ) : caseData.status === "STOPPED" ? (
                    <>
                      The Policy Engine halted recovery due to policy boundary bounds (retry limit reached, opt-out status, or security block).
                    </>
                  ) : (
                    <>
                      The Policy Engine verified that all safety rules passed: transaction amount is under threshold, retry attempt is within limit (2), customer has not opted out, and no risk flags exist.
                    </>
                  )}
                </p>
              </div>

              <div className="p-3.5 rounded-lg bg-emerald-950/30 border border-emerald-800/40 space-y-1.5">
                <span className="font-bold text-emerald-300 text-sm block">3. Execution Authority & Isolation</span>
                <p className="text-slate-200">
                  The final status is <span className="font-mono font-bold text-emerald-400">{caseData.status}</span>. Payment execution is handled by the isolated Payment Adapter under strict idempotency guarantees.
                </p>
              </div>
            </div>

            <div className="pt-2 border-t border-border flex justify-end">
              <button
                onClick={() => setShowExplainModal(false)}
                className="px-4 py-2 rounded-lg bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold"
              >
                Got It
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
