import React from "react";
import { cn } from "@/lib/utils";

interface StatusBadgeProps {
  status: string;
  className?: string;
  size?: "sm" | "md";
}

export function StatusBadge({ status, className, size = "md" }: StatusBadgeProps) {
  const s = status ? status.toUpperCase() : "UNKNOWN";

  let colorClasses = "bg-slate-800 text-slate-300 border-slate-700";

  // Recovery & Case Statuses
  if (["RECOVERED", "SUCCESS", "APPROVED", "CAPTURED"].includes(s)) {
    colorClasses = "bg-emerald-950/60 text-emerald-400 border-emerald-800/60";
  } else if (["WAITING_APPROVAL", "SCHEDULED", "ANALYZING", "EXECUTING"].includes(s)) {
    colorClasses = "bg-amber-950/60 text-amber-400 border-amber-800/60";
  } else if (["STOPPED", "BLOCKED", "FAILED", "REJECTED"].includes(s)) {
    colorClasses = "bg-rose-950/60 text-rose-400 border-rose-800/60";
  } else if (["OPEN", "UNPROCESSED"].includes(s)) {
    colorClasses = "bg-blue-950/60 text-blue-400 border-blue-800/60";
  } else if (["VIP", "HIGH_VALUE"].includes(s)) {
    colorClasses = "bg-purple-950/60 text-purple-400 border-purple-800/60";
  } else if (["UPI", "CARD", "NETBANKING"].includes(s)) {
    colorClasses = "bg-cyan-950/60 text-cyan-400 border-cyan-800/60";
  }

  const sizeClasses = size === "sm" ? "px-2 py-0.5 text-xs" : "px-2.5 py-1 text-xs";

  return (
    <span
      className={cn(
        "inline-flex items-center font-medium rounded-full border transition-colors",
        sizeClasses,
        colorClasses,
        className
      )}
    >
      {s.replace(/_/g, " ")}
    </span>
  );
}
