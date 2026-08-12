import Link from "next/link";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Términos de uso — WebHealthIQ",
  description: "Condiciones de uso del servicio WebHealthIQ.",
  alternates: { canonical: "https://webhealthiq.com/terms" },
};

export default function TermsPage() {
  return (
    <div className="min-h-screen pt-28 pb-16 px-4">
      <article className="max-w-2xl mx-auto">
        <p className="text-sm mb-4">
          <Link href="/" className="text-primary hover:underline">
            ← Volver al inicio
          </Link>
        </p>
        <h1 className="font-display text-3xl font-bold text-ink mb-2">
          Términos de uso
        </h1>
        <p className="text-sm text-muted mb-8">
          Última actualización: agosto 2026 · WebHealthIQ ·{" "}
          <a href="https://webhealthiq.com" className="text-primary">
            webhealthiq.com
          </a>
        </p>

        <div className="space-y-6 text-ink text-[15px] leading-relaxed">
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
              acceso. Eres responsable de la actividad realizada con tu cuenta.
            </p>
          </section>

          <section>
            <h2 className="text-lg font-bold text-ink mb-2">3. Planes y pagos</h2>
            <p>
              El plan gratuito tiene límite mensual de auditorías. Los planes de pago
              (Pro / Agencia) se facturan vía Stripe según el precio publicado.
              Puedes cancelar desde el portal de cliente; el acceso de pago se mantiene
              hasta el final del periodo ya abonado salvo indicación contraria.
            </p>
          </section>

          <section>
            <h2 className="text-lg font-bold text-ink mb-2">4. Uso aceptable</h2>
            <p>
              No uses el servicio para fines ilícitos, abusivos o para atacar
              infraestructuras. Nos reservamos el derecho a suspender cuentas que
              vulneren estos términos o la seguridad del sistema.
            </p>
          </section>

          <section>
            <h2 className="text-lg font-bold text-ink mb-2">5. Informes</h2>
            <p>
              Puedes descargar informes PDF. En plan Agencia puedes configurar un nombre
              de marca en el PDF. El contenido del informe es para tu uso; no lo presentes
              como certificación oficial de terceros.
            </p>
          </section>

          <section>
            <h2 className="text-lg font-bold text-ink mb-2">6. Limitación</h2>
            <p>
              El servicio se ofrece “tal cual”. En la medida permitida por la ley, no
              respondemos por daños indirectos derivados del uso o imposibilidad de uso
              del servicio.
            </p>
          </section>

          <section>
            <h2 className="text-lg font-bold text-ink mb-2">7. Contacto</h2>
            <p>
              Dudas:{" "}
              <a href="mailto:hello@webhealthiq.com" className="text-primary">
                hello@webhealthiq.com
              </a>
              . También aplica nuestra{" "}
              <a href="/privacy" className="text-primary underline">
                política de privacidad
              </a>
              .
            </p>
          </section>
        </div>
      </article>
    </div>
  );
}
