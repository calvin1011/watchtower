import Link from "next/link";
import { notFound } from "next/navigation";
import { IntelFeed } from "@/components/IntelFeed";
import { slugToName } from "@/lib/competitors";

interface CompetitorPageProps {
  params: { slug: string };
}

export default function CompetitorPage({ params }: CompetitorPageProps) {
  const { slug } = params;
  const name = slugToName(slug);
  if (!name) notFound();

  return (
    <div className="min-h-screen bg-gradient-to-b from-background via-background to-muted/30">
      <header className="border-b border-border/60 bg-background/80 backdrop-blur-sm">
        <div className="container mx-auto px-4 py-6">
          <nav className="mb-2 flex gap-4 text-sm text-muted-foreground">
            <Link href="/" className="hover:text-foreground">
              ← Dashboard
            </Link>
            <Link href="/digest" className="hover:text-foreground">
              Digest History
            </Link>
          </nav>
          <h1 className="text-2xl font-bold tracking-tight sm:text-3xl">
            {name}
          </h1>
          <p className="mt-1 text-muted-foreground">
            Competitive intelligence for {name}
          </p>
        </div>
      </header>
      <main className="container mx-auto px-4 py-8">
        <section>
          <h2 className="mb-4 text-lg font-semibold">Intel Feed</h2>
          <IntelFeed competitor={name} />
        </section>
      </main>
    </div>
  );
}
