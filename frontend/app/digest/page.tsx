"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { DigestPreview, DigestItem } from "@/components/DigestPreview";

const API_BASE =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function DigestPage() {
  const [digests, setDigests] = useState<DigestItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    async function fetchDigests() {
      setLoading(true);
      setError(null);
      try {
        const res = await fetch(`${API_BASE}/digest/history?limit=50`);
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const data = await res.json();
        if (!cancelled) setDigests(data.digests ?? []);
      } catch (e) {
        if (!cancelled) {
          setError(e instanceof Error ? e.message : "Failed to load digests");
          setDigests([]);
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    fetchDigests();
    return () => {
      cancelled = true;
    };
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-b from-background via-background to-muted/30">
      <header className="border-b border-border/60 bg-background/80 backdrop-blur-sm">
        <div className="container mx-auto px-4 py-6">
          <nav className="mb-2 flex gap-4 text-sm text-muted-foreground">
            <Link href="/" className="hover:text-foreground">
              ← Dashboard
            </Link>
          </nav>
          <h1 className="text-2xl font-bold tracking-tight sm:text-3xl">
            Digest History
          </h1>
          <p className="mt-1 text-muted-foreground">
            Past Monday morning briefings
          </p>
        </div>
      </header>
      <main className="container mx-auto px-4 py-8">
        <section>
          {loading && (
            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
              {[...Array(6)].map((_, i) => (
                <div
                  key={i}
                  className="animate-pulse rounded-xl border border-border bg-muted/30 p-6"
                >
                  <div className="mb-2 h-5 w-32 rounded bg-muted" />
                  <div className="space-y-2">
                    <div className="h-4 w-full rounded bg-muted" />
                    <div className="h-4 w-3/4 rounded bg-muted" />
                  </div>
                </div>
              ))}
            </div>
          )}

          {error && (
            <div className="rounded-xl border border-destructive/50 bg-destructive/5 p-12 text-center">
              <p className="font-medium text-destructive">Failed to load digests</p>
              <p className="mt-1 text-sm text-muted-foreground">{error}</p>
              <p className="mt-2 text-xs text-muted-foreground">
                Ensure the backend is running at {API_BASE}
              </p>
            </div>
          )}

          {!loading && !error && digests.length === 0 && (
            <div className="rounded-xl border border-border p-12 text-center">
              <p className="text-muted-foreground">No digests yet</p>
              <p className="mt-1 text-sm text-muted-foreground">
                Digests are sent every Monday via POST /digest/send
              </p>
            </div>
          )}

          {!loading && !error && digests.length > 0 && (
            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
              {digests.map((digest) => (
                <DigestPreview key={digest.id} digest={digest} />
              ))}
            </div>
          )}
        </section>
      </main>
    </div>
  );
}
