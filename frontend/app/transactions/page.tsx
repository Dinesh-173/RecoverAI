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
} from "lucide-react";
import { api } from "@/lib/api-client";
import { Transaction } from "@/lib/types";
import { formatCurrency, formatDate } from "@/lib/utils";
import { StatusBadge } from "@/components/ui/StatusBadge";

export default function TransactionsPage() {
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState("");
  const [methodFilter, setMethodFilter] = useState("");
  const [searchTerm, setSearchTerm] = useState("");
  const [skip, setSkip] = useState(0);
  const limit = 20;

  const fetchTransactions = async () => {
    try {
      setLoading(true);
      const params = new URLSearchParams();
      params.set("skip", skip.toString());
      params.set("limit", limit.toString());
      if (statusFilter) params.set("status", statusFilter);
      if (methodFilter) params.set("payment_method", methodFilter);

      const res = await api.getTransactions(params.toString());
      setTransactions(res.items || []);
      setTotal(res.total || 0);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
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
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-white">Transactions Explorer</h1>
          <p className="text-sm text-muted mt-0.5">
            Real-time transaction stream with ML risk assessment and recovery routing status.
          </p>
        </div>

        <button
          onClick={fetchTransactions}
          className="px-3.5 py-2 rounded-lg border border-border bg-surface hover:bg-surfaceHover text-slate-300 text-sm font-medium flex items-center gap-2 transition self-start"
        >
          <RefreshCw className={loading ? "w-4 h-4 animate-spin" : "w-4 h-4"} />
          Refresh
        </button>
      </div>

      {/* Filter Bar */}
      <div className="p-4 rounded-xl border border-border bg-surface flex flex-wrap items-center justify-between gap-4">
        <div className="flex items-center gap-3 flex-1 min-w-[280px]">
          <div className="relative flex-1">
            <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-muted" />
            <input
              type="text"
              placeholder="Search by transaction ID, payment ID, or customer..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full bg-background border border-border rounded-lg pl-9 pr-4 py-2 text-sm text-white placeholder:text-muted focus:outline-none focus:border-blue-500 transition"
            />
          </div>
        </div>

        <div className="flex items-center gap-3">
          <select
            value={statusFilter}
            onChange={(e) => {
              setStatusFilter(e.target.value);
              setSkip(0);
            }}
            className="bg-background border border-border rounded-lg px-3 py-2 text-sm text-slate-300 focus:outline-none focus:border-blue-500"
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
            className="bg-background border border-border rounded-lg px-3 py-2 text-sm text-slate-300 focus:outline-none focus:border-blue-500"
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
      <div className="rounded-xl border border-border bg-surface overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead className="bg-surfaceHover/60 text-muted uppercase text-[11px] font-semibold border-b border-border">
              <tr>
                <th className="px-5 py-3.5">Transaction ID</th>
                <th className="px-5 py-3.5">Customer</th>
                <th className="px-5 py-3.5">Amount</th>
                <th className="px-5 py-3.5">Rail</th>
                <th className="px-5 py-3.5">Status</th>
                <th className="px-5 py-3.5">Failure Reason</th>
                <th className="px-5 py-3.5">Risk Score</th>
                <th className="px-5 py-3.5">Recovery Status</th>
                <th className="px-5 py-3.5">Timestamp</th>
                <th className="px-5 py-3.5 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {filtered.length === 0 ? (
                <tr>
                  <td colSpan={10} className="px-5 py-12 text-center text-muted">
                    No transactions found matching your criteria.
                  </td>
                </tr>
              ) : (
                filtered.map((tx) => (
                  <tr key={tx.id} className="hover:bg-surfaceHover/40 transition">
                    <td className="px-5 py-3.5 font-mono text-xs font-medium text-white">
                      <div>{tx.id}</div>
                      {tx.external_transaction_id && (
                        <div className="text-[10px] text-muted">{tx.external_transaction_id}</div>
                      )}
                    </td>
                    <td className="px-5 py-3.5">
                      <div className="font-medium text-slate-200">{tx.customer_name || tx.customer?.name || "Customer"}</div>
                      <div className="text-[11px] text-muted flex items-center gap-1.5 mt-0.5">
                        <StatusBadge status={tx.customer_segment || tx.customer?.customer_segment || "STANDARD"} size="sm" />
                      </div>
                    </td>
                    <td className="px-5 py-3.5 font-semibold text-white">
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
                        <span className="font-mono text-[11px] text-rose-400 bg-rose-950/40 px-1.5 py-0.5 rounded border border-rose-900/40">
                          {tx.failure_code}
                        </span>
                      ) : (
                        "-"
                      )}
                    </td>
                    <td className="px-5 py-3.5">
                      {tx.risk_score !== null && tx.risk_score !== undefined ? (
                        <div className="flex items-center gap-2">
                          <span
                            className={`text-xs font-semibold font-mono ${
                              tx.risk_score > 60
                                ? "text-rose-400"
                                : tx.risk_score > 30
                                ? "text-amber-400"
                                : "text-emerald-400"
                            }`}
                          >
                            {tx.risk_score.toFixed(0)}/100
                          </span>
                        </div>
                      ) : (
                        <span className="text-muted text-xs">-</span>
                      )}
                    </td>
                    <td className="px-5 py-3.5">
                      <StatusBadge status={tx.case_status || "OPEN"} size="sm" />
                    </td>
                    <td className="px-5 py-3.5 text-xs text-muted">
                      {formatDate(tx.created_at)}
                    </td>
                    <td className="px-5 py-3.5 text-right">
                      <Link
                        href={`/recovery-cases`}
                        className="inline-flex items-center gap-1 text-xs text-blue-400 hover:text-blue-300 font-medium"
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
        <div className="p-4 border-t border-border flex items-center justify-between text-xs text-muted">
          <span>
            Showing {filtered.length} of {total} transactions
          </span>
          <div className="flex items-center gap-2">
            <button
              disabled={skip === 0}
              onClick={() => setSkip(Math.max(0, skip - limit))}
              className="px-3 py-1.5 rounded bg-background border border-border text-slate-300 disabled:opacity-40 disabled:cursor-not-allowed hover:bg-surfaceHover transition"
            >
              Previous
            </button>
            <button
              disabled={skip + limit >= total}
              onClick={() => setSkip(skip + limit)}
              className="px-3 py-1.5 rounded bg-background border border-border text-slate-300 disabled:opacity-40 disabled:cursor-not-allowed hover:bg-surfaceHover transition"
            >
              Next
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
