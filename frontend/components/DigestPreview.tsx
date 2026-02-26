"use client";

import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { Calendar, Mail, FileText } from "lucide-react";

export interface DigestItem {
  id: string;
  week_of: string | null;
  content: Record<string, unknown>;
  sent_at: string | null;
  recipient: string | null;
}

interface DigestPreviewProps {
  digest: DigestItem;
}

function formatDate(iso: string | null): string {
  if (!iso) return "—";
  const d = new Date(iso);
  return d.toLocaleDateString(undefined, {
    weekday: "long",
    month: "long",
    day: "numeric",
    year: "numeric",
  });
}

function getWeekLabel(weekOf: string | null): string {
  if (!weekOf) return "Unknown week";
  const d = new Date(weekOf);
  return `Week of ${d.toLocaleDateString(undefined, {
    month: "short",
    day: "numeric",
    year: "numeric",
  })}`;
}

function getTotalItems(content: Record<string, unknown>): number {
  const total = content?.total_items;
  if (typeof total === "number") return total;
  const grouped = content?.grouped as Record<string, unknown[]> | undefined;
  if (grouped && typeof grouped === "object") {
    return Object.values(grouped).reduce((sum, arr) => sum + (arr?.length ?? 0), 0);
  }
  return 0;
}

export function DigestPreview({ digest }: DigestPreviewProps) {
  const weekLabel = getWeekLabel(digest.week_of);
  const totalItems = getTotalItems(digest.content ?? {});
  const sentDate = formatDate(digest.sent_at);

  return (
    <Card className="border-border">
        <CardHeader className="flex flex-row items-start justify-between pb-2">
          <div className="flex items-center gap-2">
            <FileText className="h-5 w-5 text-muted-foreground" />
            <h3 className="font-semibold">{weekLabel}</h3>
          </div>
        </CardHeader>
        <CardContent className="space-y-2">
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <Calendar className="h-4 w-4 shrink-0" />
            <span>Sent {sentDate}</span>
          </div>
          {digest.recipient && (
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <Mail className="h-4 w-4 shrink-0" />
              <span className="truncate">{digest.recipient}</span>
            </div>
          )}
          <p className="text-sm text-muted-foreground">
            {totalItems} intel item{totalItems !== 1 ? "s" : ""} included
          </p>
        </CardContent>
      </Card>
  );
}
