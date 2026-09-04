"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import {
  DollarSign,
  TrendingUp,
  AlertTriangle,
  CheckCircle2,
  Clock,
  ArrowUpRight,
  ShieldAlert,
  Play,
  RefreshCw,
  Sparkles,
} from "lucide-react";
import {
  AreaChart,
  Area,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
} from "recharts";
import { api } from "@/lib/api-client";
import { DashboardMetrics } from "@/lib/types";
import { formatCurrency, formatNumber } from "@/lib/utils";

const COLORS = ["#3B82F6", "#10B981", "#F59E0B", "#8B5CF6", "#EC4899", "#06B6D4"];

export default function DashboardPage() {
  const [metrics, setMetrics] = useState<DashboardMetrics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchMetrics = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await api.getDashboardMetrics();
      setMetrics(data);
    } catch (err: any) {
      setError(err.message || "Failed to load dashboard metrics.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchMetrics();
  }, []);

  if (loading && !metrics) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="flex flex-col items-center gap-3">
          <RefreshCw className="w-8 h-8 text-blue-500 animate-spin" />
          <p className="text-sm text-muted">Calculating live recovery metrics...</p>
        </div>
      </div>
    );
  }

  if (error || !metrics) {
    return (
      <div className="p-6 rounded-xl border border-rose-800/60 bg-rose-950/20 text-rose-300">
        <p className="font-semibold">Unable to connect to backend engine</p>
        <p className="text-sm text-rose-400 mt-1">{error}</p>
        <button
          onClick={fetchMetrics}
          className="mt-4 px-4 py-2 bg-rose-600 hover:bg-rose-500 text-white rounded-lg text-sm font-medium transition"
        >
          Retry Connection
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-8 max-w-7xl mx-auto">
      {/* Top Banner & Quick Actions */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-white">Revenue Recovery Dashboard</h1>
          <p className="text-sm text-muted mt-0.5">
            Autonomous failure diagnosis, policy-bounded recovery, and ROI measurement.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={fetchMetrics}
            className="px-3.5 py-2 rounded-lg border border-border bg-surface hover:bg-surfaceHover text-slate-300 text-sm font-medium flex items-center gap-2 transition"
          >
            <RefreshCw className="w-4 h-4 text-slate-400" />
            Refresh
          </button>
          <Link
            href="/simulation"
            className="px-4 py-2 rounded-lg bg-blue-600 hover:bg-blue-500 text-white text-sm font-medium flex items-center gap-2 shadow-lg shadow-blue-500/20 transition"
          >
            <Play className="w-4 h-4 fill-white" />
            Run Recovery Simulation
          </Link>
        </div>
      </div>

      {/* KPI Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
        {/* Revenue at Risk */}
        <div className="p-5 rounded-xl border border-border bg-surface relative overflow-hidden">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold uppercase tracking-wider text-muted">Revenue at Risk</span>
            <div className="w-8 h-8 rounded-lg bg-rose-950/60 border border-rose-800/60 flex items-center justify-center text-rose-400">
              <AlertTriangle className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-3">
            <div className="text-2xl font-bold text-white tracking-tight">
              {formatCurrency(metrics.revenue_at_risk)}
            </div>
            <p className="text-xs text-muted mt-1">
              From {formatNumber(metrics.total_evaluated_transactions)} evaluated transactions
            </p>
          </div>
        </div>

        {/* Recovered Revenue */}
        <div className="p-5 rounded-xl border border-border bg-surface relative overflow-hidden">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold uppercase tracking-wider text-muted">Recovered Revenue</span>
            <div className="w-8 h-8 rounded-lg bg-emerald-950/60 border border-emerald-800/60 flex items-center justify-center text-emerald-400">
              <TrendingUp className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-3">
            <div className="text-2xl font-bold text-emerald-400 tracking-tight">
              {formatCurrency(metrics.recovered_revenue)}
            </div>
            <div className="flex items-center gap-1 text-xs text-emerald-400 font-medium mt-1">
              <ArrowUpRight className="w-3.5 h-3.5" />
              <span>{metrics.recovery_rate}% Recovery Rate</span>
            </div>
          </div>
        </div>

        {/* Net Value-Add vs Baseline */}
        <div className="p-5 rounded-xl border border-blue-800/40 bg-blue-950/20 relative overflow-hidden">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold uppercase tracking-wider text-blue-300">RecoverAI ROI Delta</span>
            <div className="w-8 h-8 rounded-lg bg-blue-600/30 border border-blue-500/40 flex items-center justify-center text-blue-400">
              <Sparkles className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-3">
            <div className="text-2xl font-bold text-white tracking-tight">
              +{formatCurrency(metrics.delta_revenue_gain)}
            </div>
            <p className="text-xs text-blue-300 mt-1">
              Beyond naive baseline ({metrics.baseline_recovery_rate}% benchmark)
            </p>
          </div>
        </div>

        {/* Pending Approvals */}
        <Link
          href="/approvals"
          className="p-5 rounded-xl border border-amber-800/40 bg-amber-950/15 hover:bg-amber-950/25 transition relative overflow-hidden group block"
        >
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold uppercase tracking-wider text-amber-300">Pending Approvals</span>
            <div className="w-8 h-8 rounded-lg bg-amber-950/60 border border-amber-800/60 flex items-center justify-center text-amber-400 group-hover:scale-105 transition">
              <ShieldAlert className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-3">
            <div className="text-2xl font-bold text-amber-400 tracking-tight">
              {metrics.pending_approvals} Cases
            </div>
            <p className="text-xs text-amber-300/80 mt-1 flex items-center gap-1">
              <span>High-value / Low-confidence escalation</span>
              <ArrowUpRight className="w-3 h-3" />
            </p>
          </div>
        </Link>
      </div>

      {/* Main Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Timeline Chart */}
        <div className="lg:col-span-2 p-6 rounded-xl border border-border bg-surface">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h2 className="text-base font-semibold text-white">Revenue at Risk vs. Recovered Over Time</h2>
              <p className="text-xs text-muted">Weekly rolling financial volume progression</p>
            </div>
          </div>

          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={metrics.chart_revenue_timeline}>
                <defs>
                  <linearGradient id="colorRisk" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#EF4444" stopOpacity={0.4} />
                    <stop offset="95%" stopColor="#EF4444" stopOpacity={0} />
                  </linearGradient>
                  <linearGradient id="colorRec" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#10B981" stopOpacity={0.4} />
                    <stop offset="95%" stopColor="#10B981" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <XAxis dataKey="period" stroke="#64748B" fontSize={12} tickLine={false} />
                <YAxis
                  stroke="#64748B"
                  fontSize={12}
                  tickLine={false}
                  tickFormatter={(val) => `₹${(val / 1000).toFixed(0)}k`}
                />
                <Tooltip
                  contentStyle={{ backgroundColor: "#111726", borderColor: "#334155", borderRadius: "8px", color: "#F8FAFC" }}
                  itemStyle={{ color: "#F8FAFC" }}
                  labelStyle={{ color: "#94A3B8" }}
                  formatter={(val: any) => [formatCurrency(Number(val)), ""]}
                />
                <Area type="monotone" dataKey="risk" stroke="#EF4444" fillOpacity={1} fill="url(#colorRisk)" name="Revenue at Risk" />
                <Area type="monotone" dataKey="recovered" stroke="#10B981" fillOpacity={1} fill="url(#colorRec)" name="Recovered Revenue" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Failure Breakdown Pie Chart */}
        <div className="p-6 rounded-xl border border-border bg-surface">
          <h2 className="text-base font-semibold text-white">Recovery by Payment Rail</h2>
          <p className="text-xs text-muted mb-4">Volume recovered across payment methods</p>

          <div className="h-48">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={metrics.chart_recovery_by_method}
                  dataKey="volume"
                  nameKey="method"
                  cx="50%"
                  cy="50%"
                  outerRadius={65}
                  innerRadius={40}
                  paddingAngle={3}
                >
                  {metrics.chart_recovery_by_method.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{ backgroundColor: "#111726", borderColor: "#334155", borderRadius: "8px", color: "#F8FAFC" }}
                  itemStyle={{ color: "#F8FAFC" }}
                  labelStyle={{ color: "#94A3B8" }}
                  formatter={(val: any) => [formatCurrency(Number(val)), "Volume"]}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>

          <div className="grid grid-cols-2 gap-2 mt-2">
            {metrics.chart_recovery_by_method.map((item, idx) => (
              <div key={item.method} className="flex items-center gap-2 text-xs">
                <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: COLORS[idx % COLORS.length] }}></span>
                <span className="text-slate-300">{item.method}</span>
                <span className="text-muted ml-auto font-mono">{formatCurrency(item.volume)}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Failure Reason Breakdown Bar Chart */}
      <div className="p-6 rounded-xl border border-border bg-surface">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-base font-semibold text-white">Failure Code Diagnostic Distribution</h2>
            <p className="text-xs text-muted">Distribution of failure reasons identified by RecoverAI</p>
          </div>
        </div>

        <div className="h-56">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={metrics.chart_recovery_by_reason}>
              <XAxis dataKey="failure_code" stroke="#64748B" fontSize={11} tickLine={false} />
              <YAxis
                stroke="#64748B"
                fontSize={12}
                tickLine={false}
                tickFormatter={(val) => `₹${(val / 1000).toFixed(0)}k`}
              />
              <Tooltip
                contentStyle={{ backgroundColor: "#111726", borderColor: "#334155", borderRadius: "8px", color: "#F8FAFC" }}
                itemStyle={{ color: "#F8FAFC" }}
                labelStyle={{ color: "#94A3B8" }}
                formatter={(val: any) => [formatCurrency(Number(val)), "Volume at Risk"]}
              />
              <Bar dataKey="volume" fill="#3B82F6" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}
