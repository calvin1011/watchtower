"use client";

import { useEffect, useState } from "react";

export interface IntelItem {
  id: string;
  competitor: string;
  signal_type: string;
  threat_level: string;
  threat_reason: string;
  summary: string;
  happyco_response: string;
  confidence: number;
  source_url: string | null;
  detected_at: string | null;
  created_at: string | null;
}

interface IntelFeedProps {
  apiUrl?: string;
  limit?: number;
  competitor?: string;
}

function ThreatLevelBadge({ level }: { level: string }) {
  const l = (level || "LOW").toUpperCase();
  const map: Record<string, string> = {
    HIGH: "border-red-500/30 bg-red-500/15 text-red-600 dark:text-red-400",
    MEDIUM: "border-amber-500/30 bg-amber-500/15 text-amber-600 dark:text-amber-400",
    LOW: "border-emerald-500/30 bg-emerald-500/15 text-emerald-600 dark:text-emerald-400",
  };
  const s = map[l] ?? map.LOW;
  return <span className={`rounded-md border px-2.5 py-0.5 text-xs font-semibold ${s}`}>{l}</span>;
}

function formatDate(iso: string | null): string {
  if (!iso) return "";
  const d = new Date(iso);
  return d.toLocaleDateString(undefined, {
    month: "short",
    day: "numeric",
    year: "numeric",
  });
}

function IntelCard({ item }: { item: IntelItem }) {
  return (
    <div className="rounded-xl border border-border bg-card/80 p-4 shadow transition-all hover:border-primary/30 hover:shadow-lg">
      <div className="mb-2 flex flex-wrap items-center justify-between gap-2">
        <h3 className="font-semibold">{item.competitor}</h3>
        <div className="flex items-center gap-2">
          <ThreatLevelBadge level={item.threat_level} />
          <span className="text-xs text-muted-foreground">
            {item.signal_type.replace(/_/g, " ")}
          </span>
        </div>
      </div>
      {item.threat_reason && (
        <p className="mb-2 text-sm text-muted-foreground">{item.threat_reason}</p>
      )}
      <p className="mb-3 text-sm leading-relaxed">{item.summary}</p>
      {item.happyco_response && (
        <div className="mb-3 rounded-lg border border-primary/20 bg-primary/5 p-3">
          <p className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
            HappyCo response
          </p>
          <p className="mt-1 text-sm">{item.happyco_response}</p>
        </div>
      )}
      <div className="flex flex-wrap items-center gap-2 text-xs text-muted-foreground">
        {item.source_url && (
          <a
            href={item.source_url}
            target="_blank"
            rel="noopener noreferrer"
            className="text-primary hover:underline"
          >
            Source →
          </a>
        )}
        <span>{formatDate(item.detected_at || item.created_at)}</span>
        {item.confidence != null && (
          <span>Confidence: {Math.round(item.confidence * 100)}%</span>
        )}
      </div>
    </div>
  );
}

export function IntelFeed({
  apiUrl,
  limit = 50,
  competitor,
}: IntelFeedProps) {
  const [items, setItems] = useState<IntelItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const baseUrl = apiUrl || process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
  const url = competitor
    ? `${baseUrl}/intel/${encodeURIComponent(competitor)}?limit=${limit}`
    : `${baseUrl}/intel?limit=${limit}`;

  useEffect(() => {
    let cancelled = false;

    async function fetchIntel() {
      setLoading(true);
      setError(null);
      try {
        const res = await fetch(url);
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const data = await res.json();
        if (!cancelled) setItems(data.items ?? []);
      } catch (e) {
        if (!cancelled) {
          setError(e instanceof Error ? e.message : "Failed to load intel");
          setItems([]);
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    fetchIntel();
    return () => {
      cancelled = true;
    };
  }, [url]);

  if (loading) {
    return (
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {[...Array(6)].map((_, i) => (
          <div
            key={i}
            className="animate-pulse rounded-xl border border-border bg-muted/30 p-4"
          >
            <div className="mb-2 h-4 w-24 rounded bg-muted" />
            <div className="mb-2 h-3 w-full rounded bg-muted" />
            <div className="space-y-2">
              <div className="h-3 w-full rounded bg-muted" />
              <div className="h-3 w-4/5 rounded bg-muted" />
              <div className="h-3 w-2/3 rounded bg-muted" />
            </div>
          </div>
        ))}
      </div>
    );
  }

  if (error) {
    return (
      <div className="rounded-xl border border-destructive/50 bg-destructive/5 p-12 text-center">
        <p className="font-medium text-destructive">Failed to load intel</p>
        <p className="mt-1 text-sm text-muted-foreground">{error}</p>
        <p className="mt-2 text-xs text-muted-foreground">
          Ensure the backend is running at {baseUrl}
        </p>
      </div>
    );
  }

  if (items.length === 0) {
    return (
      <div className="rounded-xl border border-border p-12 text-center">
        <p className="text-muted-foreground">No intel items yet</p>
        <p className="mt-1 text-sm text-muted-foreground">
          Run the pipeline via POST /intel/run to gather competitive intel
        </p>
      </div>
    );
  }

  return (
    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
      {items.map((item) => (
        <IntelCard key={item.id} item={item} />
      ))}
    </div>
  );
}
