"use client";

import { useState, useEffect, useCallback } from "react";
import Link from "next/link";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Button } from "@/components/ui/button";
import { Switch } from "@/components/ui/switch";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "@/components/ui/dialog";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";
import { Pencil, Trash2 } from "lucide-react";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export interface Competitor {
  id: string;
  name: string;
  slug: string;
  website_url: string | null;
  blog_url: string | null;
  g2_slug: string | null;
  capterra_slug: string | null;
  is_active: boolean;
  created_at: string | null;
  updated_at: string | null;
}

function slugFromName(name: string): string {
  const s = name
    .toLowerCase()
    .trim()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-|-$/g, "");
  return s || "competitor";
}

function truncateUrl(url: string | null, maxLen = 40): string {
  if (!url) return "—";
  return url.length <= maxLen ? url : url.slice(0, maxLen) + "…";
}

export default function ManageCompetitorsPage() {
  const [competitors, setCompetitors] = useState<Competitor[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [deleteTarget, setDeleteTarget] = useState<Competitor | null>(null);
  const [formSaving, setFormSaving] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);
  const [form, setForm] = useState({
    name: "",
    slug: "",
    website_url: "",
    blog_url: "",
    g2_slug: "",
    capterra_slug: "",
  });

  const fetchCompetitors = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(
        `${API_URL}/competitors?include_inactive=true`
      );
      if (!res.ok) throw new Error("Failed to load competitors");
      const data = await res.json();
      setCompetitors(data.competitors ?? []);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to load");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchCompetitors();
  }, [fetchCompetitors]);

  const openAdd = () => {
    setEditingId(null);
    setForm({
      name: "",
      slug: "",
      website_url: "",
      blog_url: "",
      g2_slug: "",
      capterra_slug: "",
    });
    setFormError(null);
    setDialogOpen(true);
  };

  const openEdit = (c: Competitor) => {
    setEditingId(c.id);
    setForm({
      name: c.name,
      slug: c.slug,
      website_url: c.website_url ?? "",
      blog_url: c.blog_url ?? "",
      g2_slug: c.g2_slug ?? "",
      capterra_slug: c.capterra_slug ?? "",
    });
    setFormError(null);
    setDialogOpen(true);
  };

  const handleNameChange = (name: string) => {
    setForm((prev) => ({
      ...prev,
      name,
      ...(editingId ? {} : { slug: slugFromName(name) }),
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setFormSaving(true);
    setFormError(null);
    try {
      const body = {
        name: form.name.trim(),
        slug: form.slug.trim() || undefined,
        website_url: form.website_url.trim() || null,
        blog_url: form.blog_url.trim() || null,
        g2_slug: form.g2_slug.trim() || null,
        capterra_slug: form.capterra_slug.trim() || null,
      };
      if (editingId) {
        const res = await fetch(`${API_URL}/competitors/${editingId}`, {
          method: "PATCH",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            name: body.name,
            website_url: body.website_url,
            blog_url: body.blog_url,
            g2_slug: body.g2_slug,
            capterra_slug: body.capterra_slug,
          }),
        });
        if (!res.ok) {
          const err = await res.json().catch(() => ({}));
          throw new Error(err.detail ?? "Update failed");
        }
        const updated = await res.json();
        setCompetitors((prev) =>
          prev.map((c) => (c.id === editingId ? updated : c))
        );
      } else {
        const res = await fetch(`${API_URL}/competitors`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(body),
        });
        if (!res.ok) {
          const err = await res.json().catch(() => ({}));
          throw new Error(
            Array.isArray(err.detail) ? err.detail[0]?.msg : err.detail ?? "Create failed"
          );
        }
        const created = await res.json();
        setCompetitors((prev) => [...prev, created]);
      }
      setDialogOpen(false);
    } catch (e) {
      setFormError(e instanceof Error ? e.message : "Save failed");
    } finally {
      setFormSaving(false);
    }
  };

  const handleToggleActive = async (c: Competitor) => {
    try {
      const res = await fetch(`${API_URL}/competitors/${c.id}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ is_active: !c.is_active }),
      });
      if (!res.ok) throw new Error("Update failed");
      const updated = await res.json();
      setCompetitors((prev) =>
        prev.map((x) => (x.id === c.id ? updated : x))
      );
    } catch {
      setError("Failed to update active state");
    }
  };

  const confirmDelete = async () => {
    if (!deleteTarget) return;
    try {
      const res = await fetch(`${API_URL}/competitors/${deleteTarget.id}`, {
        method: "DELETE",
      });
      if (!res.ok) throw new Error("Delete failed");
      setCompetitors((prev) =>
        prev.map((c) =>
          c.id === deleteTarget.id ? { ...c, is_active: false } : c
        )
      );
      setDeleteTarget(null);
    } catch {
      setError("Failed to delete");
      setDeleteTarget(null);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-background via-background to-muted/30">
      <header className="border-b border-border/60 bg-background/80 backdrop-blur-sm">
        <div className="container mx-auto px-4 py-6">
          <nav className="mb-2 flex gap-4 text-sm text-muted-foreground">
            <Link href="/" className="hover:text-foreground">
              Dashboard
            </Link>
            <Link href="/digest" className="hover:text-foreground">
              Digest History
            </Link>
            <span className="font-medium text-foreground">Manage Competitors</span>
          </nav>
          <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
            <h1 className="text-2xl font-bold tracking-tight sm:text-3xl">
              Manage Competitors
            </h1>
            <Button onClick={openAdd}>Add Competitor</Button>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8">
        {error && (
          <p className="mb-4 text-sm font-medium text-destructive">{error}</p>
        )}
        {loading ? (
          <p className="text-muted-foreground">Loading…</p>
        ) : (
          <div className="rounded-xl border border-border bg-card">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Name</TableHead>
                  <TableHead>Slug</TableHead>
                  <TableHead>Blog URL</TableHead>
                  <TableHead>G2 Slug</TableHead>
                  <TableHead>Active</TableHead>
                  <TableHead className="text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {competitors.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={6} className="text-center text-muted-foreground">
                      No competitors yet. Add one to get started.
                    </TableCell>
                  </TableRow>
                ) : (
                  competitors.map((c) => (
                    <TableRow
                      key={c.id}
                      className={!c.is_active ? "opacity-60" : undefined}
                    >
                      <TableCell className="font-medium">{c.name}</TableCell>
                      <TableCell className="font-mono text-xs">{c.slug}</TableCell>
                      <TableCell className="max-w-[200px] truncate font-mono text-xs">
                        {truncateUrl(c.blog_url)}
                      </TableCell>
                      <TableCell>{c.g2_slug ?? "—"}</TableCell>
                      <TableCell>
                        <Switch
                          checked={c.is_active}
                          onCheckedChange={() => handleToggleActive(c)}
                        />
                      </TableCell>
                      <TableCell className="text-right">
                        <div className="flex justify-end gap-2">
                          <Button
                            variant="ghost"
                            size="icon"
                            onClick={() => openEdit(c)}
                            aria-label="Edit"
                          >
                            <Pencil className="h-4 w-4" />
                          </Button>
                          <Button
                            variant="ghost"
                            size="icon"
                            onClick={() => setDeleteTarget(c)}
                            aria-label="Delete"
                          >
                            <Trash2 className="h-4 w-4 text-destructive" />
                          </Button>
                        </div>
                      </TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          </div>
        )}
      </main>

      <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle>
              {editingId ? "Edit Competitor" : "Add Competitor"}
            </DialogTitle>
          </DialogHeader>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-2">
              <label
                htmlFor="name"
                className="text-sm font-medium leading-none"
              >
                Name
              </label>
              <input
                id="name"
                type="text"
                value={form.name}
                onChange={(e) => handleNameChange(e.target.value)}
                required
                className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2"
              />
            </div>
            <div className="space-y-2">
              <label
                htmlFor="slug"
                className="text-sm font-medium leading-none"
              >
                Slug
              </label>
              <input
                id="slug"
                type="text"
                value={form.slug}
                onChange={(e) => setForm((p) => ({ ...p, slug: e.target.value }))}
                className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 font-mono text-sm ring-offset-background focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2"
              />
            </div>
            <div className="space-y-2">
              <label
                htmlFor="website_url"
                className="text-sm font-medium leading-none"
              >
                Website URL
              </label>
              <input
                id="website_url"
                type="url"
                value={form.website_url}
                onChange={(e) =>
                  setForm((p) => ({ ...p, website_url: e.target.value }))
                }
                placeholder="https://…"
                className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2"
              />
            </div>
            <div className="space-y-2">
              <label
                htmlFor="blog_url"
                className="text-sm font-medium leading-none"
              >
                Blog URL
              </label>
              <input
                id="blog_url"
                type="url"
                value={form.blog_url}
                onChange={(e) =>
                  setForm((p) => ({ ...p, blog_url: e.target.value }))
                }
                placeholder="https://…"
                className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2"
              />
            </div>
            <div className="space-y-2">
              <label
                htmlFor="g2_slug"
                className="text-sm font-medium leading-none"
              >
                G2 Slug
              </label>
              <input
                id="g2_slug"
                type="text"
                value={form.g2_slug}
                onChange={(e) =>
                  setForm((p) => ({ ...p, g2_slug: e.target.value }))
                }
                className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2"
              />
            </div>
            <div className="space-y-2">
              <label
                htmlFor="capterra_slug"
                className="text-sm font-medium leading-none"
              >
                Capterra Slug
              </label>
              <input
                id="capterra_slug"
                type="text"
                value={form.capterra_slug}
                onChange={(e) =>
                  setForm((p) => ({ ...p, capterra_slug: e.target.value }))
                }
                className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2"
              />
            </div>
            {formError && (
              <p className="text-sm font-medium text-destructive">{formError}</p>
            )}
            <DialogFooter>
              <Button
                type="button"
                variant="outline"
                onClick={() => setDialogOpen(false)}
              >
                Cancel
              </Button>
              <Button type="submit" disabled={formSaving}>
                {formSaving ? "Saving…" : editingId ? "Save" : "Add"}
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>

      <AlertDialog
        open={!!deleteTarget}
        onOpenChange={(open) => !open && setDeleteTarget(null)}
      >
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Delete competitor?</AlertDialogTitle>
            <AlertDialogDescription>
              This will deactivate &quot;{deleteTarget?.name}&quot; (soft delete).
              They will no longer appear in the active list or intel runs.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction
              onClick={confirmDelete}
              className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
            >
              Delete
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
}
