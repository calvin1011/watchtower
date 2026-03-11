"use client";

import Link from "next/link";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { ChevronRight } from "lucide-react";

/** Competitor object from API or passed from parent; at least name and slug. */
export interface CompetitorCardCompetitor {
  name: string;
  slug: string;
  intelCount?: number;
  [key: string]: unknown;
}

interface CompetitorCardProps {
  competitor: CompetitorCardCompetitor;
}

export function CompetitorCard({ competitor }: CompetitorCardProps) {
  const { name, slug, intelCount } = competitor;
  return (
    <Link href={`/competitors/${slug}`}>
      <Card className="group cursor-pointer border-border transition-all hover:border-primary/30 hover:shadow-lg">
        <CardHeader className="flex flex-row items-center justify-between pb-2">
          <h3 className="font-semibold">{name}</h3>
          <ChevronRight className="h-5 w-5 text-muted-foreground transition-transform group-hover:translate-x-1" />
        </CardHeader>
        <CardContent>
          {intelCount != null && (
            <p className="text-sm text-muted-foreground">
              {intelCount} signal{intelCount !== 1 ? "s" : ""} tracked
            </p>
          )}
          <p className="mt-1 text-xs text-muted-foreground">
            View competitive intelligence →
          </p>
        </CardContent>
      </Card>
    </Link>
  );
}
