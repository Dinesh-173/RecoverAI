"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import {
  Search,
  Filter,
  ArrowUpDown,
  ExternalLink,
  RefreshCw,
  CreditCard,
  SlidersHorizontal,
  ChevronLeft,
  ChevronRight,
} from "lucide-react";
import { api } from "@/lib/api-client";
import { Transaction } from "@/lib/types";
import { formatCurrency, formatDate } from "@/lib/utils";
import { StatusBadge } from "@/components/ui/StatusBadge";

export default function TransactionsPage() {
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [statusFilter, setStatusFilter] = useState("");
  const [methodFilter, setMethodFilter] = useState("");
  const [searchTerm, setSearchTerm] = useState("");
  const [skip, setSkip] = useState(0);
  const limit = 20;

  const fetchTransactions = async (isManual = false) => {
    try {
      if (isManual) setIsRefreshing(true);
      else setLoading(true);
      const params = new URLSearchParams();
      params.set("skip", skip.toString());
      params.set("limit", limit.toString());
      if (statusFilter) params.set("status", statusFilter);
      if (methodFilter) params.set("payment_method", methodFilter);

      const res = await api.getTransactions(params.toString());
      setTransactions(res.items || []);
      setTotal(res.total || 0);
    } catch (err) {
      console.error("Failed to fetch transactions:", err);
    } finally {
      setLoading(false);
      setIsRefreshing(false);
    }
  };

  useEffect(() => {
    fetchTransactions();
  }, [skip, statusFilter, methodFilter]);

  const filtered = transactions.filter(
    (t) =>
      t.id.toLowerCase().includes(searchTerm.toLowerCase()) ||
      (t.customer_name && t.customer_name.toLowerCase().includes(searchTerm.toLowerCase())) ||
      (t.customer?.name && t.customer.name.toLowerCase().includes(searchTerm.toLowerCase())) ||
      (t.external_transaction_id && t.external_transaction_id.toLowerCase().includes(searchTerm.toLowerCase()))
  );

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-2 border-b border-border/40">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[11px] font-medium bg-primary/10 text-primary border border-primary/20">
              <CreditCard className="w-3 h-3 text-primary" />
              TELEMETRY INGESTION
            </span>
            <span className="text-xs text-muted font-mono">{total} records captured</span>
          </div>
          <h1 className="text-2xl lg:text-3xl font-bold tracking-tight text-white">Transactions Explorer</h1>
          <p className="text-sm text-muted mt-0.5">
            Real-time transaction stream with ML risk assessment, failure classification, and automated case linkage.
          </p>
        </div>

        <button
          onClick={() => fetchTransactions(true)}
          disabled={isRefreshing || loading}
          className="px-3.5 py-2 rounded-xl border border-borderSubtle bg-surfaceSubtle hover:bg-surfaceHover text-slate-300 text-sm font-medium flex items-center gap-2 transition duration-150 active:scale-[0.98] disabled:opacity-50 self-start focus-ring"
        >
          <RefreshCw className={`w-4 h-4 text-slate-400 ${isRefreshing ? "animate-spin text-primary" : ""}`} />
          <span>{isRefreshing ? "Updating..." : "Refresh"}</span>
        </button>
      </div>

      {/* Filter Bar */}
      <div className="fintech-card p-4 flex flex-wrap items-center justify-between gap-4">
        <div className="flex items-center gap-3 flex-1 min-w-[280px]">
          <div className="relative flex-1">
            <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-muted" />
            <input
              type="text"
              placeholder="Search by transaction ID, payment ID, or customer name..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full bg-slate-950/60 border border-borderSubtle rounded-xl pl-9 pr-4 py-2 text-sm text-white placeholder:text-muted focus-ring transition duration-150"
            />
          </div>
        </div>

        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2 text-xs text-muted">
            <SlidersHorizontal className="w-3.5 h-3.5" />
            <span>Filters:</span>
          </div>

          <select
            value={statusFilter}
            onChange={(e) => {
              setStatusFilter(e.target.value);
              setSkip(0);
            }}
            className="bg-slate-950/60 border border-borderSubtle rounded-xl px-3 py-2 text-sm text-slate-300 focus-ring transition duration-150 cursor-pointer"
          >
            <option value="">All Statuses</option>
            <option value="FAILED">FAILED</option>
            <option value="CAPTURED">CAPTURED</option>
            <option value="AUTHORIZED">AUTHORIZED</option>
          </select>

          <select
            value={methodFilter}
            onChange={(e) => {
              setMethodFilter(e.target.value);
              setSkip(0);
            }}
            className="bg-slate-950/60 border border-borderSubtle rounded-xl px-3 py-2 text-sm text-slate-300 focus-ring transition duration-150 cursor-pointer"
          >
            <option value="">All Rails</option>
            <option value="UPI">UPI</option>
            <option value="CARD">CARD</option>
            <option value="NETBANKING">NETBANKING</option>
            <option value="WALLET">WALLET</option>
          </select>
        </div>
      </div>

      {/* Transactions Table */}
      <div className="fintech-card overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead className="bg-surfaceSubtle/80 text-muted uppercase text-[10px] font-mono tracking-wider border-b border-borderSubtle">
              <tr>
                <th className="px-5 py-3.5">Transaction ID</th>
                <th className="px-5 py-3.5">Customer</th>
                <th className="px-5 py-3.5">Amount</th>
                <th className="px-5 py-3.5">Rail</th>
                <th className="px-5 py-3.5">Status</th>
                <th className="px-5 py-3.5">Failure Reason</th>
                <th className="px-5 py-3.5">ML Risk</th>
                <th className="px-5 py-3.5">Case Status</th>
                <th className="px-5 py-3.5">Timestamp</th>
                <th className="px-5 py-3.5 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-borderSubtle">
              {loading && transactions.length === 0 ? (
                <tr>
                  <td colSpan={10} className="px-5 py-16 text-center text-muted">
                    <div className="flex flex-col items-center justify-center gap-2">
                      <RefreshCw className="w-6 h-6 text-primary animate-spin" />
                      <span className="text-xs text-slate-400">Loading transaction stream...</span>
                    </div>
                  </td>
                </tr>
              ) : filtered.length === 0 ? (
                <tr>
                  <td colSpan={10} className="px-5 py-16 text-center text-muted">
                    <div className="flex flex-col items-center justify-center gap-1.5">
                      <p className="text-sm font-medium text-slate-300">No transactions match your criteria</p>
                      <p className="text-xs text-slate-500">Try adjusting your search keyword or clearing status filters</p>
                    </div>
                  </td>
                </tr>
              ) : (
                filtered.map((tx) => (
                  <tr key={tx.id} className="hover:bg-surfaceSubtle/50 transition-colors group">
                    <td className="px-5 py-3.5 font-mono text-xs font-medium text-white">
                      <div className="group-hover:text-primary transition-colors">{tx.id}</div>
                      {tx.external_transaction_id && (
                        <div className="text-[10px] text-muted font-mono">{tx.external_transaction_id}</div>
                      )}
                    </td>
                    <td className="px-5 py-3.5">
                      <div className="font-medium text-slate-200">{tx.customer_name || tx.customer?.name || "Customer"}</div>
                      <div className="text-[11px] text-muted flex items-center gap-1.5 mt-0.5">
                        <StatusBadge status={tx.customer_segment || tx.customer?.customer_segment || "STANDARD"} size="sm" />
                      </div>
                    </td>
                    <td className="px-5 py-3.5 font-semibold text-white tabular-nums">
                      {formatCurrency(tx.amount, tx.currency)}
                    </td>
                    <td className="px-5 py-3.5">
                      <StatusBadge status={tx.payment_method} size="sm" />
                    </td>
                    <td className="px-5 py-3.5">
                      <StatusBadge status={tx.status} size="sm" />
                    </td>
                    <td className="px-5 py-3.5 text-xs text-slate-300 max-w-[200px] truncate">
                      {tx.failure_code ? (
                        <span className="font-mono text-[11px] text-rose-400 bg-rose-950/40 px-2 py-0.5 rounded-md border border-rose-900/40">
                          {tx.failure_code}
                        </span>
                      ) : (
                        <span className="text-slate-600 font-mono">-</span>
                      )}
                    </td>
                    <td className="px-5 py-3.5">
                      {tx.risk_score !== null && tx.risk_score !== undefined ? (
                        <div className="flex items-center gap-2">
                          <span
                            className={`text-xs font-semibold font-mono px-2 py-0.5 rounded-md ${
                              tx.risk_score > 60
                                ? "text-rose-400 bg-rose-950/30 border border-rose-900/30"
                                : tx.risk_score > 30
                                ? "text-amber-400 bg-amber-950/30 border border-amber-900/30"
                                : "text-emerald-400 bg-emerald-950/30 border border-emerald-900/30"
                            }`}
                          >
                            {tx.risk_score.toFixed(0)}/100
                          </span>
                        </div>
                      ) : (
                        <span className="text-slate-600 text-xs font-mono">-</span>
                      )}
                    </td>
                    <td className="px-5 py-3.5">
                      <StatusBadge status={tx.case_status || "OPEN"} size="sm" />
                    </td>
                    <td className="px-5 py-3.5 text-xs text-muted font-mono">
                      {formatDate(tx.created_at)}
                    </td>
                    <td className="px-5 py-3.5 text-right">
                      <Link
                        href={`/recovery-cases`}
                        className="inline-flex items-center gap-1 text-xs text-primary hover:text-primary-light font-medium transition"
                      >
                        <span>View</span>
                        <ExternalLink className="w-3 h-3" />
                      </Link>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination */}
        <div className="p-4 border-t border-borderSubtle flex items-center justify-between text-xs text-muted bg-surfaceSubtle/30">
          <span className="font-mono">
            Showing <strong className="text-slate-300">{filtered.length}</strong> of <strong className="text-slate-300">{total}</strong> transactions
          </span>
          <div className="flex items-center gap-2">
            <button
              disabled={skip === 0}
              onClick={() => setSkip(Math.max(0, skip - limit))}
              className="px-3 py-1.5 rounded-xl bg-slate-950/60 border border-borderSubtle text-slate-300 disabled:opacity-40 disabled:cursor-not-allowed hover:bg-surfaceHover transition flex items-center gap-1 font-medium"
            >
              <ChevronLeft className="w-3.5 h-3.5" />
              Previous
            </button>
            <button
              disabled={skip + limit >= total}
              onClick={() => setSkip(skip + limit)}
              className="px-3 py-1.5 rounded-xl bg-slate-950/60 border border-borderSubtle text-slate-300 disabled:opacity-40 disabled:cursor-not-allowed hover:bg-surfaceHover transition flex items-center gap-1 font-medium"
            >
              Next
              <ChevronRight className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
