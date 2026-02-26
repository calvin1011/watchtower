import { IntelFeed } from "@/components/IntelFeed";

export default function DashboardPage() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-background via-background to-muted/30">
      <header className="border-b border-border/60 bg-background/80 backdrop-blur-sm">
        <div className="container mx-auto px-4 py-6">
          <h1 className="text-2xl font-bold tracking-tight sm:text-3xl">
            Watchtower
          </h1>
          <p className="mt-1 text-muted-foreground">
            HappyCo Competitive Intelligence Dashboard
          </p>
        </div>
      </header>
      <main className="container mx-auto px-4 py-8">
        <section>
          <h2 className="mb-4 text-lg font-semibold">Intel Feed</h2>
          <IntelFeed />
        </section>
      </main>
    </div>
  );
}
