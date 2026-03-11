import Link from "next/link";
import { notFound } from "next/navigation";
import { IntelFeed } from "@/components/IntelFeed";
import { AccountSection } from "@/components/AccountSection";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function getCompetitorBySlug(slug: string): Promise<{ name: string } | null> {
  const res = await fetch(`${API_URL}/competitors`, { cache: "no-store" });
  if (!res.ok) return null;
  const data = await res.json();
  const list = data.competitors ?? [];
  const match = list.find((c: { slug: string }) => c.slug === slug);
  return match ? { name: match.name } : null;
}

interface CompetitorPageProps {
  params: { slug: string };
}

export default async function CompetitorPage({ params }: CompetitorPageProps) {
  const { slug } = params;
  const competitor = await getCompetitorBySlug(slug);
  if (!competitor) notFound();
  const { name } = competitor;

  return (
    <div className="min-h-screen bg-gradient-to-b from-background via-background to-muted/50">
      <header className="gradient-accent border-b border-primary/20 bg-background/90 backdrop-blur-md">
        <div className="container mx-auto px-4 py-6">
          <nav className="mb-2 flex flex-wrap items-center justify-between gap-4 text-sm text-muted-foreground">
            <div className="flex gap-4">
              <Link href="/" className="hover:text-primary transition-colors">
                ← Dashboard
              </Link>
              <Link href="/digest" className="hover:text-primary transition-colors">
                Digest History
              </Link>
              <Link href="/competitors/manage" className="hover:text-primary transition-colors">
                Manage Competitors
              </Link>
            </div>
            <AccountSection />
          </nav>
          <h1 className="text-2xl font-bold tracking-tight sm:text-3xl text-foreground">
            {name}
          </h1>
          <p className="mt-1 text-muted-foreground">
            Competitive intelligence for {name}
          </p>
        </div>
      </header>
      <main className="container mx-auto px-4 py-8">
        <section>
          <h2 className="mb-4 text-lg font-semibold text-foreground">Intel Feed</h2>
          <IntelFeed competitor={name} />
        </section>
      </main>
    </div>
  );
}
