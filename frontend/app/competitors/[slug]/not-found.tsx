import Link from "next/link";

export default function CompetitorNotFound() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center gap-4 bg-gradient-to-b from-background via-background to-muted/30">
      <h1 className="text-2xl font-semibold">Competitor not found</h1>
      <p className="text-muted-foreground">
        The competitor you&apos;re looking for doesn&apos;t exist or isn&apos;t tracked.
      </p>
      <Link
        href="/"
        className="rounded-lg border border-border px-4 py-2 text-sm hover:bg-muted"
      >
        ← Back to Dashboard
      </Link>
    </div>
  );
}
