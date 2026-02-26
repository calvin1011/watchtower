"use client";

type ThreatLevel = "HIGH" | "MEDIUM" | "LOW" | string;

interface ThreatBadgeProps {
  level: ThreatLevel;
  className?: string;
}

const styles: Record<string, string> = {
  HIGH: "bg-red-500/15 text-red-600 dark:text-red-400 border-red-500/30",
  MEDIUM: "bg-amber-500/15 text-amber-600 dark:text-amber-400 border-amber-500/30",
  LOW: "bg-emerald-500/15 text-emerald-600 dark:text-emerald-400 border-emerald-500/30",
};

export function ThreatBadge({ level, className = "" }: ThreatBadgeProps) {
  const normalized = level?.toUpperCase?.() ?? "LOW";
  const style = styles[normalized] ?? styles.LOW;
  const base =
    "inline-flex items-center rounded-md border px-2.5 py-0.5 text-xs font-semibold";

  return (
    <span className={`${base} ${style} ${className}`.trim()}>
      {normalized}
    </span>
  );
}
