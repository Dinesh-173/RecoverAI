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
} from "lucide-react";
import { api } from "@/lib/api-client";
import { PendingApprovalItem } from "@/lib/types";
import { formatCurrency, formatDate } from "@/lib/utils";
import { StatusBadge } from "@/components/ui/StatusBadge";

export default function ApprovalsPage() {
  const [approvals, setApprovals] = useState<PendingApprovalItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeModal, setActiveModal] = useState<{ type: "APPROVE" | "REJECT"; item: PendingApprovalItem } | null>(null);
  const [actionLoading, setActionLoading] = useState(false);
  const [rejectReason, setRejectReason] = useState("");
  const [feedback, setFeedback] = useState<string | null>(null);

  const fetchApprovals = async () => {
    try {
      setLoading(true);
      const res = await api.getPendingApprovals();
      setApprovals(res.items || []);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
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
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-white">Pending Human Approvals</h1>
          <p className="text-sm text-muted mt-0.5">
            High-value or low-confidence recovery actions requiring merchant signoff.
          </p>
        </div>

        <button
          onClick={fetchApprovals}
          className="px-3.5 py-2 rounded-lg border border-border bg-surface hover:bg-surfaceHover text-slate-300 text-sm font-medium flex items-center gap-2 transition self-start"
        >
          <RefreshCw className={loading ? "w-4 h-4 animate-spin" : "w-4 h-4"} />
          Refresh Queue
        </button>
      </div>

      {feedback && (
        <div className="p-3.5 rounded-lg bg-blue-950/40 border border-blue-800/40 text-blue-300 text-xs flex items-center justify-between">
          <span>{feedback}</span>
          <button onClick={() => setFeedback(null)} className="text-muted hover:text-white">&times;</button>
        </div>
      )}

      {/* Approvals Cards List */}
      {approvals.length === 0 ? (
        <div className="p-12 text-center rounded-xl border border-border bg-surface">
          <div className="w-12 h-12 rounded-full bg-emerald-950/60 border border-emerald-800/60 flex items-center justify-center text-emerald-400 mx-auto mb-3">
            <CheckCircle className="w-6 h-6" />
          </div>
          <h3 className="text-base font-bold text-white">No Pending Escalations</h3>
          <p className="text-xs text-muted mt-1 max-w-sm mx-auto">
            All autonomous recovery cases have been processed within safe policy limits.
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-4">
          {approvals.map((item) => (
            <div
              key={item.id}
              className="p-6 rounded-xl border border-amber-800/40 bg-surface hover:border-amber-700/60 transition shadow-sm space-y-4"
            >
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-border pb-3">
                <div className="flex items-center gap-3">
                  <span className="font-bold text-lg text-white font-mono">
                    {formatCurrency(item.amount, item.currency)}
                  </span>
                  <StatusBadge status={item.payment_method} size="sm" />
                  <StatusBadge status={item.customer_segment} size="sm" />
                </div>
                <div className="flex items-center gap-2 text-xs text-amber-400 font-medium">
                  <ShieldAlert className="w-4 h-4" />
                  <span>{item.approval_reason}</span>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
                <div>
                  <span className="text-muted block mb-0.5">Customer</span>
                  <span className="font-semibold text-slate-200 text-sm">{item.customer_name}</span>
                  <span className="text-muted block mt-1">Transaction Ref: {item.transaction_id}</span>
                </div>

                <div>
                  <span className="text-muted block mb-0.5">AI Proposed Strategy</span>
                  <span className="font-mono font-bold text-blue-400 bg-blue-950/40 px-2 py-0.5 rounded border border-blue-800/40 inline-block">
                    {item.recommended_action}
                  </span>
                  <span className="text-muted ml-2">Score: {item.recovery_score.toFixed(1)}/100</span>
                </div>
              </div>

              <div className="p-3.5 rounded-lg bg-background/60 border border-border text-xs text-slate-300">
                <span className="font-semibold text-slate-200 block mb-1">AI Diagnostic Evidence:</span>
                {item.diagnosis}
              </div>

              <div className="flex items-center justify-end gap-3 pt-2">
                <button
                  onClick={() => setActiveModal({ type: "REJECT", item })}
                  className="px-4 py-2 rounded-lg bg-rose-950/40 hover:bg-rose-900/60 text-rose-300 border border-rose-800/60 text-xs font-semibold flex items-center gap-1.5 transition"
                >
                  <XCircle className="w-4 h-4" />
                  Reject Recovery
                </button>
                <button
                  onClick={() => setActiveModal({ type: "APPROVE", item })}
                  className="px-4 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold flex items-center gap-1.5 shadow-lg shadow-emerald-500/20 transition"
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
        <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-surface border border-border rounded-xl max-w-md w-full p-6 space-y-4 shadow-2xl">
            <h3 className="text-lg font-bold text-white">
              {activeModal.type === "APPROVE" ? "Authorize High-Value Action" : "Reject Recovery Case"}
            </h3>

            <p className="text-xs text-slate-300">
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
                  className="w-full bg-background border border-border rounded-lg px-3 py-2 text-xs text-white placeholder:text-muted focus:outline-none focus:border-rose-500"
                />
              </div>
            )}

            <div className="flex items-center justify-end gap-3 pt-3">
              <button
                disabled={actionLoading}
                onClick={() => setActiveModal(null)}
                className="px-3.5 py-1.5 rounded-lg border border-border text-slate-300 text-xs hover:bg-surfaceHover transition"
              >
                Cancel
              </button>
              <button
                disabled={actionLoading}
                onClick={activeModal.type === "APPROVE" ? handleApprove : handleReject}
                className={`px-4 py-2 rounded-lg text-white text-xs font-semibold transition ${
                  activeModal.type === "APPROVE"
                    ? "bg-emerald-600 hover:bg-emerald-500 shadow-lg shadow-emerald-500/20"
                    : "bg-rose-600 hover:bg-rose-500 shadow-lg shadow-rose-500/20"
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
