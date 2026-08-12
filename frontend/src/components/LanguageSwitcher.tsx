"use client";

import { useI18n } from "@/lib/i18n/LanguageProvider";
import type { Lang } from "@/lib/i18n/translations";

export default function LanguageSwitcher() {
  const { lang, setLang, langs } = useI18n();

  return (
    <div
      className="inline-flex items-center gap-0.5 p-0.5 rounded-md border border-border bg-surface"
      role="group"
      aria-label="Language"
    >
      {langs.map((item) => {
        const active = item.code === lang;
        return (
          <button
            key={item.code}
            type="button"
            onClick={() => setLang(item.code as Lang)}
            className={`px-2 py-1 text-xs font-semibold rounded-sm transition-colors ${
              active
                ? "bg-primary text-white"
                : "text-muted hover:text-ink hover:bg-surface-hover"
            }`}
            aria-pressed={active}
          >
            {item.code.toUpperCase()}
          </button>
        );
      })}
    </div>
  );
}
