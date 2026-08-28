"use client";

import React, { useState } from "react";
import {
  Play,
  Sparkles,
  Shield,
  Zap,
  CheckCircle2,
  TrendingUp,
  AlertTriangle,
  Clock,
  RefreshCw,
  Sliders,
  Layers,
} from "lucide-react";
import { api } from "@/lib/api-client";
import { SimulationResult } from "@/lib/types";
import { formatCurrency } from "@/lib/utils";
import { StatusBadge } from "@/components/ui/StatusBadge";

export default function SimulationPage() {
  const [running, setRunning] = useState(false);
  const [result, setResult] = useState<SimulationResult | null>(null);
  const [scenarioType, setScenarioType] = useState("predefined_5_scenarios");
  const [batchSize, setBatchSize] = useState(10);
  const [error, setError] = useState<string | null>(null);

  const handleRunSimulation = async () => {
    try {
      setRunning(true);
      setError(null);
      const res = await api.runSimulation({
        scenario_name: scenarioType,
        batch_size: batchSize,
        enable_ai_agent: true,
        enable_policy_engine: true,
      });
      setResult(res);
    } catch (err: any) {
      setError(err.message || "Simulation execution failed.");
    } finally {
      setRunning(false);
    }
  };

  return (
    <div className="space-y-8 max-w-6xl mx-auto pb-12">
      {/* Header */}
      <div>
        <div className="flex items-center gap-2 text-xs font-semibold text-blue-400 uppercase tracking-wider mb-1">
          <Sparkles className="w-4 h-4" />
          <span>Interactive Recovery Sandbox</span>
        </div>
        <h1 className="text-2xl font-bold tracking-tight text-white">
          Autonomous Recovery Simulation Runner
        </h1>
        <p className="text-sm text-muted mt-1">
          Run end-to-end recovery loops across 5 canonical scenarios or batch test sets in Test/Simulation Mode.
        </p>
      </div>

      {/* Configuration Card */}
      <div className="p-6 rounded-xl border border-border bg-surface space-y-6">
        <div className="flex items-center justify-between border-b border-border pb-4">
          <div className="flex items-center gap-2">
            <Sliders className="w-5 h-5 text-blue-400" />
            <h2 className="text-base font-bold text-white">Simulation Setup</h2>
          </div>
          <div className="text-xs text-muted font-mono">Adapter: SIMULATION_PAYMENT_ADAPTER</div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="text-xs font-semibold uppercase tracking-wider text-muted block mb-2">
              Scenario Selection
            </label>
            <div className="space-y-2">
              <label
                className={`p-3 rounded-lg border flex items-center gap-3 cursor-pointer transition ${
                  scenarioType === "predefined_5_scenarios"
                    ? "bg-blue-950/30 border-blue-500/50 text-white"
                    : "bg-background border-border text-slate-300 hover:bg-surfaceHover"
                }`}
              >
                <input
                  type="radio"
                  name="scenario"
                  value="predefined_5_scenarios"
                  checked={scenarioType === "predefined_5_scenarios"}
                  onChange={() => setScenarioType("predefined_5_scenarios")}
                  className="text-blue-600 focus:ring-0"
                />
                <div>
                  <div className="text-xs font-bold">5 Predefined Canonical Scenarios</div>
                  <div className="text-[11px] text-muted">
                    High-value escalation, transient retry, max retry stops, opt-out compliance, fraud block
                  </div>
                </div>
              </label>

              <label
                className={`p-3 rounded-lg border flex items-center gap-3 cursor-pointer transition ${
                  scenarioType === "custom_batch"
                    ? "bg-blue-950/30 border-blue-500/50 text-white"
                    : "bg-background border-border text-slate-300 hover:bg-surfaceHover"
                }`}
              >
                <input
                  type="radio"
                  name="scenario"
                  value="custom_batch"
                  checked={scenarioType === "custom_batch"}
                  onChange={() => setScenarioType("custom_batch")}
                  className="text-blue-600 focus:ring-0"
                />
                <div>
                  <div className="text-xs font-bold">Live Synthetic Batch Ingestion</div>
                  <div className="text-[11px] text-muted">
                    Select a dynamic slice of unprocessed failed transactions
                  </div>
                </div>
              </label>
            </div>
          </div>

          <div className="space-y-4">
            <div>
              <label className="text-xs font-semibold uppercase tracking-wider text-muted block mb-2">
                Batch Size: {batchSize} Transactions
              </label>
              <input
                type="range"
                min={5}
                max={50}
                step={5}
                value={batchSize}
                disabled={scenarioType === "predefined_5_scenarios"}
                onChange={(e) => setBatchSize(Number(e.target.value))}
                className="w-full h-2 bg-background rounded-lg appearance-none cursor-pointer accent-blue-500 disabled:opacity-40"
              />
            </div>

            <div className="p-4 rounded-lg bg-background/50 border border-border text-xs space-y-1.5 text-slate-300">
              <div className="font-semibold text-white">Fintech Guardrails Active:</div>
              <div className="text-muted flex items-center gap-1.5">
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                <span>High-Value Threshold &gt; ₹10,000 escalates to human</span>
              </div>
              <div className="text-muted flex items-center gap-1.5">
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                <span>Opt-out customer notifications strictly blocked</span>
              </div>
              <div className="text-muted flex items-center gap-1.5">
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                <span>Repeated failures (&ge; 2 retries) halted</span>
              </div>
            </div>
          </div>
        </div>

        <div className="pt-2 flex justify-end">
          <button
            disabled={running}
            onClick={handleRunSimulation}
            className="px-6 py-3 rounded-lg bg-blue-600 hover:bg-blue-500 text-white text-sm font-semibold flex items-center gap-2 shadow-xl shadow-blue-500/20 transition disabled:opacity-50"
          >
            {running ? (
              <>
                <RefreshCw className="w-4 h-4 animate-spin" />
                Running Autonomous Recovery Loop...
              </>
            ) : (
              <>
                <Play className="w-4 h-4 fill-white" />
                Run Recovery Simulation
              </>
            )}
          </button>
        </div>
      </div>

      {error && (
        <div className="p-4 rounded-xl border border-rose-800/60 bg-rose-950/20 text-rose-300 text-xs">
          {error}
        </div>
      )}

      {/* Results Section */}
      {result && (
        <div className="space-y-6 animate-in fade-in duration-300">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-bold text-white">Simulation Execution Results</h2>
            <span className="text-xs text-muted font-mono">
              Batch: {result.batch_id} ({result.execution_duration_ms}ms)
            </span>
          </div>

          {/* KPI Output Grid */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="p-4 rounded-xl border border-border bg-surface">
              <span className="text-xs text-muted block mb-1">Evaluated at Risk</span>
              <div className="text-xl font-bold text-white font-mono">
                {formatCurrency(result.revenue_at_risk)}
              </div>
              <span className="text-xs text-muted mt-1 block">
                {result.evaluated_count} failed transactions
              </span>
            </div>

            <div className="p-4 rounded-xl border border-emerald-800/40 bg-emerald-950/20">
              <span className="text-xs text-emerald-300 block mb-1">Recovered Revenue</span>
              <div className="text-xl font-bold text-emerald-400 font-mono">
                {formatCurrency(result.revenue_recovered)}
              </div>
              <span className="text-xs text-emerald-300 mt-1 block">
                {result.recovery_rate}% Recovery Rate ({result.recovered_count} cases)
              </span>
            </div>

            <div className="p-4 rounded-xl border border-blue-800/40 bg-blue-950/20">
              <span className="text-xs text-blue-300 block mb-1">Value-Add vs Baseline</span>
              <div className="text-xl font-bold text-white font-mono">
                +{formatCurrency(result.revenue_recovered - result.baseline_recovered_revenue)}
              </div>
              <span className="text-xs text-blue-300 mt-1 block">
                +{result.value_add_percentage}% uplift vs blind retry
              </span>
            </div>

            <div className="p-4 rounded-xl border border-border bg-surface">
              <span className="text-xs text-muted block mb-1">Policy Governance</span>
              <div className="text-sm font-semibold text-slate-200 mt-1 flex items-center justify-between">
                <span>Escalated:</span>
                <span className="font-mono text-amber-400 font-bold">{result.escalated_count}</span>
              </div>
              <div className="text-sm font-semibold text-slate-200 mt-1 flex items-center justify-between">
                <span>Stopped:</span>
                <span className="font-mono text-rose-400 font-bold">{result.stopped_count}</span>
              </div>
            </div>
          </div>

          {/* Cases Breakdown Table */}
          <div className="rounded-xl border border-border bg-surface overflow-hidden">
            <div className="p-4 border-b border-border font-semibold text-white text-sm">
              Evaluated Cases Breakdown
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm">
                <thead className="bg-surfaceHover/60 text-muted uppercase text-[11px] font-semibold border-b border-border">
                  <tr>
                    <th className="px-5 py-3">Case</th>
                    <th className="px-5 py-3">Amount</th>
                    <th className="px-5 py-3">Failure Reason</th>
                    <th className="px-5 py-3">AI Diagnosis</th>
                    <th className="px-5 py-3">Strategy</th>
                    <th className="px-5 py-3">Policy Outcome</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border">
                  {result.cases.map((c) => (
                    <tr key={c.case_id} className="hover:bg-surfaceHover/40 transition">
                      <td className="px-5 py-3 font-mono text-xs text-white">{c.case_id}</td>
                      <td className="px-5 py-3 font-semibold text-white">
                        {formatCurrency(c.amount)}
                      </td>
                      <td className="px-5 py-3">
                        <span className="font-mono text-[11px] text-rose-400 bg-rose-950/40 px-1.5 py-0.5 rounded border border-rose-900/40">
                          {c.failure_code}
                        </span>
                      </td>
                      <td className="px-5 py-3 text-xs text-slate-300 max-w-[280px]">
                        {c.diagnosis}
                      </td>
                      <td className="px-5 py-3">
                        <span className="font-mono text-xs text-blue-400 bg-blue-950/40 px-2 py-0.5 rounded border border-blue-800/40">
                          {c.recommended_action}
                        </span>
                      </td>
                      <td className="px-5 py-3">
                        <StatusBadge status={c.action_status || c.case_status} size="sm" />
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
