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
  Zap,
  Activity,
  Layers,
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
  CartesianGrid,
} from "recharts";
import { api } from "@/lib/api-client";
import { DashboardMetrics } from "@/lib/types";
import { formatCurrency, formatNumber } from "@/lib/utils";

const PALETTE = ["#6366F1", "#10B981", "#F59E0B", "#8B5CF6", "#EC4899", "#06B6D4"];

// Custom Tooltip component for Recharts with calm fintech styling
function CustomChartTooltip({ active, payload, label }: any) {
  if (active && payload && payload.length) {
    return (
      <div className="rounded-xl border border-white/10 bg-slate-950/95 backdrop-blur-md px-3.5 py-2.5 shadow-xl text-xs space-y-1.5 ring-1 ring-white/5">
        {label && <p className="font-medium text-slate-400 border-b border-white/5 pb-1 mb-1">{label}</p>}
        {payload.map((entry: any, index: number) => (
          <div key={`item-${index}`} className="flex items-center justify-between gap-4">
            <span className="flex items-center gap-1.5 text-slate-300">
              <span className="w-2 h-2 rounded-full shrink-0" style={{ backgroundColor: entry.color || entry.stroke || entry.fill }} />
              <span>{entry.name || entry.dataKey}:</span>
            </span>
            <span className="font-mono font-semibold text-white tabular-nums">
              {formatCurrency(Number(entry.value))}
            </span>
          </div>
        ))}
      </div>
    );
  }
  return null;
}

