import React from "react";
import { cn } from "@/lib/utils";

interface StatusBadgeProps {
  status: string;
  className?: string;
  size?: "sm" | "md";
}

export function StatusBadge({ status, className, size = "md" }: StatusBadgeProps) {
  const s = status ? status.toUpperCase() : "UNKNOWN";

  let colorClasses = "bg-slate-800/70 text-slate-300 border-slate-700/60";
  let dotColor = "bg-slate-400";
  let isPulsing = false;

  // Recovery & Case Statuses
  if (["RECOVERED", "SUCCESS", "APPROVED", "CAPTURED"].includes(s)) {
    colorClasses = "bg-emerald-950/25 text-emerald-400 border-emerald-800/40";
    dotColor = "bg-emerald-400";
  } else if (["WAITING_APPROVAL", "SCHEDULED", "ANALYZING", "EXECUTING"].includes(s)) {
    colorClasses = "bg-amber-950/25 text-amber-300 border-amber-800/40";
    dotColor = "bg-amber-400";
    isPulsing = true;
  } else if (["STOPPED", "BLOCKED", "FAILED", "REJECTED"].includes(s)) {
    colorClasses = "bg-rose-950/25 text-rose-400 border-rose-800/40";
    dotColor = "bg-rose-400";
  } else if (["OPEN", "UNPROCESSED"].includes(s)) {
    colorClasses = "bg-slate-800/40 text-slate-300 border-slate-700/50";
    dotColor = "bg-slate-400";
  } else if (["VIP", "HIGH_VALUE"].includes(s)) {
    colorClasses = "bg-purple-950/25 text-purple-300 border-purple-800/40";
    dotColor = "bg-purple-400";
  } else if (["UPI", "CARD", "NETBANKING"].includes(s)) {
    colorClasses = "bg-cyan-950/25 text-cyan-300 border-cyan-800/40";
    dotColor = "bg-cyan-400";
  }

  const sizeClasses = size === "sm" ? "px-2 py-0.5 text-[10px]" : "px-2.5 py-0.5 text-[11px]";

  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 font-medium rounded-full border backdrop-blur-sm transition-colors",
        sizeClasses,
        colorClasses,
        className
      )}
    >
      <span
        className={cn(
          "w-1.5 h-1.5 rounded-full shrink-0",
          dotColor,
          isPulsing && "animate-pulse-subtle"
        )}
      />
      <span className="truncate">{s.replace(/_/g, " ")}</span>
    </span>
  );
}
