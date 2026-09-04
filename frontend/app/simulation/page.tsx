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
  Upload,
  Plus,
  Trash2,
  Download,
  Filter,
  FileSpreadsheet,
  Calendar,
  RotateCcw,
  HelpCircle,
  Lock,
} from "lucide-react";
import { api } from "@/lib/api-client";
import { SimulationResult, CustomTransactionInput } from "@/lib/types";
import { formatCurrency } from "@/lib/utils";
import { StatusBadge } from "@/components/ui/StatusBadge";

export default function SimulationPage() {
  const [running, setRunning] = useState(false);
  const [result, setResult] = useState<SimulationResult | null>(null);
  const [resetModalOpen, setResetModalOpen] = useState(false);
  const [resetLoading, setResetLoading] = useState(false);
  const [resetFeedback, setResetFeedback] = useState<string | null>(null);
  const [explainCase, setExplainCase] = useState<any | null>(null);

  // Tab State: "demo" | "csv" | "manual"
  const [sourceTab, setSourceTab] = useState<"demo" | "csv" | "manual">("demo");

  // Demo config
  const [scenarioType, setScenarioType] = useState("predefined_5_scenarios");
  const [batchSize, setBatchSize] = useState(10);

  // Date Range Filters
  const [startDateFilter, setStartDateFilter] = useState("");
  const [endDateFilter, setEndDateFilter] = useState("");

  // Result Filtering State
  const [statusFilter, setStatusFilter] = useState("ALL");
  const [failureCodeFilter, setFailureCodeFilter] = useState("ALL");

  // Manual Transaction Form
  const [manualRows, setManualRows] = useState<CustomTransactionInput[]>([
    {
      transaction_id: "TXN-MANUAL-001",
      transaction_date: "2026-08-01T10:30:00",
      amount: 1499.0,
      currency: "INR",
      payment_method: "UPI",
      failure_code: "GATEWAY_ERROR",
      retry_attempt: 1,
      customer_opt_out: false,
      risk_flag: false,
    },
  ]);

  const [newTx, setNewTx] = useState<CustomTransactionInput>({
    transaction_id: "",
    transaction_date: "",
    amount: 1499,
    currency: "INR",
    payment_method: "UPI",
    failure_code: "GATEWAY_ERROR",
    retry_attempt: 1,
    customer_opt_out: false,
    risk_flag: false,
  });

  // CSV State
  const [csvRows, setCsvRows] = useState<CustomTransactionInput[]>([]);
  const [csvErrors, setCsvErrors] = useState<string[]>([]);
  const [csvFileName, setCsvFileName] = useState<string | null>(null);

  const [error, setError] = useState<string | null>(null);

  // Download Example CSV Template
  const handleDownloadTemplate = () => {
    const csvContent =
      "transaction_id,transaction_date,amount,currency,payment_method,failure_code,retry_attempt,customer_opt_out,risk_flag\n" +
      "TXN001,2026-08-01T10:30:00,1499,INR,UPI,GATEWAY_ERROR,1,false,false\n" +
      "TXN002,2026-08-05T14:15:00,45000,INR,CARD,GATEWAY_ERROR,1,false,false\n" +
      "TXN003,2026-08-10T09:00:00,2499,INR,UPI,GATEWAY_ERROR,3,false,false\n" +
      "TXN004,2026-08-15T18:45:00,999,INR,CARD,INSUFFICIENT_FUNDS,1,true,false\n" +
      "TXN005,2026-08-20T21:00:00,7999,INR,UPI,FRAUD_SECURITY_BLOCK,1,false,true\n";

    const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.setAttribute("href", url);
    link.setAttribute("download", "recoverai_simulation_template.csv");
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  // CSV Parser
  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setCsvFileName(file.name);

    const reader = new FileReader();
    reader.onload = (event) => {
      const text = event.target?.result as string;
      parseCSV(text);
    };
    reader.readAsText(file);
  };

  const parseCSV = (text: string) => {
    const lines = text.split(/\r?\n/).filter((line) => line.trim() !== "");
    if (lines.length < 2) {
      setCsvErrors(["CSV file must contain a header row and at least one data row."]);
      setCsvRows([]);
      return;
    }

    const headers = lines[0].split(",").map((h) => h.trim().toLowerCase());
    const expectedHeaders = [
      "transaction_id",
      "transaction_date",
      "amount",
      "currency",
      "payment_method",
      "failure_code",
      "retry_attempt",
      "customer_opt_out",
      "risk_flag",
    ];

    const missingHeaders = expectedHeaders.filter((h) => !headers.includes(h));
    if (missingHeaders.length > 0) {
      setCsvErrors([`Missing required CSV column headers: ${missingHeaders.join(", ")}`]);
      setCsvRows([]);
      return;
    }

    const parsed: CustomTransactionInput[] = [];
    const errs: string[] = [];

    for (let i = 1; i < lines.length; i++) {
      const cols = lines[i].split(",").map((c) => c.trim());
      if (cols.length < headers.length) continue;

      const rowObj: any = {};
      headers.forEach((h, idx) => {
        rowObj[h] = cols[idx];
      });

      const rowNum = i + 1;
      const txId = rowObj["transaction_id"];
      const amount = parseFloat(rowObj["amount"]);
      const retry = parseInt(rowObj["retry_attempt"], 10);
      const optOut = rowObj["customer_opt_out"]?.toLowerCase() === "true";
      const risk = rowObj["risk_flag"]?.toLowerCase() === "true";

      if (!txId) {
        errs.push(`Row ${rowNum}: transaction_id is required.`);
      }
      if (isNaN(amount) || amount < 0) {
        errs.push(`Row ${rowNum}: amount must be a non-negative number.`);
      }
      if (isNaN(retry) || retry < 1) {
        errs.push(`Row ${rowNum}: retry_attempt must be an integer >= 1.`);
      }

      if (errs.length === 0 || errs.length < 5) {
        parsed.push({
          transaction_id: txId || `TXN-ROW-${rowNum}`,
          transaction_date: rowObj["transaction_date"] || undefined,
          amount: isNaN(amount) ? 0 : amount,
          currency: rowObj["currency"] || "INR",
          payment_method: rowObj["payment_method"] || "UPI",
          failure_code: rowObj["failure_code"] || "GATEWAY_ERROR",
          retry_attempt: isNaN(retry) ? 1 : retry,
          customer_opt_out: optOut,
          risk_flag: risk,
        });
      }
    }

    setCsvErrors(errs);
    setCsvRows(parsed);
  };

  // Add Manual Entry Row
  const handleAddManualRow = () => {
    if (!newTx.transaction_id.trim()) {
      setError("Please enter a valid Transaction ID.");
      return;
    }
    setManualRows([...manualRows, { ...newTx }]);
    setNewTx({
      transaction_id: "",
      transaction_date: "",
      amount: 1499,
      currency: "INR",
      payment_method: "UPI",
      failure_code: "GATEWAY_ERROR",
      retry_attempt: 1,
      customer_opt_out: false,
      risk_flag: false,
    });
    setError(null);
  };

  const handleRemoveManualRow = (index: number) => {
    setManualRows(manualRows.filter((_, idx) => idx !== index));
  };

  // Trigger Simulation Execution
  const handleRunSimulation = async () => {
    try {
      setRunning(true);
      setError(null);

      let payload: any = {
        enable_ai_agent: true,
        enable_policy_engine: true,
      };

      if (startDateFilter) payload.start_date = startDateFilter;
      if (endDateFilter) payload.end_date = endDateFilter;

      if (sourceTab === "demo") {
        payload.source = "predefined";
        payload.scenario_name = scenarioType;
        payload.batch_size = batchSize;
      } else if (sourceTab === "csv") {
        if (csvRows.length === 0) {
          setError("Please upload a valid CSV file before running simulation.");
          setRunning(false);
          return;
        }
        if (csvErrors.length > 0) {
          setError("Please correct CSV validation errors before running simulation.");
          setRunning(false);
          return;
        }
        payload.source = "custom";
        payload.custom_transactions = csvRows;
      } else if (sourceTab === "manual") {
        if (manualRows.length === 0) {
          setError("Please add at least one manual transaction before running simulation.");
          setRunning(false);
          return;
        }
        payload.source = "custom";
        payload.custom_transactions = manualRows;
      }

      const res = await api.runSimulation(payload);
      setResult(res);
    } catch (err: any) {
      setError(err.message || "Simulation execution failed.");
    } finally {
      setRunning(false);
    }
  };

  const handleResetSimulation = async () => {
    try {
      setResetLoading(true);
      setError(null);
      const res = await api.resetSimulation();
      setResetFeedback(`Simulation data safely reset: ${res.purged_simulation_transactions} simulation transactions purged. Live production records remain protected.`);
      setResult(null);
      setResetModalOpen(false);
    } catch (err: any) {
      setError(err.message || "Failed to reset simulation data.");
    } finally {
      setResetLoading(false);
    }
  };

  // Filtered result cases
  const filteredCases = (result?.cases || []).filter((c) => {
    if (statusFilter !== "ALL" && (c.action_status !== statusFilter && c.case_status !== statusFilter)) {
      return false;
    }
    if (failureCodeFilter !== "ALL" && c.failure_code !== failureCodeFilter) {
      return false;
    }
    return true;
  });

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
          Test RecoverAI against predefined demo scenarios, custom CSV uploads, or manual transaction entries with historical date preservation.
        </p>
      </div>

      {resetFeedback && (
        <div className="p-3.5 rounded-lg bg-emerald-950/40 border border-emerald-800/40 text-emerald-300 text-xs flex items-center justify-between">
          <div className="flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4 text-emerald-400" />
            <span>{resetFeedback}</span>
          </div>
          <button onClick={() => setResetFeedback(null)} className="text-muted hover:text-white">&times;</button>
        </div>
      )}

      {/* Main Configuration Card */}
      <div className="p-6 rounded-xl border border-border bg-surface space-y-6">
        <div className="flex items-center justify-between border-b border-border pb-4">
          <div className="flex items-center gap-2">
            <Sliders className="w-5 h-5 text-blue-400" />
            <h2 className="text-base font-bold text-white">Simulation Setup</h2>
          </div>
          <div className="text-xs text-muted font-mono">Adapter: SIMULATION_PAYMENT_ADAPTER (is_simulation=True)</div>
        </div>

        {/* Data Source Selector Tabs */}
        <div>
          <label className="text-xs font-semibold uppercase tracking-wider text-muted block mb-3">
            Select Data Source
          </label>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            <button
              onClick={() => setSourceTab("demo")}
              className={`p-3.5 rounded-lg border text-left flex items-center gap-3 transition ${
                sourceTab === "demo"
                  ? "bg-blue-950/40 border-blue-500/60 text-white shadow-lg shadow-blue-500/10"
                  : "bg-background/80 border-border text-slate-300 hover:bg-surfaceHover"
              }`}
            >
              <Zap className={`w-5 h-5 ${sourceTab === "demo" ? "text-blue-400" : "text-slate-400"}`} />
              <div>
                <div className="text-xs font-bold">Demo Scenarios</div>
                <div className="text-[11px] text-muted">5 Predefined / Synthetic</div>
              </div>
            </button>

            <button
              onClick={() => setSourceTab("csv")}
              className={`p-3.5 rounded-lg border text-left flex items-center gap-3 transition ${
                sourceTab === "csv"
                  ? "bg-blue-950/40 border-blue-500/60 text-white shadow-lg shadow-blue-500/10"
                  : "bg-background/80 border-border text-slate-300 hover:bg-surfaceHover"
              }`}
            >
              <Upload className={`w-5 h-5 ${sourceTab === "csv" ? "text-blue-400" : "text-slate-400"}`} />
              <div>
                <div className="text-xs font-bold">Upload CSV</div>
                <div className="text-[11px] text-muted">Custom Transaction File</div>
              </div>
            </button>

            <button
              onClick={() => setSourceTab("manual")}
              className={`p-3.5 rounded-lg border text-left flex items-center gap-3 transition ${
                sourceTab === "manual"
                  ? "bg-blue-950/40 border-blue-500/60 text-white shadow-lg shadow-blue-500/10"
                  : "bg-background/80 border-border text-slate-300 hover:bg-surfaceHover"
              }`}
            >
              <Plus className={`w-5 h-5 ${sourceTab === "manual" ? "text-blue-400" : "text-slate-400"}`} />
              <div>
                <div className="text-xs font-bold">Manual Entry</div>
                <div className="text-[11px] text-muted">Form Entry & Preview</div>
              </div>
            </button>
          </div>
        </div>

        {/* Date Range Filtering Options */}
        <div className="p-4 rounded-xl bg-background/50 border border-border space-y-3">
          <div className="flex items-center gap-2 text-xs font-semibold text-white">
            <Calendar className="w-4 h-4 text-blue-400" />
            <span>Optional Date Range Filter (Inclusive Boundary)</span>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="text-[11px] text-muted block mb-1">Start Date (ISO / YYYY-MM-DD)</label>
              <input
                type="date"
                value={startDateFilter}
                onChange={(e) => setStartDateFilter(e.target.value)}
                className="w-full px-3 py-2 text-xs rounded-lg bg-surface border border-border text-white focus:outline-none focus:border-blue-500"
              />
            </div>
            <div>
              <label className="text-[11px] text-muted block mb-1">End Date (ISO / YYYY-MM-DD)</label>
              <input
                type="date"
                value={endDateFilter}
                onChange={(e) => setEndDateFilter(e.target.value)}
                className="w-full px-3 py-2 text-xs rounded-lg bg-surface border border-border text-white focus:outline-none focus:border-blue-500"
              />
            </div>
          </div>
        </div>

        {/* Tab 1: Demo Scenarios View */}
        {sourceTab === "demo" && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="text-xs font-semibold uppercase tracking-wider text-muted block mb-2">
                Scenario Mode
              </label>
              <div className="space-y-2">
                <label
                  className={`p-3 rounded-lg border flex items-center gap-3 cursor-pointer transition ${
                    scenarioType === "predefined_5_scenarios"
                      ? "bg-blue-950/30 border-blue-500/50 text-white"
                      : "bg-background border-border text-slate-300"
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
                      : "bg-background border-border text-slate-300"
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
          </div>
        )}

        {/* Tab 2: Upload CSV View */}
        {sourceTab === "csv" && (
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-white">Upload Custom Transaction CSV</span>
              <button
                onClick={handleDownloadTemplate}
                className="px-3 py-1.5 rounded-lg border border-blue-800/60 bg-blue-950/30 hover:bg-blue-900/40 text-blue-300 text-xs font-semibold flex items-center gap-1.5 transition"
              >
                <Download className="w-3.5 h-3.5" />
                <span>DOWNLOAD CSV TEMPLATE</span>
              </button>
            </div>

            <div className="border-2 border-dashed border-border hover:border-blue-500/50 rounded-xl p-6 text-center bg-background/40 transition">
              <input
                type="file"
                accept=".csv"
                id="csvInput"
                onChange={handleFileUpload}
                className="hidden"
              />
              <label htmlFor="csvInput" className="cursor-pointer space-y-2 block">
                <FileSpreadsheet className="w-8 h-8 text-blue-400 mx-auto" />
                <div className="text-xs font-semibold text-white">
                  {csvFileName ? `Uploaded: ${csvFileName}` : "Click to browse or drop CSV file"}
                </div>
                <div className="text-[11px] text-muted">
                  Required columns: transaction_id, transaction_date, amount, currency, payment_method, failure_code, retry_attempt, customer_opt_out, risk_flag
                </div>
              </label>
            </div>

            {csvErrors.length > 0 && (
              <div className="p-4 rounded-xl border border-rose-800/60 bg-rose-950/20 text-rose-300 text-xs space-y-1">
                <div className="font-bold flex items-center gap-1.5">
                  <AlertTriangle className="w-4 h-4 text-rose-400" />
                  <span>CSV Validation Errors ({csvErrors.length}):</span>
                </div>
                <ul className="list-disc list-inside space-y-0.5 font-mono text-[11px]">
                  {csvErrors.map((err, i) => (
                    <li key={i}>{err}</li>
                  ))}
                </ul>
              </div>
            )}

            {csvRows.length > 0 && csvErrors.length === 0 && (
              <div className="p-3 rounded-lg border border-emerald-800/40 bg-emerald-950/20 text-emerald-300 text-xs flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                  <span>CSV Validated Successfully: {csvRows.length} custom transactions parsed.</span>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Tab 3: Manual Entry View */}
        {sourceTab === "manual" && (
          <div className="space-y-6">
            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3 p-4 rounded-xl bg-background/50 border border-border">
              <div>
                <label className="text-[11px] text-muted block mb-1">Transaction ID *</label>
                <input
                  type="text"
                  placeholder="TXN-001"
                  value={newTx.transaction_id}
                  onChange={(e) => setNewTx({ ...newTx, transaction_id: e.target.value })}
                  className="w-full px-3 py-1.5 text-xs rounded bg-surface border border-border text-white focus:outline-none focus:border-blue-500"
                />
              </div>

              <div>
                <label className="text-[11px] text-muted block mb-1">Transaction Date</label>
                <input
                  type="datetime-local"
                  value={newTx.transaction_date}
                  onChange={(e) => setNewTx({ ...newTx, transaction_date: e.target.value })}
                  className="w-full px-3 py-1.5 text-xs rounded bg-surface border border-border text-white focus:outline-none focus:border-blue-500"
                />
              </div>

              <div>
                <label className="text-[11px] text-muted block mb-1">Amount (₹) *</label>
                <input
                  type="number"
                  min={0}
                  value={newTx.amount}
                  onChange={(e) => setNewTx({ ...newTx, amount: parseFloat(e.target.value) || 0 })}
                  className="w-full px-3 py-1.5 text-xs rounded bg-surface border border-border text-white focus:outline-none focus:border-blue-500"
                />
              </div>

              <div>
                <label className="text-[11px] text-muted block mb-1">Payment Method</label>
                <select
                  value={newTx.payment_method}
                  onChange={(e) => setNewTx({ ...newTx, payment_method: e.target.value })}
                  className="w-full px-3 py-1.5 text-xs rounded bg-surface border border-border text-white focus:outline-none focus:border-blue-500"
                >
                  <option value="UPI">UPI</option>
                  <option value="CARD">CARD</option>
                  <option value="NETBANKING">NETBANKING</option>
                  <option value="WALLET">WALLET</option>
                </select>
              </div>

              <div>
                <label className="text-[11px] text-muted block mb-1">Failure Code</label>
                <select
                  value={newTx.failure_code}
                  onChange={(e) => setNewTx({ ...newTx, failure_code: e.target.value })}
                  className="w-full px-3 py-1.5 text-xs rounded bg-surface border border-border text-white focus:outline-none focus:border-blue-500"
                >
                  <option value="GATEWAY_ERROR">GATEWAY_ERROR</option>
                  <option value="INSUFFICIENT_FUNDS">INSUFFICIENT_FUNDS</option>
                  <option value="NETWORK_TIMEOUT">NETWORK_TIMEOUT</option>
                  <option value="EXPIRED_CARD">EXPIRED_CARD</option>
                  <option value="FRAUD_SECURITY_BLOCK">FRAUD_SECURITY_BLOCK</option>
                  <option value="USER_DROPPED">USER_DROPPED</option>
                </select>
              </div>

              <div>
                <label className="text-[11px] text-muted block mb-1">Retry Attempt</label>
                <input
                  type="number"
                  min={1}
                  max={5}
                  value={newTx.retry_attempt}
                  onChange={(e) => setNewTx({ ...newTx, retry_attempt: parseInt(e.target.value, 10) || 1 })}
                  className="w-full px-3 py-1.5 text-xs rounded bg-surface border border-border text-white focus:outline-none focus:border-blue-500"
                />
              </div>

              <div className="flex items-center gap-4 pt-4">
                <label className="flex items-center gap-1.5 text-xs text-slate-300 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={newTx.customer_opt_out}
                    onChange={(e) => setNewTx({ ...newTx, customer_opt_out: e.target.checked })}
                    className="rounded text-blue-600"
                  />
                  <span>Opt-out</span>
                </label>

                <label className="flex items-center gap-1.5 text-xs text-slate-300 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={newTx.risk_flag}
                    onChange={(e) => setNewTx({ ...newTx, risk_flag: e.target.checked })}
                    className="rounded text-rose-600"
                  />
                  <span>Risk Flag</span>
                </label>
              </div>

              <div className="pt-2 sm:col-span-2 lg:col-span-1 flex items-end">
                <button
                  onClick={handleAddManualRow}
                  className="w-full py-1.5 rounded bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold flex items-center justify-center gap-1.5 transition"
                >
                  <Plus className="w-3.5 h-3.5" />
                  <span>Add Transaction</span>
                </button>
              </div>
            </div>

            {/* Manual Entry Preview Table */}
            {manualRows.length > 0 && (
              <div className="rounded-xl border border-border bg-surface overflow-hidden">
                <div className="p-3 border-b border-border text-xs font-semibold text-white flex items-center justify-between">
                  <span>Manual Transactions Preview ({manualRows.length})</span>
                </div>
                <div className="overflow-x-auto">
                  <table className="w-full text-left text-xs">
                    <thead className="bg-surfaceHover/60 text-muted uppercase text-[10px] font-semibold border-b border-border">
                      <tr>
                        <th className="px-4 py-2">ID</th>
                        <th className="px-4 py-2">Date</th>
                        <th className="px-4 py-2">Amount</th>
                        <th className="px-4 py-2">Method</th>
                        <th className="px-4 py-2">Failure Code</th>
                        <th className="px-4 py-2">Retry</th>
                        <th className="px-4 py-2">Opt-out</th>
                        <th className="px-4 py-2">Risk</th>
                        <th className="px-4 py-2">Action</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-border font-mono">
                      {manualRows.map((r, idx) => (
                        <tr key={idx} className="hover:bg-surfaceHover/30">
                          <td className="px-4 py-2 text-white font-bold">{r.transaction_id}</td>
                          <td className="px-4 py-2 text-slate-300">{r.transaction_date || "Now"}</td>
                          <td className="px-4 py-2 text-emerald-400">{formatCurrency(r.amount)}</td>
                          <td className="px-4 py-2 text-blue-300">{r.payment_method}</td>
                          <td className="px-4 py-2 text-rose-300">{r.failure_code}</td>
                          <td className="px-4 py-2 text-slate-300">{r.retry_attempt}</td>
                          <td className="px-4 py-2 text-slate-300">{r.customer_opt_out ? "YES" : "NO"}</td>
                          <td className="px-4 py-2 text-slate-300">{r.risk_flag ? "YES" : "NO"}</td>
                          <td className="px-4 py-2">
                            <button
                              onClick={() => handleRemoveManualRow(idx)}
                              className="text-rose-400 hover:text-rose-300 p-1"
                            >
                              <Trash2 className="w-3.5 h-3.5" />
                            </button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Action Controls */}
        <div className="pt-4 border-t border-border flex items-center justify-between flex-wrap gap-4">
          <div className="text-xs text-muted font-mono flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4 text-emerald-400" />
            <span>Policy Engine Authoritative • Advisory AI • Simulation Isolation Enforced</span>
          </div>

          <div className="flex items-center gap-3">
            <button
              disabled={running || resetLoading}
              onClick={() => setResetModalOpen(true)}
              className="px-4 py-3 rounded-lg border border-rose-800/60 bg-rose-950/30 hover:bg-rose-900/40 text-rose-300 text-xs font-semibold flex items-center gap-2 transition disabled:opacity-50"
            >
              <RotateCcw className="w-4 h-4" />
              RESET SIMULATION DATA
            </button>

            <button
              disabled={running || resetLoading}
              onClick={handleRunSimulation}
              className="px-6 py-3 rounded-lg bg-blue-600 hover:bg-blue-500 text-white text-sm font-semibold flex items-center gap-2 shadow-xl shadow-blue-500/20 transition disabled:opacity-50"
            >
              {running ? (
                <>
                  <RefreshCw className="w-4 h-4 animate-spin" />
                  Running Autonomous Recovery Simulation...
                </>
              ) : (
                <>
                  <Play className="w-4 h-4 fill-white" />
                  RUN CUSTOM SIMULATION
                </>
              )}
            </button>
          </div>
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
          <div className="flex items-center justify-between flex-wrap gap-4">
            <div>
              <h2 className="text-lg font-bold text-white">Simulation Execution Results</h2>
              <span className="text-xs text-muted font-mono">
                Batch: {result.batch_id} ({result.execution_duration_ms}ms)
              </span>
            </div>

            {/* Filter Bar */}
            <div className="flex items-center gap-3">
              <div className="flex items-center gap-1.5 text-xs text-muted">
                <Filter className="w-3.5 h-3.5" />
                <span>Filter:</span>
              </div>
              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                className="px-2.5 py-1 text-xs rounded bg-surface border border-border text-white focus:outline-none"
              >
                <option value="ALL">All Outcomes</option>
                <option value="ESCALATED_TO_HUMAN">Escalated</option>
                <option value="STOPPED_BY_POLICY">Stopped</option>
                <option value="SUCCESS">Success</option>
              </select>

              <select
                value={failureCodeFilter}
                onChange={(e) => setFailureCodeFilter(e.target.value)}
                className="px-2.5 py-1 text-xs rounded bg-surface border border-border text-white focus:outline-none"
              >
                <option value="ALL">All Failures</option>
                <option value="GATEWAY_ERROR">GATEWAY_ERROR</option>
                <option value="INSUFFICIENT_FUNDS">INSUFFICIENT_FUNDS</option>
                <option value="FRAUD_SECURITY_BLOCK">FRAUD_SECURITY_BLOCK</option>
                <option value="USER_DROPPED">USER_DROPPED</option>
              </select>
            </div>
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
            <div className="p-4 border-b border-border font-semibold text-white text-sm flex items-center justify-between">
              <span>Evaluated Cases Breakdown ({filteredCases.length} shown)</span>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm">
                <thead className="bg-surfaceHover/60 text-muted uppercase text-[11px] font-semibold border-b border-border">
                  <tr>
                    <th className="px-5 py-3">Case ID</th>
                    <th className="px-5 py-3">Tx ID & Date</th>
                    <th className="px-5 py-3">Amount</th>
                    <th className="px-5 py-3">Failure Reason</th>
                    <th className="px-5 py-3">AI Strategy</th>
                    <th className="px-5 py-3">Policy Outcome</th>
                    <th className="px-5 py-3">Explainability</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border">
                  {filteredCases.map((c) => (
                    <tr key={c.case_id} className="hover:bg-surfaceHover/40 transition">
                      <td className="px-5 py-3 font-mono text-xs text-white">{c.case_id}</td>
                      <td className="px-5 py-3">
                        <div className="font-mono text-xs text-white font-bold">{c.transaction_id}</div>
                        <div className="text-[11px] text-muted font-mono">
                          {c.transaction_date || c.created_at || "N/A"}
                        </div>
                      </td>
                      <td className="px-5 py-3 font-semibold text-white">
                        {formatCurrency(c.amount)}
                      </td>
                      <td className="px-5 py-3">
                        <span className="font-mono text-[11px] text-rose-400 bg-rose-950/40 px-1.5 py-0.5 rounded border border-rose-900/40">
                          {c.failure_code}
                        </span>
                      </td>
                      <td className="px-5 py-3">
                        <span className="font-mono text-xs text-blue-400 bg-blue-950/40 px-2 py-0.5 rounded border border-blue-800/40">
                          {c.recommended_action}
                        </span>
                      </td>
                      <td className="px-5 py-3">
                        <StatusBadge status={c.action_status || c.case_status} size="sm" />
                      </td>
                      <td className="px-5 py-3">
                        <button
                          onClick={() => setExplainCase(c)}
                          className="px-2.5 py-1 rounded bg-blue-950/40 hover:bg-blue-900/40 border border-blue-800/50 text-blue-300 text-xs font-medium flex items-center gap-1 transition"
                        >
                          <HelpCircle className="w-3 h-3 text-blue-400" />
                          <span>Why this action?</span>
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* Reset Simulation Confirmation Modal */}
      {resetModalOpen && (
        <div className="fixed inset-0 z-50 bg-black/75 backdrop-blur-sm flex items-center justify-center p-4 animate-in fade-in duration-200">
          <div className="bg-surface border border-border rounded-xl max-w-md w-full p-6 space-y-4 shadow-2xl">
            <div className="flex items-center gap-2 text-rose-400 font-bold text-base">
              <RotateCcw className="w-5 h-5" />
              <h3>Reset Simulation Data?</h3>
            </div>

            <div className="space-y-2 text-xs text-slate-300">
              <p className="p-3 rounded bg-background/60 border border-border">
                Only simulation records (<span className="font-mono text-amber-300 font-bold">is_simulation=True</span>) will be purged.
              </p>
              <p className="text-emerald-400 font-semibold flex items-center gap-1.5">
                <CheckCircle2 className="w-4 h-4" />
                Live production records and financial metrics will NOT be modified.
              </p>
            </div>

            <div className="flex items-center justify-end gap-3 pt-3">
              <button
                disabled={resetLoading}
                onClick={() => setResetModalOpen(false)}
                className="px-3.5 py-1.5 rounded-lg border border-border text-slate-300 text-xs hover:bg-surfaceHover transition"
              >
                Cancel
              </button>
              <button
                disabled={resetLoading}
                onClick={handleResetSimulation}
                className="px-4 py-2 rounded-lg bg-rose-600 hover:bg-rose-500 text-white text-xs font-semibold shadow-lg shadow-rose-500/20 transition flex items-center gap-1.5"
              >
                {resetLoading ? (
                  <>
                    <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                    Resetting...
                  </>
                ) : (
                  "Confirm Simulation Reset"
                )}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Row-Level Explainability Modal */}
      {explainCase && (
        <div className="fixed inset-0 z-50 bg-black/75 backdrop-blur-sm flex items-center justify-center p-4 animate-in fade-in duration-200">
          <div className="bg-surface border border-border rounded-xl max-w-lg w-full p-6 space-y-4 shadow-2xl">
            <div className="flex items-center justify-between border-b border-border pb-3">
              <div className="flex items-center gap-2">
                <HelpCircle className="w-5 h-5 text-blue-400" />
                <h3 className="text-base font-bold text-white">Why Did RecoverAI Do This?</h3>
              </div>
              <button
                onClick={() => setExplainCase(null)}
                className="text-muted hover:text-white text-lg font-bold"
              >
                &times;
              </button>
            </div>

            <div className="space-y-3 text-xs">
              <div className="p-3 rounded-lg bg-background/50 border border-border flex justify-between">
                <span className="text-muted">Transaction ID:</span>
                <span className="font-mono font-bold text-white">{explainCase.transaction_id}</span>
              </div>

              <div className="p-3 rounded-lg bg-blue-950/30 border border-blue-800/40 space-y-1">
                <span className="font-bold text-blue-300 block">AI Diagnostic Proposal (Advisory)</span>
                <p className="text-slate-200 leading-relaxed">{explainCase.diagnosis}</p>
                <div className="pt-1 text-[11px] text-blue-300 font-mono">
                  Recommendation: {explainCase.recommended_action} | Score: {explainCase.recovery_score?.toFixed(1)}/100
                </div>
              </div>

              <div className="p-3 rounded-lg bg-purple-950/30 border border-purple-800/40 space-y-1">
                <span className="font-bold text-purple-300 block">Deterministic Policy Engine Decision (Authoritative)</span>
                <div className="text-slate-200">
                  Policy Status: <span className="font-mono font-bold text-amber-300">{explainCase.action_status || explainCase.case_status}</span>
                </div>
                <p className="text-slate-400 text-[11px] mt-1">
                  {explainCase.amount >= 10000
                    ? "Transaction amount (>= ₹10,000) triggered mandatory human approval escalation."
                    : explainCase.customer_opt_out
                    ? "Customer communication opt-out blocked external engagement."
                    : explainCase.failure_code === "FRAUD_SECURITY_BLOCK"
                    ? "Security/fraud block detected by issuer; recovery halted."
                    : explainCase.retry_attempt > 2
                    ? "Exceeded maximum retry attempts (2); recovery stopped."
                    : "All deterministic policy rules satisfied; action authorized for execution."}
                </p>
              </div>
            </div>

            <div className="pt-2 border-t border-border flex justify-end">
              <button
                onClick={() => setExplainCase(null)}
                className="px-4 py-2 rounded-lg bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold"
              >
                Close Explanation
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
