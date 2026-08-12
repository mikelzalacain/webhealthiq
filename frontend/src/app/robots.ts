import type { MetadataRoute } from "next";

export default function robots(): MetadataRoute.Robots {
  return {
    rules: {
      userAgent: "*",
      allow: "/",
      disallow: ["/account", "/history", "/reset-password"],
    },
    sitemap: "https://webhealthiq.com/sitemap.xml",
    host: "https://webhealthiq.com",
  };
}
