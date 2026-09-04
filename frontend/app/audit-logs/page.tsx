"use client";

import React, { useEffect, useState } from "react";
import {
  FileText,
  Search,
  Filter,
  RefreshCw,
  Shield,
  Bot,
  User,
  Cpu,
  ChevronDown,
  ChevronRight,
  SlidersHorizontal,
  Lock,
} from "lucide-react";
import { api } from "@/lib/api-client";
import { AuditLogItem } from "@/lib/types";
import { formatDate } from "@/lib/utils";
import { StatusBadge } from "@/components/ui/StatusBadge";

export default function AuditLogsPage() {
  const [logs, setLogs] = useState<AuditLogItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [actorFilter, setActorFilter] = useState("");
  const [expandedLogId, setExpandedLogId] = useState<string | null>(null);

  const fetchLogs = async (isManual = false) => {
    try {
      if (isManual) setIsRefreshing(true);
      else setLoading(true);
      const params = new URLSearchParams();
      if (actorFilter) params.set("actor_type", actorFilter);
      const res = await api.getAuditLogs(params.toString());
      setLogs(res.items || []);
    } catch (err) {
      console.error("Failed to fetch audit logs:", err);
    } finally {
      setLoading(false);
      setIsRefreshing(false);
    }
  };

  useEffect(() => {
    fetchLogs();
  }, [actorFilter]);

  const toggleExpand = (id: string) => {
    setExpandedLogId(expandedLogId === id ? null : id);
  };

  const getActorIcon = (type: string) => {
    switch (type) {
      case "AI_AGENT":
        return <Bot className="w-3.5 h-3.5 text-primary" />;
      case "MERCHANT":
      case "ADMIN":
        return <User className="w-3.5 h-3.5 text-amber-400" />;
      default:
        return <Cpu className="w-3.5 h-3.5 text-slate-400" />;
    }
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-2 border-b border-border/40">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[11px] font-medium bg-purple-500/10 text-purple-300 border border-purple-500/20">
              <Lock className="w-3 h-3 text-purple-400" />
              IMMUTABLE AUDIT LEDGER
            </span>
            <span className="text-xs text-muted font-mono">{logs.length} logged events</span>
          </div>
          <h1 className="text-2xl lg:text-3xl font-bold tracking-tight text-white">Audit Trail</h1>
          <p className="text-sm text-muted mt-0.5">
            Cryptographically verifiable record tracking every AI diagnosis, policy check, and autonomous transaction execution.
          </p>
        </div>

        <button
          onClick={() => fetchLogs(true)}
          disabled={isRefreshing || loading}
          className="px-3.5 py-2 rounded-xl border border-borderSubtle bg-surfaceSubtle hover:bg-surfaceHover text-slate-300 text-sm font-medium flex items-center gap-2 transition duration-150 active:scale-[0.98] disabled:opacity-50 self-start focus-ring"
        >
          <RefreshCw className={`w-4 h-4 text-slate-400 ${isRefreshing ? "animate-spin text-primary" : ""}`} />
          <span>{isRefreshing ? "Updating..." : "Refresh Logs"}</span>
        </button>
      </div>

      {/* Filter Bar */}
      <div className="fintech-card p-4 flex items-center gap-3">
        <div className="flex items-center gap-2 text-xs text-muted">
          <SlidersHorizontal className="w-3.5 h-3.5" />
          <span>Filter by Actor:</span>
        </div>
        <select
          value={actorFilter}
          onChange={(e) => setActorFilter(e.target.value)}
          className="bg-slate-950/60 border border-borderSubtle rounded-xl px-3 py-2 text-sm text-slate-300 focus-ring transition duration-150 cursor-pointer"
        >
          <option value="">All Actors</option>
          <option value="AI_AGENT">AI AGENT</option>
          <option value="SYSTEM">SYSTEM</option>
          <option value="MERCHANT">MERCHANT / OPERATOR</option>
        </select>
      </div>

      {/* Audit Log Table */}
      <div className="fintech-card overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead className="bg-surfaceSubtle/80 text-muted uppercase text-[10px] font-mono tracking-wider border-b border-borderSubtle">
              <tr>
                <th className="w-8 px-4 py-3"></th>
                <th className="px-5 py-3.5">Timestamp</th>
                <th className="px-5 py-3.5">Actor</th>
                <th className="px-5 py-3.5">Action</th>
                <th className="px-5 py-3.5">Entity Ref</th>
                <th className="px-5 py-3.5">Policy Result</th>
                <th className="px-5 py-3.5">Reason Summary</th>
                <th className="px-5 py-3.5 font-mono text-xs">Correlation ID</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-borderSubtle">
              {loading && logs.length === 0 ? (
                <tr>
                  <td colSpan={8} className="px-5 py-16 text-center text-muted">
                    <div className="flex flex-col items-center justify-center gap-2">
                      <RefreshCw className="w-6 h-6 text-primary animate-spin" />
                      <span className="text-xs text-slate-400">Loading audit ledger...</span>
                    </div>
                  </td>
                </tr>
              ) : logs.length === 0 ? (
                <tr>
                  <td colSpan={8} className="px-5 py-16 text-center text-muted">
                    <div className="flex flex-col items-center justify-center gap-1.5">
                      <p className="text-sm font-medium text-slate-300">No audit records found</p>
                      <p className="text-xs text-slate-500">Events will appear as actions are evaluated and executed</p>
                    </div>
                  </td>
                </tr>
              ) : (
                logs.map((log) => {
                  const isExpanded = expandedLogId === log.id;
                  return (
                    <React.Fragment key={log.id}>
                      <tr
                        onClick={() => toggleExpand(log.id)}
                        className="hover:bg-surfaceSubtle/50 transition-colors cursor-pointer group"
                      >
                        <td className="px-4 py-3 text-muted">
                          {isExpanded ? (
                            <ChevronDown className="w-4 h-4 text-primary" />
                          ) : (
                            <ChevronRight className="w-4 h-4 text-slate-500 group-hover:text-slate-300" />
                          )}
                        </td>
                        <td className="px-5 py-3.5 font-mono text-xs text-muted">
                          {formatDate(log.timestamp)}
                        </td>
                        <td className="px-5 py-3.5">
                          <div className="flex items-center gap-1.5 font-medium text-xs text-slate-200">
                            {getActorIcon(log.actor_type)}
                            <span>{log.actor_type}</span>
                          </div>
                          <div className="text-[10px] text-muted font-mono">{log.actor_id}</div>
                        </td>
                        <td className="px-5 py-3.5 font-mono text-xs font-semibold text-white">
                          {log.action}
                        </td>
                        <td className="px-5 py-3.5 font-mono text-xs text-slate-300">
                          <div>{log.entity_type}</div>
                          <div className="text-[10px] text-muted">{log.entity_id}</div>
                        </td>
                        <td className="px-5 py-3.5">
                          {log.policy_result ? (
                            <StatusBadge status={log.policy_result} size="sm" />
                          ) : (
                            <span className="text-slate-600 font-mono">-</span>
                          )}
                        </td>
                        <td className="px-5 py-3.5 text-xs text-slate-300 max-w-[240px] truncate">
                          {log.reason || <span className="text-slate-600">-</span>}
                        </td>
                        <td className="px-5 py-3.5 font-mono text-[11px] text-muted">
                          {log.correlation_id}
                        </td>
                      </tr>

                      {isExpanded && (
                        <tr className="bg-slate-950/60">
                          <td colSpan={8} className="p-4 border-b border-borderSubtle">
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
                              <div>
                                <span className="font-semibold text-muted block mb-1">
                                  Input Payload Summary:
                                </span>
                                <pre className="p-3 rounded-xl bg-slate-900 border border-borderSubtle font-mono text-[11px] text-slate-300 overflow-x-auto">
                                  {JSON.stringify(log.input_summary, null, 2)}
                                </pre>
                              </div>
                              <div>
                                <span className="font-semibold text-muted block mb-1">
                                  Output / Decision Payload:
                                </span>
                                <pre className="p-3 rounded-xl bg-slate-900 border border-borderSubtle font-mono text-[11px] text-slate-300 overflow-x-auto">
                                  {JSON.stringify(log.output_summary, null, 2)}
                                </pre>
                              </div>
                            </div>
                          </td>
                        </tr>
                      )}
                    </React.Fragment>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
