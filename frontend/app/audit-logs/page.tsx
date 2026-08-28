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
} from "lucide-react";
import { api } from "@/lib/api-client";
import { AuditLogItem } from "@/lib/types";
import { formatDate } from "@/lib/utils";
import { StatusBadge } from "@/components/ui/StatusBadge";

export default function AuditLogsPage() {
  const [logs, setLogs] = useState<AuditLogItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [actorFilter, setActorFilter] = useState("");
  const [expandedLogId, setExpandedLogId] = useState<string | null>(null);

  const fetchLogs = async () => {
    try {
      setLoading(true);
      const params = new URLSearchParams();
      if (actorFilter) params.set("actor_type", actorFilter);
      const res = await api.getAuditLogs(params.toString());
      setLogs(res.items || []);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
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
        return <Bot className="w-3.5 h-3.5 text-blue-400" />;
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
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-white">Immutable Audit Trail</h1>
          <p className="text-sm text-muted mt-0.5">
            Cryptographically structured decision ledger tracking every AI diagnosis, policy check, and financial action.
          </p>
        </div>

        <button
          onClick={fetchLogs}
          className="px-3.5 py-2 rounded-lg border border-border bg-surface hover:bg-surfaceHover text-slate-300 text-sm font-medium flex items-center gap-2 transition self-start"
        >
          <RefreshCw className={loading ? "w-4 h-4 animate-spin" : "w-4 h-4"} />
          Refresh Logs
        </button>
      </div>

      {/* Filter Bar */}
      <div className="p-4 rounded-xl border border-border bg-surface flex items-center gap-3">
        <select
          value={actorFilter}
          onChange={(e) => setActorFilter(e.target.value)}
          className="bg-background border border-border rounded-lg px-3 py-2 text-sm text-slate-300 focus:outline-none focus:border-blue-500"
        >
          <option value="">All Actors</option>
          <option value="AI_AGENT">AI AGENT</option>
          <option value="SYSTEM">SYSTEM</option>
          <option value="MERCHANT">MERCHANT / OPERATOR</option>
        </select>
      </div>

      {/* Audit Log Table */}
      <div className="rounded-xl border border-border bg-surface overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead className="bg-surfaceHover/60 text-muted uppercase text-[11px] font-semibold border-b border-border">
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
            <tbody className="divide-y divide-border">
              {logs.length === 0 ? (
                <tr>
                  <td colSpan={8} className="px-5 py-12 text-center text-muted">
                    No audit records found.
                  </td>
                </tr>
              ) : (
                logs.map((log) => {
                  const isExpanded = expandedLogId === log.id;
                  return (
                    <React.Fragment key={log.id}>
                      <tr
                        onClick={() => toggleExpand(log.id)}
                        className="hover:bg-surfaceHover/40 transition cursor-pointer"
                      >
                        <td className="px-4 py-3 text-muted">
                          {isExpanded ? (
                            <ChevronDown className="w-4 h-4 text-blue-400" />
                          ) : (
                            <ChevronRight className="w-4 h-4" />
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
                            "-"
                          )}
                        </td>
                        <td className="px-5 py-3.5 text-xs text-slate-300 max-w-[240px] truncate">
                          {log.reason || "-"}
                        </td>
                        <td className="px-5 py-3.5 font-mono text-[11px] text-muted">
                          {log.correlation_id}
                        </td>
                      </tr>

                      {isExpanded && (
                        <tr className="bg-background/80">
                          <td colSpan={8} className="p-4 border-b border-border/80">
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
                              <div>
                                <span className="font-semibold text-muted block mb-1">
                                  Input Payload Summary:
                                </span>
                                <pre className="p-3 rounded-lg bg-surface border border-border font-mono text-[11px] text-slate-300 overflow-x-auto">
                                  {JSON.stringify(log.input_summary, null, 2)}
                                </pre>
                              </div>
                              <div>
                                <span className="font-semibold text-muted block mb-1">
                                  Output / Decision Payload:
                                </span>
                                <pre className="p-3 rounded-lg bg-surface border border-border font-mono text-[11px] text-slate-300 overflow-x-auto">
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
