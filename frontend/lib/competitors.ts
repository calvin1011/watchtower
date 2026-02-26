/**
 * Tracked competitors. Must match backend scrapers/competitor_config.py.
 */
export const COMPETITORS = [
  { name: "AppFolio", slug: "appfolio" },
  { name: "Buildium", slug: "buildium" },
  { name: "SmartRent", slug: "smartrent" },
  { name: "Entrata", slug: "entrata" },
] as const;

export function slugToName(slug: string): string | null {
  const c = COMPETITORS.find((c) => c.slug === slug.toLowerCase());
  return c?.name ?? null;
}

export function nameToSlug(name: string): string | null {
  const c = COMPETITORS.find((c) => c.name.toLowerCase() === name.toLowerCase());
  return c?.slug ?? null;
}