export default function DashboardPage() {
  const [metrics, setMetrics] = useState<DashboardMetrics | null>(null);
  const [loading, setLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchMetrics = async (isManual = false) => {
    try {
      if (isManual) setIsRefreshing(true);
      else setLoading(true);
      setError(null);
      const data = await api.getDashboardMetrics();
      setMetrics(data);
    } catch (err: any) {
      setError(err.message || "Failed to load dashboard metrics.");
    } finally {
      setLoading(false);
      setIsRefreshing(false);
    }
  };

  useEffect(() => {
    fetchMetrics();
  }, []);

  if (loading && !metrics) {
    return (
      <div className="space-y-8 max-w-7xl mx-auto animate-fade-in">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-2 border-b border-border/40">
          <div className="space-y-2">
            <div className="h-7 w-64 skeleton-shimmer rounded-lg"></div>
            <div className="h-4 w-96 skeleton-shimmer rounded"></div>
          </div>
          <div className="flex gap-3">
            <div className="h-10 w-28 skeleton-shimmer rounded-lg"></div>
            <div className="h-10 w-44 skeleton-shimmer rounded-lg"></div>
          </div>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="fintech-card p-5 h-36 flex flex-col justify-between">
              <div className="h-4 w-28 skeleton-shimmer rounded"></div>
              <div className="h-8 w-40 skeleton-shimmer rounded"></div>
              <div className="h-3 w-32 skeleton-shimmer rounded"></div>
            </div>
          ))}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 fintech-card p-6 h-80 skeleton-shimmer"></div>
          <div className="fintech-card p-6 h-80 skeleton-shimmer"></div>
        </div>
      </div>
    );
  }

  if (error || !metrics) {
    return (
      <div className="max-w-2xl mx-auto mt-12 p-6 rounded-2xl border border-rose-500/30 bg-rose-950/20 backdrop-blur-md shadow-2xl text-rose-200 space-y-4">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-rose-500/20 border border-rose-500/30 flex items-center justify-center text-rose-400">
            <AlertTriangle className="w-5 h-5" />
          </div>
          <div>
            <h2 className="font-semibold text-white">Unable to Connect to Recovery Engine</h2>
            <p className="text-xs text-rose-300/80">The backend service may be initializing or restarting.</p>
          </div>
        </div>
        <p className="text-sm bg-rose-950/40 p-3 rounded-lg border border-rose-900/50 font-mono text-xs text-rose-300 break-all">
          {error}
        </p>
        <button
          onClick={() => fetchMetrics(true)}
          className="px-4 py-2 bg-rose-600 hover:bg-rose-500 text-white rounded-lg text-sm font-medium transition inline-flex items-center gap-2 shadow-lg shadow-rose-900/40"
        >
          <RefreshCw className="w-4 h-4" />
          Retry Connection
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-8 max-w-7xl mx-auto">
      {/* Top Banner & Quick Actions */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-2 border-b border-border/40">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[11px] font-medium bg-primary/10 text-primary border border-primary/20">
              <Zap className="w-3 h-3 text-primary animate-pulse" />
              AUTONOMOUS RECOVERY AGENT
            </span>
            <span className="text-xs text-muted font-mono">POLICY ENGINE v1.2</span>
          </div>
          <h1 className="text-2xl lg:text-3xl font-bold tracking-tight text-white">
            Revenue Recovery Dashboard
          </h1>
          <p className="text-sm text-muted mt-0.5 max-w-2xl">
            Real-time telemetry on payment failure diagnosis, policy-bounded execution, and net financial ROI.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => fetchMetrics(true)}
            disabled={isRefreshing}
            className="px-3.5 py-2 rounded-xl border border-borderSubtle bg-surfaceSubtle hover:bg-surfaceHover text-slate-300 text-sm font-medium flex items-center gap-2 transition duration-150 active:scale-[0.98] disabled:opacity-50 focus-ring"
            title="Refresh dashboard metrics"
          >
            <RefreshCw className={`w-4 h-4 text-slate-400 ${isRefreshing ? "animate-spin text-primary" : ""}`} />
            <span>{isRefreshing ? "Updating..." : "Refresh"}</span>
          </button>
          <Link
            href="/simulation"
            className="px-4 py-2 rounded-xl bg-primary hover:bg-primary-hover text-white text-sm font-medium flex items-center gap-2 shadow-md shadow-primary/20 hover:shadow-primary/30 transition duration-150 active:scale-[0.98] focus-ring"
          >
            <Play className="w-4 h-4 fill-white" />
            <span>Run Recovery Simulation</span>
          </Link>
        </div>
      </div>

      {/* KPI Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
        {/* Revenue at Risk */}
        <div className="fintech-card fintech-card-interactive p-5 relative overflow-hidden group">
          <div className="absolute top-0 left-0 right-0 h-[2px] bg-gradient-to-r from-rose-500/0 via-rose-500 to-rose-500/0 opacity-60 group-hover:opacity-100 transition-opacity"></div>
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold uppercase tracking-wider text-muted">Revenue at Risk</span>
            <div className="w-8 h-8 rounded-lg bg-rose-950/40 border border-rose-800/40 flex items-center justify-center text-rose-400 shadow-sm">
              <AlertTriangle className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-3.5">
            <div className="text-2xl lg:text-3xl font-bold text-white tracking-tight tabular-nums">
              {formatCurrency(metrics.revenue_at_risk)}
            </div>
            <p className="text-xs text-muted mt-1.5 flex items-center gap-1.5">
              <span className="w-1.5 h-1.5 rounded-full bg-rose-400/80"></span>
              <span>From <strong className="text-slate-300 font-mono tabular-nums">{formatNumber(metrics.total_evaluated_transactions)}</strong> evaluated failures</span>
            </p>
          </div>
        </div>

        {/* Recovered Revenue */}
        <div className="fintech-card fintech-card-interactive p-5 relative overflow-hidden group border-emerald-500/20 bg-emerald-950/[0.04]">
          <div className="absolute top-0 left-0 right-0 h-[2px] bg-gradient-to-r from-emerald-500/0 via-emerald-500 to-emerald-500/0 opacity-70 group-hover:opacity-100 transition-opacity"></div>
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold uppercase tracking-wider text-muted">Recovered Revenue</span>
            <div className="w-8 h-8 rounded-lg bg-emerald-950/50 border border-emerald-800/40 flex items-center justify-center text-emerald-400 shadow-sm">
              <TrendingUp className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-3.5">
            <div className="text-2xl lg:text-3xl font-bold text-emerald-400 tracking-tight tabular-nums">
              {formatCurrency(metrics.recovered_revenue)}
            </div>
            <div className="flex items-center gap-1.5 text-xs text-emerald-400 font-medium mt-1.5">
              <ArrowUpRight className="w-3.5 h-3.5 stroke-[2.5]" />
              <span className="font-semibold font-mono tabular-nums">{metrics.recovery_rate}%</span>
              <span className="text-slate-400 font-normal">Recovery Rate</span>
            </div>
          </div>
        </div>

        {/* Net Value-Add vs Baseline */}
        <div className="fintech-card fintech-card-interactive p-5 relative overflow-hidden group border-primary/25 bg-primary/[0.03]">
          <div className="absolute top-0 left-0 right-0 h-[2px] bg-gradient-to-r from-primary/0 via-primary to-primary/0 opacity-80 group-hover:opacity-100 transition-opacity"></div>
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold uppercase tracking-wider text-primary-light">RecoverAI ROI Delta</span>
            <div className="w-8 h-8 rounded-lg bg-primary/20 border border-primary/30 flex items-center justify-center text-primary-light shadow-sm">
              <Sparkles className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-3.5">
            <div className="text-2xl lg:text-3xl font-bold text-white tracking-tight tabular-nums">
              +{formatCurrency(metrics.delta_revenue_gain)}
            </div>
            <p className="text-xs text-slate-300 mt-1.5 flex items-center gap-1.5">
              <span className="w-1.5 h-1.5 rounded-full bg-primary-light"></span>
              <span>Beyond baseline (<strong className="font-mono text-white tabular-nums">{metrics.baseline_recovery_rate}%</strong> benchmark)</span>
            </p>
          </div>
        </div>

        {/* Pending Approvals */}
        <Link
          href="/approvals"
          className="fintech-card fintech-card-interactive p-5 relative overflow-hidden group border-amber-800/40 bg-amber-950/[0.08] hover:border-amber-700/60 transition-all block focus-ring"
        >
          <div className="absolute top-0 left-0 right-0 h-[2px] bg-gradient-to-r from-amber-500/0 via-amber-500 to-amber-500/0 opacity-60 group-hover:opacity-100 transition-opacity"></div>
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold uppercase tracking-wider text-amber-300">Pending Approvals</span>
            <div className="w-8 h-8 rounded-lg bg-amber-950/60 border border-amber-800/60 flex items-center justify-center text-amber-400 group-hover:scale-105 transition-transform">
              <ShieldAlert className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-3.5">
            <div className="text-2xl lg:text-3xl font-bold text-amber-400 tracking-tight tabular-nums">
              {metrics.pending_approvals} Cases
            </div>
            <p className="text-xs text-amber-300/90 mt-1.5 flex items-center justify-between">
              <span>High-value / policy escalated</span>
              <ArrowUpRight className="w-3.5 h-3.5 group-hover:translate-x-0.5 group-hover:-translate-y-0.5 transition-transform" />
            </p>
          </div>
        </Link>
      </div>

      {/* Main Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Timeline Chart */}
        <div className="lg:col-span-2 fintech-card p-6">
          <div className="flex items-center justify-between mb-4 pb-3 border-b border-border/40">
            <div>
              <h2 className="text-base font-semibold text-white flex items-center gap-2">
                <Activity className="w-4 h-4 text-primary" />
                Revenue at Risk vs. Recovered Over Time
              </h2>
              <p className="text-xs text-muted mt-0.5">Weekly rolling financial progression and recovery capture</p>
            </div>
            <div className="flex items-center gap-4 text-xs font-medium">
              <span className="flex items-center gap-1.5 text-slate-300">
                <span className="w-2.5 h-2.5 rounded-full bg-rose-500 shadow-sm shadow-rose-500/50"></span>
                <span>At Risk</span>
              </span>
              <span className="flex items-center gap-1.5 text-slate-300">
                <span className="w-2.5 h-2.5 rounded-full bg-emerald-500 shadow-sm shadow-emerald-500/50"></span>
                <span>Recovered</span>
              </span>
            </div>
          </div>

          <div className="h-64 sm:h-72 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={metrics.chart_revenue_timeline} margin={{ top: 10, right: 10, left: -15, bottom: 0 }}>
                <defs>
                  <linearGradient id="colorRisk" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#EF4444" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#EF4444" stopOpacity={0.0} />
                  </linearGradient>
                  <linearGradient id="colorRec" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#10B981" stopOpacity={0.35} />
                    <stop offset="95%" stopColor="#10B981" stopOpacity={0.0} />
                  </linearGradient>
                </defs>
                <CartesianGrid stroke="rgba(255, 255, 255, 0.04)" strokeDasharray="3 3" vertical={false} />
                <XAxis
                  dataKey="period"
                  stroke="#64748B"
                  fontSize={11}
                  tickLine={false}
                  axisLine={{ stroke: "#334155" }}
                />
                <YAxis
                  stroke="#64748B"
                  fontSize={11}
                  tickLine={false}
                  axisLine={{ stroke: "#334155" }}
                  tickFormatter={(val) => `₹${(val / 1000).toFixed(0)}k`}
                />
                <Tooltip content={<CustomChartTooltip />} />
                <Area
                  type="monotone"
                  dataKey="risk"
                  stroke="#EF4444"
                  strokeWidth={2}
                  fillOpacity={1}
                  fill="url(#colorRisk)"
                  name="Revenue at Risk"
                  isAnimationActive={true}
                  animationDuration={600}
                  animationEasing="ease-out"
                />
                <Area
                  type="monotone"
                  dataKey="recovered"
                  stroke="#10B981"
                  strokeWidth={2}
                  fillOpacity={1}
                  fill="url(#colorRec)"
                  name="Recovered Revenue"
                  isAnimationActive={true}
                  animationDuration={600}
                  animationEasing="ease-out"
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Failure Breakdown Pie Chart */}
        <div className="fintech-card p-6 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-4 pb-3 border-b border-border/40">
              <div>
                <h2 className="text-base font-semibold text-white flex items-center gap-2">
                  <Layers className="w-4 h-4 text-primary" />
                  Recovery by Payment Rail
                </h2>
                <p className="text-xs text-muted mt-0.5">Recovered volume across rails</p>
              </div>
            </div>

            <div className="h-48 w-full flex items-center justify-center">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={metrics.chart_recovery_by_method}
                    dataKey="volume"
                    nameKey="method"
                    cx="50%"
                    cy="50%"
                    outerRadius={68}
                    innerRadius={44}
                    paddingAngle={3}
                  >
                    {metrics.chart_recovery_by_method.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={PALETTE[index % PALETTE.length]} stroke="#0f172a" strokeWidth={2} />
                    ))}
                  </Pie>
                  <Tooltip content={<CustomChartTooltip />} />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="grid grid-cols-1 gap-1.5 mt-3 pt-3 border-t border-border/40">
            {metrics.chart_recovery_by_method.map((item, idx) => (
              <div key={item.method} className="flex items-center justify-between text-xs py-1 px-2 rounded-lg hover:bg-surfaceSubtle transition">
                <span className="flex items-center gap-2 text-slate-300">
                  <span className="w-2.5 h-2.5 rounded-full shadow-sm" style={{ backgroundColor: PALETTE[idx % PALETTE.length] }}></span>
                  <span className="font-medium">{item.method}</span>
                </span>
                <span className="text-slate-200 font-mono font-medium">{formatCurrency(item.volume)}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Failure Reason Breakdown Bar Chart */}
      <div className="fintech-card p-6">
        <div className="flex items-center justify-between mb-4 pb-3 border-b border-border/40">
          <div>
            <h2 className="text-base font-semibold text-white">Failure Code Diagnostic Distribution</h2>
            <p className="text-xs text-muted mt-0.5">Distribution of failure reasons classified by RecoverAI autonomous diagnosis</p>
          </div>
        </div>

        <div className="h-56 sm:h-64 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={metrics.chart_recovery_by_reason} margin={{ top: 10, right: 10, left: -15, bottom: 0 }}>
              <CartesianGrid stroke="rgba(255, 255, 255, 0.04)" strokeDasharray="3 3" vertical={false} />
              <XAxis
                dataKey="failure_code"
                stroke="#64748B"
                fontSize={11}
                tickLine={false}
                axisLine={{ stroke: "#334155" }}
              />
              <YAxis
                stroke="#64748B"
                fontSize={11}
                tickLine={false}
                axisLine={{ stroke: "#334155" }}
                tickFormatter={(val) => `₹${(val / 1000).toFixed(0)}k`}
              />
              <Tooltip content={<CustomChartTooltip />} />
              <Bar
                dataKey="volume"
                name="Volume at Risk"
                fill="#6366F1"
                radius={[6, 6, 0, 0]}
                isAnimationActive={true}
                animationDuration={600}
                animationEasing="ease-out"
              />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}
