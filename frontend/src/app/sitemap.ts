import type { MetadataRoute } from "next";

const SITE = "https://webhealthiq.com";

export default function sitemap(): MetadataRoute.Sitemap {
  const lastModified = new Date();
  return [
    { url: SITE, lastModified, changeFrequency: "weekly", priority: 1 },
    { url: `${SITE}/login`, lastModified, changeFrequency: "monthly", priority: 0.5 },
    { url: `${SITE}/register`, lastModified, changeFrequency: "monthly", priority: 0.5 },
    { url: `${SITE}/privacy`, lastModified, changeFrequency: "yearly", priority: 0.4 },
    { url: `${SITE}/terms`, lastModified, changeFrequency: "yearly", priority: 0.4 },
    { url: `${SITE}/cookies`, lastModified, changeFrequency: "yearly", priority: 0.4 },
  ];
}
