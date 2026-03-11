import Link from "next/link";
import { IntelFeed } from "@/components/IntelFeed";
import { CompetitorCard } from "@/components/CompetitorCard";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function getActiveCompetitors(): Promise<{ name: string; slug: string; [key: string]: unknown }[]> {
  const res = await fetch(`${API_URL}/competitors`, {
    cache: "no-store",
  });
  if (!res.ok) return [];
  const data = await res.json();
  return data.competitors ?? [];
}

export default async function DashboardPage() {
  const competitors = await getActiveCompetitors();

  return (
    <div className="min-h-screen bg-gradient-to-b from-background via-background to-muted/30">
      <header className="border-b border-border/60 bg-background/80 backdrop-blur-sm">
        <div className="container mx-auto px-4 py-6">
          <nav className="mb-2 flex gap-4 text-sm text-muted-foreground">
            <span className="font-medium text-foreground">Dashboard</span>
            <Link href="/digest" className="hover:text-foreground">
              Digest History
            </Link>
            <Link href="/competitors/manage" className="hover:text-foreground">
              Manage Competitors
            </Link>
          </nav>
          <h1 className="text-2xl font-bold tracking-tight sm:text-3xl">
            Watchtower
          </h1>
          <p className="mt-1 text-muted-foreground">
            HappyCo Competitive Intelligence Dashboard
          </p>
        </div>
      </header>
      <main className="container mx-auto px-4 py-8 space-y-12">
        <section>
          <h2 className="mb-4 text-lg font-semibold">Competitors</h2>
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            {competitors.map((c) => (
              <CompetitorCard key={c.slug} competitor={c} />
            ))}
          </div>
        </section>
        <section>
          <h2 className="mb-4 text-lg font-semibold">Intel Feed</h2>
          <IntelFeed />
        </section>
      </main>
    </div>
  );
}
