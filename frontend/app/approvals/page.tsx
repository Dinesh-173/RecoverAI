"use client";

import React, { useEffect, useState } from "react";
import {
  UserCheck,
  ShieldAlert,
  CheckCircle,
  XCircle,
  RefreshCw,
  AlertTriangle,
  ArrowRight,
  ShieldCheck,
  X,
} from "lucide-react";
import { api } from "@/lib/api-client";
import { PendingApprovalItem } from "@/lib/types";
import { formatCurrency, formatDate } from "@/lib/utils";
import { StatusBadge } from "@/components/ui/StatusBadge";

export default function ApprovalsPage() {
  const [approvals, setApprovals] = useState<PendingApprovalItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [activeModal, setActiveModal] = useState<{ type: "APPROVE" | "REJECT"; item: PendingApprovalItem } | null>(null);
  const [actionLoading, setActionLoading] = useState(false);
  const [rejectReason, setRejectReason] = useState("");
  const [feedback, setFeedback] = useState<string | null>(null);

  const fetchApprovals = async (isManual = false) => {
    try {
      if (isManual) setIsRefreshing(true);
      else setLoading(true);
      const res = await api.getPendingApprovals();
      setApprovals(res.items || []);
    } catch (err) {
      console.error("Failed to fetch pending approvals:", err);
    } finally {
      setLoading(false);
      setIsRefreshing(false);
    }
  };

  useEffect(() => {
    fetchApprovals();
  }, []);

  const handleApprove = async () => {
    if (!activeModal) return;
    try {
      setActionLoading(true);
      await api.approveCase(activeModal.item.id);
      setFeedback(`Approved recovery action for ${formatCurrency(activeModal.item.amount)}.`);
      setActiveModal(null);
      await fetchApprovals();
    } catch (err: any) {
      setFeedback(`Error: ${err.message}`);
    } finally {
      setActionLoading(false);
    }
  };

  const handleReject = async () => {
    if (!activeModal) return;
    try {
      setActionLoading(true);
      await api.rejectCase(activeModal.item.id, rejectReason || "Rejected by merchant operator");
      setFeedback(`Rejected and terminated recovery case ${activeModal.item.id}.`);
      setActiveModal(null);
      setRejectReason("");
      await fetchApprovals();
    } catch (err: any) {
      setFeedback(`Error: ${err.message}`);
    } finally {
      setActionLoading(false);
    }
  };

  return (
    <div className="space-y-6 max-w-6xl mx-auto">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-2 border-b border-border/40">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[11px] font-medium bg-amber-500/10 text-amber-400 border border-amber-500/20">
              <ShieldAlert className="w-3 h-3 text-amber-400" />
              HUMAN-IN-THE-LOOP GOVERNANCE
            </span>
            <span className="text-xs text-muted font-mono">{approvals.length} pending review</span>
          </div>
          <h1 className="text-2xl lg:text-3xl font-bold tracking-tight text-white">Pending Human Approvals</h1>
          <p className="text-sm text-muted mt-0.5">
            Deterministic policy escalations for high-value transactions (&gt; ₹10,000) or low AI confidence.
          </p>
        </div>

        <button
          onClick={() => fetchApprovals(true)}
          disabled={isRefreshing || loading}
          className="px-3.5 py-2 rounded-xl border border-borderSubtle bg-surfaceSubtle hover:bg-surfaceHover text-slate-300 text-sm font-medium flex items-center gap-2 transition active:scale-[0.98] disabled:opacity-50 self-start"
        >
          <RefreshCw className={`w-4 h-4 text-slate-400 ${isRefreshing ? "animate-spin text-primary" : ""}`} />
          <span>{isRefreshing ? "Updating..." : "Refresh Queue"}</span>
        </button>
      </div>

      {feedback && (
        <div className="p-3.5 rounded-xl bg-primary/10 border border-primary/30 text-primary-light text-xs flex items-center justify-between">
          <span>{feedback}</span>
          <button onClick={() => setFeedback(null)} className="text-muted hover:text-white">&times;</button>
        </div>
      )}

      {/* Approvals Cards List */}
      {loading && approvals.length === 0 ? (
        <div className="fintech-card p-16 text-center">
          <RefreshCw className="w-6 h-6 text-primary animate-spin mx-auto mb-2" />
          <p className="text-xs text-muted">Checking policy escalation queue...</p>
        </div>
      ) : approvals.length === 0 ? (
        <div className="fintech-card p-12 text-center">
          <div className="w-12 h-12 rounded-2xl bg-emerald-950/40 border border-emerald-800/40 flex items-center justify-center text-emerald-400 mx-auto mb-3 shadow-lg shadow-emerald-900/20">
            <ShieldCheck className="w-6 h-6" />
          </div>
          <h3 className="text-base font-bold text-white">No Pending Escalations</h3>
          <p className="text-xs text-muted mt-1 max-w-sm mx-auto">
            All autonomous recovery cases have evaluated safely within merchant policy boundaries.
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-4">
          {approvals.map((item) => (
            <div
              key={item.id}
              className="fintech-card p-6 border-amber-800/40 bg-amber-950/[0.04] hover:border-amber-700/60 transition-all shadow-sm space-y-4 relative overflow-hidden"
            >
              <div className="absolute top-0 left-0 right-0 h-[2px] bg-gradient-to-r from-amber-500/0 via-amber-500 to-amber-500/0 opacity-60"></div>

              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-borderSubtle pb-3">
                <div className="flex items-center gap-3">
                  <span className="font-bold text-lg text-white font-mono tabular-nums">
                    {formatCurrency(item.amount, item.currency)}
                  </span>
                  <StatusBadge status={item.payment_method} size="sm" />
                  <StatusBadge status={item.customer_segment} size="sm" />
                </div>
                <div className="flex items-center gap-2 text-xs text-amber-300 font-medium">
                  <ShieldAlert className="w-4 h-4 text-amber-400" />
                  <span>{item.approval_reason}</span>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
                <div>
                  <span className="text-muted block mb-0.5">Customer</span>
                  <span className="font-semibold text-slate-200 text-sm">{item.customer_name}</span>
                  <span className="text-muted block mt-1 font-mono">Transaction Ref: {item.transaction_id}</span>
                </div>

                <div>
                  <span className="text-muted block mb-0.5">AI Proposed Strategy</span>
                  <span className="font-mono font-bold text-primary-light bg-primary/10 px-2 py-0.5 rounded-md border border-primary/20 inline-block">
                    {item.recommended_action}
                  </span>
                  <span className="text-muted ml-2 font-mono">Score: {item.recovery_score.toFixed(1)}/100</span>
                </div>
              </div>

              <div className="p-3.5 rounded-xl bg-slate-950/60 border border-borderSubtle text-xs text-slate-300">
                <span className="font-semibold text-slate-200 block mb-1">AI Diagnostic Evidence:</span>
                {item.diagnosis}
              </div>

              <div className="flex items-center justify-end gap-3 pt-2">
                <button
                  onClick={() => setActiveModal({ type: "REJECT", item })}
                  className="px-4 py-2 rounded-xl bg-rose-950/25 hover:bg-rose-900/40 text-rose-300 border border-rose-800/40 text-xs font-semibold flex items-center gap-1.5 transition duration-150 active:scale-[0.98] focus-ring"
                >
                  <XCircle className="w-4 h-4 text-rose-400" />
                  Reject Recovery
                </button>
                <button
                  onClick={() => setActiveModal({ type: "APPROVE", item })}
                  className="px-4 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold flex items-center gap-1.5 shadow-md shadow-emerald-600/20 transition duration-150 active:scale-[0.98] focus-ring"
                >
                  <CheckCircle className="w-4 h-4" />
                  Authorize Recovery
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Confirmation Modal */}
      {activeModal && (
        <div className="fixed inset-0 z-50 bg-black/75 backdrop-blur-sm flex items-center justify-center p-4 animate-fade-in">
          <div className="bg-slate-900 border border-slate-700/80 rounded-2xl max-w-md w-full p-6 space-y-4 shadow-2xl animate-slide-up ring-1 ring-white/10">
            <div className="flex items-center justify-between border-b border-borderSubtle pb-3">
              <h3 className="text-base font-bold text-white flex items-center gap-2">
                {activeModal.type === "APPROVE" ? (
                  <>
                    <CheckCircle className="w-5 h-5 text-emerald-400" />
                    Authorize High-Value Action
                  </>
                ) : (
                  <>
                    <XCircle className="w-5 h-5 text-rose-400" />
                    Reject Recovery Case
                  </>
                )}
              </h3>
              <button
                onClick={() => setActiveModal(null)}
                className="text-muted hover:text-white rounded-lg p-1 transition duration-150 focus-ring"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <p className="text-xs text-slate-300 leading-relaxed">
              {activeModal.type === "APPROVE"
                ? `You are authorizing ${activeModal.item.recommended_action} for transaction ${activeModal.item.transaction_id} (${formatCurrency(activeModal.item.amount)}). An immutable audit trail entry will be recorded.`
                : `Are you sure you want to stop recovery for case ${activeModal.item.id}? No further autonomous attempts will be made.`}
            </p>

            {activeModal.type === "REJECT" && (
              <div>
                <label className="text-xs text-muted block mb-1">Reason for Rejection</label>
                <input
                  type="text"
                  placeholder="e.g. Verified fraud with customer, manual offline resolution"
                  value={rejectReason}
                  onChange={(e) => setRejectReason(e.target.value)}
                  className="w-full bg-slate-950/60 border border-borderSubtle rounded-xl px-3 py-2 text-xs text-white placeholder:text-muted focus-ring transition duration-150"
                />
              </div>
            )}

            <div className="flex items-center justify-end gap-3 pt-3 border-t border-borderSubtle">
              <button
                disabled={actionLoading}
                onClick={() => setActiveModal(null)}
                className="px-3.5 py-1.5 rounded-xl border border-borderSubtle text-slate-300 text-xs hover:bg-surfaceHover transition duration-150 focus-ring"
              >
                Cancel
              </button>
              <button
                disabled={actionLoading}
                onClick={activeModal.type === "APPROVE" ? handleApprove : handleReject}
                className={`px-4 py-2 rounded-xl text-white text-xs font-semibold transition duration-150 active:scale-[0.98] focus-ring ${
                  activeModal.type === "APPROVE"
                    ? "bg-emerald-600 hover:bg-emerald-500 shadow-md shadow-emerald-600/20"
                    : "bg-rose-600 hover:bg-rose-500 shadow-md shadow-rose-600/20"
                }`}
              >
                {actionLoading ? "Processing..." : activeModal.type === "APPROVE" ? "Confirm & Authorize" : "Confirm Rejection"}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
