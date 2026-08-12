"use client";

import Link from "next/link";
import { useI18n } from "@/lib/i18n/LanguageProvider";

export default function CookiesPage() {
  const { t } = useI18n();

  return (
    <div className="min-h-screen pt-28 pb-16 px-4">
      <article className="max-w-2xl mx-auto">
        <h1 className="font-display text-3xl font-bold text-ink mb-2">
          Política de cookies
        </h1>
        <p className="text-sm text-muted mb-8">
          {t("legal.updated")}: agosto 2026 · WebHealthIQ ·{" "}
          <a href="https://webhealthiq.com" className="text-primary">
            webhealthiq.com
          </a>
        </p>

        <div className="space-y-6 text-ink/90 text-[15px] leading-relaxed">
          <p>
            Esta página explica qué cookies y almacenamiento local usa WebHealthIQ y
            para qué.
          </p>

          <section>
            <h2 className="text-lg font-bold text-ink mb-2">1. Qué usamos</h2>
            <ul className="list-disc pl-5 space-y-1 text-muted">
              <li>
                <strong className="text-ink">Sesión (localStorage)</strong>: token de
                acceso y datos básicos de usuario para mantenerte conectado.
              </li>
              <li>
                <strong className="text-ink">Preferencia de idioma</strong>: idioma de
                la interfaz (ES / EN / EU).
              </li>
              <li>
                Cookies técnicas del hosting o CDN si el proveedor las requiere para
                seguridad y rendimiento.
              </li>
            </ul>
          </section>

          <section>
            <h2 className="text-lg font-bold text-ink mb-2">2. Finalidad</h2>
            <p>
              Autenticación, seguridad y recordar tu idioma. No usamos cookies de
              publicidad de terceros en el producto actual.
            </p>
          </section>

          <section>
            <h2 className="text-lg font-bold text-ink mb-2">3. Gestión</h2>
            <p>
              Puedes borrar el almacenamiento del sitio en tu navegador o cerrar
              sesión. Si bloqueas el almacenamiento local, la sesión y el idioma pueden
              no persistir.
            </p>
          </section>

          <section>
            <h2 className="text-lg font-bold text-ink mb-2">4. Más información</h2>
            <p>
              Ver{" "}
              <Link href="/privacy" className="text-primary">
                privacidad
              </Link>{" "}
              y{" "}
              <Link href="/terms" className="text-primary">
                términos
              </Link>
              . Contacto:{" "}
              <a href="mailto:hello@webhealthiq.com" className="text-primary">
                hello@webhealthiq.com
              </a>
              .
            </p>
          </section>
        </div>
      </article>
    </div>
  );
}
