import type { Metadata } from "next";
import { Syne, Figtree, IBM_Plex_Mono } from "next/font/google";
import "./globals.css";
import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";
import { LanguageProvider } from "@/lib/i18n/LanguageProvider";
import { AuthProvider } from "@/lib/AuthProvider";
import { FAVICON_32, ICON_64, ICON_192, LOGO_SRC } from "@/lib/brandAssets";

const syne = Syne({
  variable: "--font-display",
  subsets: ["latin"],
  display: "swap",
});

const figtree = Figtree({
  variable: "--font-body",
  subsets: ["latin"],
  display: "swap",
});

const plexMono = IBM_Plex_Mono({
  variable: "--font-mono",
  subsets: ["latin"],
  weight: ["400", "500"],
  display: "swap",
});

const siteUrl = "https://webhealthiq.com";
const title = "WebHealthIQ — Auditorías web inteligentes y automatizadas";
const description =
  "Audita automáticamente SEO, rendimiento, accesibilidad, seguridad y RGPD de tu web. Informes claros, puntuación 0–100 y recomendaciones accionables en minutos.";

export const metadata: Metadata = {
  metadataBase: new URL(siteUrl),
  title: {
    default: title,
    template: "%s · WebHealthIQ",
  },
  description,
  applicationName: "WebHealthIQ",
  authors: [{ name: "WebHealthIQ", url: siteUrl }],
  creator: "WebHealthIQ",
  keywords: [
    "auditoría web",
    "SEO",
    "rendimiento",
    "accesibilidad",
    "seguridad",
    "RGPD",
    "WebHealthIQ",
  ],
  alternates: {
    canonical: siteUrl,
  },
  robots: {
    index: true,
    follow: true,
    googleBot: { index: true, follow: true },
  },
  openGraph: {
    type: "website",
    locale: "es_ES",
    url: siteUrl,
    siteName: "WebHealthIQ",
    title,
    description,
    images: [
      {
        url: "/og.png?v=20260812c",
        width: 1200,
        height: 630,
        alt: "WebHealthIQ — Auditorías web inteligentes",
      },
    ],
  },
  twitter: {
    card: "summary_large_image",
    title,
    description,
    images: ["/og.png?v=20260812c"],
  },
  icons: {
    icon: [
      { url: "/favicon.ico?v=20260812d", sizes: "any" },
      { url: FAVICON_32, type: "image/png", sizes: "32x32" },
      { url: ICON_64, type: "image/png", sizes: "64x64" },
      { url: LOGO_SRC, type: "image/png", sizes: "512x512" },
    ],
    apple: [{ url: ICON_192, sizes: "192x192" }],
    shortcut: [FAVICON_32],
  },
};

const jsonLd = {
  "@context": "https://schema.org",
  "@type": "SoftwareApplication",
  name: "WebHealthIQ",
  applicationCategory: "BusinessApplication",
  operatingSystem: "Web",
  url: siteUrl,
  description,
  offers: {
    "@type": "Offer",
    price: "0",
    priceCurrency: "EUR",
  },
  publisher: {
    "@type": "Organization",
    name: "WebHealthIQ",
    url: siteUrl,
    email: "hello@webhealthiq.com",
    logo: `${siteUrl}${LOGO_SRC}`,
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html
      lang="es"
      className={`${syne.variable} ${figtree.variable} ${plexMono.variable} h-full antialiased`}
    >
      <head>
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
        />
      </head>
      <body className="min-h-full flex flex-col selection:bg-primary/20 bg-mesh">
        <a href="#main-content" className="skip-link">
          Saltar al contenido
        </a>
        <LanguageProvider>
          <AuthProvider>
            <Navbar />
            <main id="main-content" className="flex-1" tabIndex={-1}>
              {children}
            </main>
            <Footer />
          </AuthProvider>
        </LanguageProvider>
      </body>
    </html>
  );
}
