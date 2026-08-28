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
} from "lucide-react";
import { api } from "@/lib/api-client";
import { EvaluationReport } from "@/lib/types";
import { formatCurrency, formatNumber } from "@/lib/utils";

export default function AnalyticsPage() {
  const [report, setReport] = useState<EvaluationReport | null>(null);
  const [loading, setLoading] = useState(true);

  const fetchResults = async () => {
    try {
      setLoading(true);
      const res = await api.getEvaluationResults();
      setReport(res);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchResults();
  }, []);

  if (loading && !report) {
    return (
      <div className="flex items-center justify-center min-h-[50vh]">
        <RefreshCw className="w-8 h-8 text-blue-500 animate-spin" />
      </div>
    );
  }

  const ml = report?.model_evaluation;
  const rec = report?.recovery_evaluation;

  return (
    <div className="space-y-8 max-w-6xl mx-auto pb-12">
      {/* Header */}
      <div>
        <div className="flex items-center gap-2 text-xs font-semibold text-blue-400 uppercase tracking-wider mb-1">
          <BarChart3 className="w-4 h-4" />
          <span>Empirical Evaluation & Benchmarks</span>
        </div>
        <h1 className="text-2xl font-bold tracking-tight text-white">
          Model & Financial Recovery Analytics
        </h1>
        <p className="text-sm text-muted mt-1">
          Measurable benchmarks computed directly on held-out test data (never trained on). No fabricated metrics.
        </p>
      </div>

      {/* Financial ROI Uplift Comparison Card */}
      {rec && (
        <div className="p-6 rounded-xl border border-border bg-surface space-y-6">
          <div className="flex items-center justify-between border-b border-border pb-4">
            <div>
              <h2 className="text-base font-bold text-white">Financial Recovery Benchmark vs. Baseline</h2>
              <p className="text-xs text-muted">
                Evaluated on {formatNumber(rec.total_evaluated_transactions)} held-out transaction test cases
              </p>
            </div>
            <div className="px-3 py-1 rounded-full bg-emerald-950/60 border border-emerald-800/60 text-emerald-400 text-xs font-bold font-mono">
              +{rec.impact_delta.relative_improvement_percentage}% NET UPLIFT
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Baseline Strategy */}
            <div className="p-5 rounded-lg border border-border bg-background/50 space-y-3">
              <span className="text-xs font-semibold uppercase tracking-wider text-muted block">
                Baseline Strategy: Blind Retry Once
              </span>
              <div className="text-2xl font-bold text-slate-300 font-mono">
                {formatCurrency(rec.baseline_performance.recovered_revenue)}
              </div>
              <div className="text-xs text-muted">
                Recovery Rate: <span className="text-slate-200 font-bold">{rec.baseline_performance.recovery_rate_pct}%</span>
              </div>
              <div className="text-xs text-rose-400">
                Wasted Retries Incurred: <span className="font-mono">{rec.baseline_performance.wasted_retries} transactions</span>
              </div>
            </div>

            {/* RecoverAI Strategy */}
            <div className="p-5 rounded-lg border border-emerald-800/40 bg-emerald-950/20 space-y-3">
              <span className="text-xs font-semibold uppercase tracking-wider text-emerald-400 block">
                RecoverAI: ML + Agent + Policy Guardrails
              </span>
              <div className="text-2xl font-bold text-emerald-400 font-mono">
                {formatCurrency(rec.recoverai_performance.recovered_revenue)}
              </div>
              <div className="text-xs text-emerald-300">
                Recovery Rate: <span className="text-white font-bold">{rec.recoverai_performance.recovery_rate_pct}%</span>
              </div>
              <div className="text-xs text-emerald-300">
                Wasted Retries Avoided: <span className="font-mono font-bold text-white">{rec.recoverai_performance.avoided_wasteful_retries} transactions</span>
              </div>
            </div>
          </div>

          {/* Value summary bar */}
          <div className="p-4 rounded-lg bg-blue-950/20 border border-blue-800/40 flex flex-wrap items-center justify-between gap-4 text-xs">
            <div>
              <span className="text-blue-300 font-semibold">Net Incremental Revenue Recovered: </span>
              <span className="font-bold text-white font-mono text-sm ml-1">
                +{formatCurrency(rec.impact_delta.additional_revenue_recovered)}
              </span>
            </div>
            <div>
              <span className="text-blue-300 font-semibold">Human Escalation Rate: </span>
              <span className="font-mono text-amber-400 font-bold ml-1">
                {rec.impact_delta.human_escalation_rate_pct}%
              </span>
            </div>
            <div>
              <span className="text-blue-300 font-semibold">Stopped Case Rate: </span>
              <span className="font-mono text-rose-400 font-bold ml-1">
                {rec.impact_delta.stopped_case_rate_pct}%
              </span>
            </div>
          </div>
        </div>
      )}

      {/* Machine Learning Model Performance */}
      {ml && (
        <div className="p-6 rounded-xl border border-border bg-surface space-y-6">
          <div className="flex items-center justify-between border-b border-border pb-4">
            <div>
              <h2 className="text-base font-bold text-white">Recoverability Prediction Model Performance</h2>
              <p className="text-xs text-muted">
                Model: Gradient Boosting Classifier ({ml.model_version}) on held-out test split
              </p>
            </div>
          </div>

          {/* Metric Badges */}
          <div className="grid grid-cols-2 sm:grid-cols-5 gap-4">
            <div className="p-4 rounded-lg bg-background/50 border border-border text-center">
              <span className="text-xs text-muted block mb-1">ROC-AUC</span>
              <span className="text-xl font-bold font-mono text-blue-400">{ml.roc_auc.toFixed(4)}</span>
            </div>
            <div className="p-4 rounded-lg bg-background/50 border border-border text-center">
              <span className="text-xs text-muted block mb-1">Precision</span>
              <span className="text-xl font-bold font-mono text-emerald-400">{ml.precision.toFixed(4)}</span>
            </div>
            <div className="p-4 rounded-lg bg-background/50 border border-border text-center">
              <span className="text-xs text-muted block mb-1">Recall</span>
              <span className="text-xl font-bold font-mono text-emerald-400">{ml.recall.toFixed(4)}</span>
            </div>
            <div className="p-4 rounded-lg bg-background/50 border border-border text-center">
              <span className="text-xs text-muted block mb-1">F1 Score</span>
              <span className="text-xl font-bold font-mono text-purple-400">{ml.f1_score.toFixed(4)}</span>
            </div>
            <div className="p-4 rounded-lg bg-background/50 border border-border text-center">
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
              <div className="grid grid-cols-2 gap-2 text-xs font-mono">
                <div className="p-3 rounded bg-emerald-950/30 border border-emerald-800/40">
                  <span className="text-muted block text-[10px]">TRUE NEGATIVES (TN)</span>
                  <span className="text-base font-bold text-emerald-400">
                    {ml.confusion_matrix.true_negatives}
                  </span>
                  <span className="text-[10px] text-muted block mt-0.5">Correctly avoided</span>
                </div>
                <div className="p-3 rounded bg-rose-950/30 border border-rose-800/40">
                  <span className="text-muted block text-[10px]">FALSE POSITIVES (FP)</span>
                  <span className="text-base font-bold text-rose-400">
                    {ml.confusion_matrix.false_positives}
                  </span>
                  <span className="text-[10px] text-muted block mt-0.5">Wasted attempts</span>
                </div>
                <div className="p-3 rounded bg-amber-950/30 border border-amber-800/40">
                  <span className="text-muted block text-[10px]">FALSE NEGATIVES (FN)</span>
                  <span className="text-base font-bold text-amber-400">
                    {ml.confusion_matrix.false_negatives}
                  </span>
                  <span className="text-[10px] text-muted block mt-0.5">Missed recovery</span>
                </div>
                <div className="p-3 rounded bg-emerald-950/30 border border-emerald-800/40">
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
              <div className="space-y-2 text-xs text-slate-300">
                <div className="p-3 rounded-lg bg-background/50 border border-border">
                  <span className="font-semibold text-rose-400 block mb-1">Why False Positives Matter:</span>
                  <p className="text-slate-400 leading-relaxed">
                    {ml.domain_analysis.why_false_positives_matter}
                  </p>
                </div>
                <div className="p-3 rounded-lg bg-background/50 border border-border">
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
