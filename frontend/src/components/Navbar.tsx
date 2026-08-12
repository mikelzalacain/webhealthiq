"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import Image from "next/image";
import LanguageSwitcher from "@/components/LanguageSwitcher";
import { useI18n } from "@/lib/i18n/LanguageProvider";
import { useAuth } from "@/lib/AuthProvider";

export default function Navbar() {
  const [scrolled, setScrolled] = useState(false);
  const { t } = useI18n();
  const { user, loading, logout } = useAuth();

  useEffect(() => {
    const handleScroll = () => setScrolled(window.scrollY > 16);
    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  return (
    <nav
      className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${
        scrolled
          ? "bg-surface/90 backdrop-blur-md border-b border-border py-3"
          : "bg-transparent py-5"
      }`}
    >
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between gap-4">
          <Link href="/" className="flex items-center gap-3 group shrink-0">
            <div className="relative w-9 h-9 overflow-hidden rounded-md bg-primary">
              <Image
                src="/logo.png"
                alt="WebHealthIQ"
                fill
                sizes="36px"
                className="object-contain p-1"
                priority
              />
            </div>
            <span className="font-display text-xl font-bold tracking-tight text-ink group-hover:text-primary transition-colors">
              WebHealthIQ
            </span>
          </Link>

          <div className="hidden md:flex items-center gap-7">
            <Link href="/#features" className="text-sm font-medium text-muted hover:text-ink transition-colors">
              {t("nav.modules")}
            </Link>
            <Link href="/#how-it-works" className="text-sm font-medium text-muted hover:text-ink transition-colors">
              {t("nav.method")}
            </Link>
            <Link href="/#pricing" className="text-sm font-medium text-muted hover:text-ink transition-colors">
              {t("nav.pricing")}
            </Link>
          </div>

          <div className="flex items-center gap-2 sm:gap-3">
            <LanguageSwitcher />
            {!loading && user ? (
              <>
                <span className="hidden sm:inline text-xs text-muted max-w-[140px] truncate" title={user.email}>
                  {user.audits_used}/{user.audits_limit} · {user.plan}
                </span>
                <button
                  type="button"
                  onClick={logout}
                  className="hidden sm:inline-flex text-sm font-semibold text-muted hover:text-ink transition-colors px-2 py-2"
                >
                  {t("nav.logout")}
                </button>
              </>
            ) : (
              <Link
                href="/login"
                className="hidden sm:inline-flex text-sm font-semibold text-muted hover:text-ink transition-colors px-2 py-2"
              >
                {t("nav.login")}
              </Link>
            )}
            <Link
              href="/#audit"
              className="inline-flex items-center justify-center px-3 sm:px-4 py-2.5 text-sm font-semibold text-white bg-accent rounded-md hover:bg-accent-light transition-colors"
            >
              {t("nav.cta")}
            </Link>
          </div>
        </div>
      </div>
    </nav>
  );
}
