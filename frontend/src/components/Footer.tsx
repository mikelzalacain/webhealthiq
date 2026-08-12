"use client";

import Link from "next/link";
import Image from "next/image";
import { useI18n } from "@/lib/i18n/LanguageProvider";

export default function Footer() {
  const currentYear = new Date().getFullYear();
  const { t } = useI18n();

  return (
    <footer className="border-t border-border bg-surface mt-auto">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-14">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-10 mb-10">
          <div className="md:col-span-1">
            <Link href="/" className="flex items-center gap-2 mb-4">
              <div className="relative w-8 h-8 rounded-md bg-primary overflow-hidden">
                <Image
                  src="/icon-64.png"
                  alt="WebHealthIQ"
                  fill
                  sizes="32px"
                  className="object-contain p-1"
                />
              </div>
              <span className="font-display text-lg font-bold text-ink tracking-tight">
                WebHealthIQ
              </span>
            </Link>
            <p className="text-sm text-muted leading-relaxed">{t("footer.tagline")}</p>
            <p className="text-sm text-muted mt-3">
              <a href="mailto:hello@webhealthiq.com" className="hover:text-primary transition-colors">
                hello@webhealthiq.com
              </a>
            </p>
          </div>

          <div>
            <h3 className="text-xs font-semibold text-ink tracking-[0.14em] uppercase mb-4">
              {t("footer.product")}
            </h3>
            <ul className="space-y-2.5">
              <li><Link href="/#features" className="text-sm text-muted hover:text-primary transition-colors">{t("nav.modules")}</Link></li>
              <li><Link href="/#pricing" className="text-sm text-muted hover:text-primary transition-colors">{t("nav.pricing")}</Link></li>
              <li><Link href="/#pricing" className="text-sm text-muted hover:text-primary transition-colors">{t("footer.agencies")}</Link></li>
            </ul>
          </div>

          <div>
            <h3 className="text-xs font-semibold text-ink tracking-[0.14em] uppercase mb-4">
              {t("footer.resources")}
            </h3>
            <ul className="space-y-2.5">
              <li><Link href="/history" className="text-sm text-muted hover:text-primary transition-colors">{t("nav.history")}</Link></li>
              <li><Link href="/account" className="text-sm text-muted hover:text-primary transition-colors">{t("nav.account")}</Link></li>
              <li>
                <a href="mailto:hello@webhealthiq.com" className="text-sm text-muted hover:text-primary transition-colors">
                  {t("footer.help")}
                </a>
              </li>
            </ul>
          </div>

          <div>
            <h3 className="text-xs font-semibold text-ink tracking-[0.14em] uppercase mb-4">
              {t("footer.legal")}
            </h3>
            <ul className="space-y-2.5">
              <li><Link href="/privacy" className="text-sm text-muted hover:text-primary transition-colors">{t("footer.privacy")}</Link></li>
              <li><Link href="/terms" className="text-sm text-muted hover:text-primary transition-colors">{t("footer.terms")}</Link></li>
              <li><Link href="/cookies" className="text-sm text-muted hover:text-primary transition-colors">{t("footer.cookies")}</Link></li>
            </ul>
          </div>
        </div>

        <div className="pt-6 border-t border-border flex flex-col sm:flex-row justify-between gap-3 text-sm text-muted">
          <p>&copy; {currentYear} WebHealthIQ</p>
          <p className="font-mono text-xs tracking-wide uppercase">{t("footer.motto")}</p>
        </div>
      </div>
    </footer>
  );
}
