"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { createClient } from "@/lib/supabase";

export default function SignUpPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      const supabase = createClient();
      const { data, error: signUpError } = await supabase.auth.signUp({
        email,
        password,
        options: { emailRedirectTo: typeof window !== "undefined" ? `${window.location.origin}/` : undefined },
      });
      if (signUpError) {
        setError(signUpError.message);
        return;
      }
      if (data?.user?.identities?.length === 0) {
        setError("An account with this email already exists. Try signing in.");
        return;
      }
      if (data?.session) {
        router.push("/");
        router.refresh();
        return;
      }
      setSuccess(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Sign up failed");
    } finally {
      setLoading(false);
    }
  }

  if (success) {
    return (
      <div className="min-h-screen bg-gradient-to-b from-background via-background to-muted/50">
        <header className="gradient-accent border-b border-primary/20 bg-background/90 backdrop-blur-md">
          <div className="container mx-auto px-4 py-6">
            <nav className="mb-2 flex gap-4 text-sm text-muted-foreground">
              <Link href="/" className="hover:text-primary transition-colors">
                ← Dashboard
              </Link>
            </nav>
            <h1 className="text-2xl font-bold tracking-tight sm:text-3xl text-foreground">
              Watchtower
            </h1>
            <p className="mt-1 text-muted-foreground">
              HappyCo Competitive Intelligence Dashboard
            </p>
          </div>
        </header>
        <main className="container mx-auto flex min-h-[calc(100vh-140px)] flex-col items-center justify-center px-4 py-8">
          <Card className="w-full max-w-md border-primary/20 bg-card/95 shadow-xl shadow-primary/5">
            <CardHeader className="space-y-1">
              <CardTitle className="text-2xl">Check your email</CardTitle>
              <CardDescription>
                We sent a confirmation link to <strong>{email}</strong>. Click the link to activate your account, then sign in.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Link
                href="/login"
                className="inline-flex h-10 w-full items-center justify-center rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground shadow transition-colors hover:bg-primary/90 focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2"
              >
                Go to sign in
              </Link>
            </CardContent>
          </Card>
        </main>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-background via-background to-muted/50">
      <header className="gradient-accent border-b border-primary/20 bg-background/90 backdrop-blur-md">
        <div className="container mx-auto px-4 py-6">
          <nav className="mb-2 flex gap-4 text-sm text-muted-foreground">
            <Link href="/" className="hover:text-primary transition-colors">
              ← Dashboard
            </Link>
          </nav>
          <h1 className="text-2xl font-bold tracking-tight sm:text-3xl text-foreground">
            Watchtower
          </h1>
          <p className="mt-1 text-muted-foreground">
            HappyCo Competitive Intelligence Dashboard
          </p>
        </div>
      </header>
      <main className="container mx-auto flex min-h-[calc(100vh-140px)] flex-col items-center justify-center px-4 py-8">
        <Card className="w-full max-w-md border-primary/20 bg-card/95 shadow-xl shadow-primary/5">
          <CardHeader className="space-y-1">
            <CardTitle className="text-2xl">Create an account</CardTitle>
            <CardDescription>
              Enter your email and a password to sign up
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="space-y-2">
                <label
                  htmlFor="email"
                  className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
                >
                  Email
                </label>
                <input
                  id="email"
                  type="email"
                  placeholder="you@example.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                  autoComplete="email"
                  className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm text-foreground ring-offset-background placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                />
              </div>
              <div className="space-y-2">
                <label
                  htmlFor="password"
                  className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
                >
                  Password
                </label>
                <input
                  id="password"
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  minLength={12}
                  autoComplete="new-password"
                  className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm text-foreground ring-offset-background placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                />
                <p className="text-xs text-muted-foreground">At least 12 characters</p>
              </div>
              {error && (
                <p className="text-sm font-medium text-destructive">{error}</p>
              )}
              <button
                type="submit"
                disabled={loading}
                className="inline-flex h-10 w-full items-center justify-center rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground shadow transition-colors hover:bg-primary/90 focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 disabled:pointer-events-none disabled:opacity-50"
              >
                {loading ? "Creating account…" : "Sign up"}
              </button>
              <p className="text-center text-sm text-muted-foreground">
                Already have an account?{" "}
                <Link href="/login" className="font-medium text-primary underline-offset-4 hover:underline">
                  Sign in
                </Link>
              </p>
            </form>
          </CardContent>
        </Card>
      </main>
    </div>
  );
}
