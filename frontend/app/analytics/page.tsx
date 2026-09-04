"use client";

import React, { useEffect, useState } from "react";
import {
  BarChart3,
  TrendingUp,
  ShieldAlert,
  Sparkles,
  CheckCircle,
  AlertCircle,
  HelpCircle,
  RefreshCw,
  Award,
  Zap,
} from "lucide-react";
import { api } from "@/lib/api-client";
import { EvaluationReport } from "@/lib/types";
import { formatCurrency, formatNumber } from "@/lib/utils";

export default function AnalyticsPage() {
  const [report, setReport] = useState<EvaluationReport | null>(null);
  const [loading, setLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);

  const fetchResults = async (isManual = false) => {
    try {
      if (isManual) setIsRefreshing(true);
      else setLoading(true);
      const res = await api.getEvaluationResults();
      setReport(res);
    } catch (err) {
      console.error("Failed to fetch evaluation analytics:", err);
    } finally {
      setLoading(false);
      setIsRefreshing(false);
    }
  };

  useEffect(() => {
    fetchResults();
  }, []);

  if (loading && !report) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[50vh] gap-3">
        <RefreshCw className="w-8 h-8 text-primary animate-spin" />
        <p className="text-xs text-muted">Calculating empirical test benchmarks on held-out dataset...</p>
      </div>
    );
  }

  const ml = report?.model_evaluation;
  const rec = report?.recovery_evaluation;

  return (
    <div className="space-y-8 max-w-6xl mx-auto pb-12">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-2 border-b border-border/40">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[11px] font-medium bg-primary/10 text-primary border border-primary/20">
              <BarChart3 className="w-3 h-3 text-primary" />
              EMPIRICAL VALIDATION BENCHMARK
            </span>
            <span className="text-xs text-muted font-mono">Held-Out Test Set</span>
          </div>
          <h1 className="text-2xl lg:text-3xl font-bold tracking-tight text-white">
            Model & Financial Recovery Analytics
          </h1>
          <p className="text-sm text-muted mt-1">
            Auditable benchmarks computed directly on held-out evaluation data (never trained on). No fabricated metrics.
          </p>
        </div>

        <button
          onClick={() => fetchResults(true)}
          disabled={isRefreshing || loading}
          className="px-3.5 py-2 rounded-xl border border-borderSubtle bg-surfaceSubtle hover:bg-surfaceHover text-slate-300 text-sm font-medium flex items-center gap-2 transition duration-150 active:scale-[0.98] disabled:opacity-50 self-start focus-ring"
        >
          <RefreshCw className={`w-4 h-4 text-slate-400 ${isRefreshing ? "animate-spin text-primary" : ""}`} />
          <span>{isRefreshing ? "Updating..." : "Recalculate"}</span>
        </button>
      </div>

      {/* Financial ROI Uplift Comparison Card */}
      {rec && (
        <div className="fintech-card p-6 space-y-6">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-borderSubtle pb-4">
            <div>
              <h2 className="text-base font-bold text-white flex items-center gap-2">
                <TrendingUp className="w-4 h-4 text-emerald-400" />
                Financial Recovery Benchmark vs. Baseline
              </h2>
              <p className="text-xs text-muted mt-0.5">
                Evaluated across <strong className="text-slate-300 font-mono">{formatNumber(rec.total_evaluated_transactions)}</strong> held-out transaction test cases
              </p>
            </div>
            <div className="px-3 py-1 rounded-full bg-emerald-950/40 border border-emerald-800/50 text-emerald-400 text-xs font-bold font-mono inline-flex items-center gap-1.5 self-start">
              <Award className="w-3.5 h-3.5" />
              <span>+{rec.impact_delta.relative_improvement_percentage}% NET UPLIFT</span>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Baseline Strategy */}
            <div className="p-5 rounded-xl border border-borderSubtle bg-slate-950/40 space-y-3">
              <span className="text-xs font-semibold uppercase tracking-wider text-muted block">
                Baseline Strategy: Blind Retry Once
              </span>
              <div className="text-2xl font-bold text-slate-300 font-mono tabular-nums">
                {formatCurrency(rec.baseline_performance.recovered_revenue)}
              </div>
              <div className="text-xs text-muted">
                Recovery Rate: <span className="text-slate-200 font-bold font-mono">{rec.baseline_performance.recovery_rate_pct}%</span>
              </div>
              <div className="text-xs text-rose-400">
                Wasted Retries Incurred: <span className="font-mono font-medium">{rec.baseline_performance.wasted_retries} transactions</span>
              </div>
            </div>

            {/* RecoverAI Strategy */}
            <div className="p-5 rounded-xl border border-emerald-800/40 bg-emerald-950/[0.08] space-y-3 relative overflow-hidden">
              <div className="absolute top-0 left-0 right-0 h-[2px] bg-gradient-to-r from-emerald-500/0 via-emerald-500 to-emerald-500/0 opacity-60"></div>
              <span className="text-xs font-semibold uppercase tracking-wider text-emerald-400 block">
                RecoverAI: ML + Agent + Policy Guardrails
              </span>
              <div className="text-2xl font-bold text-emerald-400 font-mono tabular-nums">
                {formatCurrency(rec.recoverai_performance.recovered_revenue)}
              </div>
              <div className="text-xs text-emerald-300">
                Recovery Rate: <span className="text-white font-bold font-mono">{rec.recoverai_performance.recovery_rate_pct}%</span>
              </div>
              <div className="text-xs text-emerald-300">
                Wasted Retries Avoided: <span className="font-mono font-bold text-white">{rec.recoverai_performance.avoided_wasteful_retries} transactions</span>
              </div>
            </div>
          </div>

          {/* Value summary bar */}
          <div className="p-4 rounded-xl bg-primary/[0.04] border border-primary/20 flex flex-wrap items-center justify-between gap-4 text-xs">
            <div>
              <span className="text-primary-light font-medium">Net Incremental Revenue Recovered: </span>
              <span className="font-bold text-white font-mono text-sm ml-1 tabular-nums">
                +{formatCurrency(rec.impact_delta.additional_revenue_recovered)}
              </span>
            </div>
            <div>
              <span className="text-primary-light font-medium">Human Escalation Rate: </span>
              <span className="font-mono text-amber-400 font-bold ml-1">
                {rec.impact_delta.human_escalation_rate_pct}%
              </span>
            </div>
            <div>
              <span className="text-primary-light font-medium">Stopped Case Rate: </span>
              <span className="font-mono text-rose-400 font-bold ml-1">
                {rec.impact_delta.stopped_case_rate_pct}%
              </span>
            </div>
          </div>
        </div>
      )}

      {/* Machine Learning Model Performance */}
      {ml && (
        <div className="fintech-card p-6 space-y-6">
          <div className="flex items-center justify-between border-b border-borderSubtle pb-4">
            <div>
              <h2 className="text-base font-bold text-white flex items-center gap-2">
                <Zap className="w-4 h-4 text-primary" />
                Recoverability Prediction Model Performance
              </h2>
              <p className="text-xs text-muted mt-0.5">
                Model: Gradient Boosting Classifier ({ml.model_version}) evaluated on held-out test split
              </p>
            </div>
          </div>

          {/* Metric Badges */}
          <div className="grid grid-cols-2 sm:grid-cols-5 gap-4">
            <div className="p-4 rounded-xl bg-slate-950/60 border border-borderSubtle text-center">
              <span className="text-xs text-muted block mb-1">ROC-AUC</span>
              <span className="text-xl font-bold font-mono text-primary-light">{ml.roc_auc.toFixed(4)}</span>
            </div>
            <div className="p-4 rounded-xl bg-slate-950/60 border border-borderSubtle text-center">
              <span className="text-xs text-muted block mb-1">Precision</span>
              <span className="text-xl font-bold font-mono text-emerald-400">{ml.precision.toFixed(4)}</span>
            </div>
            <div className="p-4 rounded-xl bg-slate-950/60 border border-borderSubtle text-center">
              <span className="text-xs text-muted block mb-1">Recall</span>
              <span className="text-xl font-bold font-mono text-emerald-400">{ml.recall.toFixed(4)}</span>
            </div>
            <div className="p-4 rounded-xl bg-slate-950/60 border border-borderSubtle text-center">
              <span className="text-xs text-muted block mb-1">F1 Score</span>
              <span className="text-xl font-bold font-mono text-purple-400">{ml.f1_score.toFixed(4)}</span>
            </div>
            <div className="p-4 rounded-xl bg-slate-950/60 border border-borderSubtle text-center">
              <span className="text-xs text-muted block mb-1">False Pos. Rate</span>
              <span className="text-xl font-bold font-mono text-amber-400">
                {(ml.false_positive_rate * 100).toFixed(1)}%
              </span>
            </div>
          </div>

          {/* Confusion Matrix Table */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-3">
              <h3 className="text-xs font-semibold uppercase tracking-wider text-muted">
                Confusion Matrix (Held-out Test Set)
              </h3>
              <div className="grid grid-cols-2 gap-2.5 text-xs font-mono">
                <div className="p-3.5 rounded-xl bg-emerald-950/30 border border-emerald-800/40">
                  <span className="text-muted block text-[10px]">TRUE NEGATIVES (TN)</span>
                  <span className="text-base font-bold text-emerald-400">
                    {ml.confusion_matrix.true_negatives}
                  </span>
                  <span className="text-[10px] text-muted block mt-0.5">Correctly avoided</span>
                </div>
                <div className="p-3.5 rounded-xl bg-rose-950/30 border border-rose-800/40">
                  <span className="text-muted block text-[10px]">FALSE POSITIVES (FP)</span>
                  <span className="text-base font-bold text-rose-400">
                    {ml.confusion_matrix.false_positives}
                  </span>
                  <span className="text-[10px] text-muted block mt-0.5">Wasted attempts</span>
                </div>
                <div className="p-3.5 rounded-xl bg-amber-950/30 border border-amber-800/40">
                  <span className="text-muted block text-[10px]">FALSE NEGATIVES (FN)</span>
                  <span className="text-base font-bold text-amber-400">
                    {ml.confusion_matrix.false_negatives}
                  </span>
                  <span className="text-[10px] text-muted block mt-0.5">Missed recovery</span>
                </div>
                <div className="p-3.5 rounded-xl bg-emerald-950/30 border border-emerald-800/40">
                  <span className="text-muted block text-[10px]">TRUE POSITIVES (TP)</span>
                  <span className="text-base font-bold text-emerald-400">
                    {ml.confusion_matrix.true_positives}
                  </span>
                  <span className="text-[10px] text-muted block mt-0.5">Recovered revenue</span>
                </div>
              </div>
            </div>

            <div className="space-y-3">
              <h3 className="text-xs font-semibold uppercase tracking-wider text-muted">
                Domain-Specific Error Cost Analysis
              </h3>
              <div className="space-y-2.5 text-xs text-slate-300">
                <div className="p-3.5 rounded-xl bg-slate-950/60 border border-borderSubtle">
                  <span className="font-semibold text-rose-400 block mb-1">Why False Positives Matter:</span>
                  <p className="text-slate-400 leading-relaxed">
                    {ml.domain_analysis.why_false_positives_matter}
                  </p>
                </div>
                <div className="p-3.5 rounded-xl bg-slate-950/60 border border-borderSubtle">
                  <span className="font-semibold text-amber-400 block mb-1">Why False Negatives Matter:</span>
                  <p className="text-slate-400 leading-relaxed">
                    {ml.domain_analysis.why_false_negatives_matter}
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
