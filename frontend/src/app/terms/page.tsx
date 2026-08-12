"use client";

import Link from "next/link";
import { useI18n } from "@/lib/i18n/LanguageProvider";

export default function TermsPage() {
  const { t } = useI18n();

  return (
    <div className="min-h-screen pt-28 pb-16 px-4">
      <article className="max-w-2xl mx-auto">
        <h1 className="font-display text-3xl font-bold text-ink mb-2">
          Términos de uso
        </h1>
        <p className="text-sm text-muted mb-8">
          {t("legal.updated")}: agosto 2026 · WebHealthIQ ·{" "}
          <a href="https://webhealthiq.com" className="text-primary">
            webhealthiq.com
          </a>
        </p>

        <div className="space-y-6 text-ink/90 text-[15px] leading-relaxed">
          <p>
            Al crear una cuenta o usar WebHealthIQ aceptas estos términos. Si no estás
            de acuerdo, no uses el servicio.
          </p>

          <section>
            <h2 className="text-lg font-bold text-ink mb-2">1. Servicio</h2>
            <p>
              WebHealthIQ ofrece auditorías automatizadas de sitios web (SEO,
              rendimiento, accesibilidad, seguridad y RGPD). Los resultados son
              orientativos y no sustituyen asesoramiento legal o de cumplimiento.
            </p>
          </section>

          <section>
            <h2 className="text-lg font-bold text-ink mb-2">2. Cuenta</h2>
            <p>
              Debes proporcionar datos veraces y mantener la confidencialidad de tu
              contraseña. Eres responsable del uso de tu cuenta. Planes free / pro /
              agency tienen límites de auditorías mensuales y de historial.
            </p>
          </section>

          <section>
            <h2 className="text-lg font-bold text-ink mb-2">3. Uso aceptable</h2>
            <ul className="list-disc pl-5 space-y-1 text-muted">
              <li>Solo audita URLs que tengas derecho a analizar.</li>
              <li>No abuses del servicio ni intentes vulnerarlo.</li>
              <li>No uses WebHealthIQ para actividades ilegales.</li>
            </ul>
          </section>

          <section>
            <h2 className="text-lg font-bold text-ink mb-2">4. Informes y marca blanca</h2>
            <p>
              Puedes descargar informes PDF. En plan Agencia puedes configurar un nombre
              de marca para tus informes. WebHealthIQ puede seguir apareciendo como
              tecnología generadora salvo acuerdo distinto.
            </p>
          </section>

          <section>
            <h2 className="text-lg font-bold text-ink mb-2">5. Disponibilidad</h2>
            <p>
              Intentamos mantener el servicio operativo, pero no garantizamos
              disponibilidad ininterrumpida ni exactitud total de mediciones externas
              (red, CDN, bloqueos del sitio auditado, etc.).
            </p>
          </section>

          <section>
            <h2 className="text-lg font-bold text-ink mb-2">6. Limitación de responsabilidad</h2>
            <p>
              En la medida permitida por la ley, WebHealthIQ no responde por daños
              indirectos, pérdida de beneficios o decisiones tomadas únicamente a partir
              de un informe automático.
            </p>
          </section>

          <section>
            <h2 className="text-lg font-bold text-ink mb-2">7. Privacidad</h2>
            <p>
              El tratamiento de datos se rige por la{" "}
              <Link href="/privacy" className="text-primary">
                política de privacidad
              </Link>
              .
            </p>
          </section>

          <section>
            <h2 className="text-lg font-bold text-ink mb-2">8. Contacto</h2>
            <p>
              {t("legal.contact")}:{" "}
              <a href="mailto:hello@webhealthiq.com" className="text-primary">
                hello@webhealthiq.com
              </a>
            </p>
          </section>
        </div>
      </article>
    </div>
  );
}
