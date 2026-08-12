import Link from "next/link";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Política de privacidad — WebHealthIQ",
  description:
    "Cómo WebHealthIQ trata los datos personales de cuentas, auditorías y contacto.",
  alternates: { canonical: "https://webhealthiq.com/privacy" },
};

export default function PrivacyPage() {
  return (
    <div className="min-h-screen pt-28 pb-16 px-4">
      <article className="max-w-2xl mx-auto">
        <p className="text-sm mb-4">
          <Link href="/" className="text-primary hover:underline">
            ← Volver al inicio
          </Link>
        </p>
        <h1 className="font-display text-3xl font-bold text-ink mb-2">
          Política de privacidad
        </h1>
        <p className="text-sm text-muted mb-8">
          Última actualización: agosto 2026 · WebHealthIQ ·{" "}
          <a href="https://webhealthiq.com" className="text-primary">
            webhealthiq.com
          </a>
        </p>

        <div className="space-y-6 text-ink text-[15px] leading-relaxed">
          <p>
            Esta política describe cómo WebHealthIQ trata los datos personales cuando
            usas nuestro servicio de auditorías web (SEO, rendimiento, accesibilidad,
            seguridad y RGPD).
          </p>

          <section>
            <h2 className="text-lg font-bold text-ink mb-2">1. Responsable</h2>
            <p>
              WebHealthIQ. Contacto:{" "}
              <a href="mailto:hello@webhealthiq.com" className="text-primary">
                hello@webhealthiq.com
              </a>
              . Sitio:{" "}
              <a href="https://webhealthiq.com" className="text-primary">
                https://webhealthiq.com
              </a>
              .
            </p>
          </section>

          <section>
            <h2 className="text-lg font-bold text-ink mb-2">2. Datos que tratamos</h2>
            <ul className="list-disc pl-5 space-y-1">
              <li>Cuenta: email, nombre, empresa (opcional), contraseña cifrada.</li>
              <li>Uso: URLs auditadas, puntuaciones, informes e insights asociados.</li>
              <li>Técnicos: logs de acceso y seguridad necesarios para operar el servicio.</li>
              <li>Pagos: datos de facturación gestionados por Stripe (no almacenamos el número completo de tarjeta).</li>
            </ul>
          </section>

          <section>
            <h2 className="text-lg font-bold text-ink mb-2">3. Finalidad y base legal</h2>
            <p>
              Prestamos el servicio de auditoría y gestión de cuenta (ejecución del
              contrato). Enviamos emails de seguridad (p. ej. restablecer contraseña)
              por interés legítimo / obligación contractual. No vendemos tus datos.
            </p>
          </section>

          <section>
            <h2 className="text-lg font-bold text-ink mb-2">4. Conservación</h2>
            <p>
              Conservamos la cuenta mientras esté activa y el historial de auditorías
              según los límites de tu plan. Puedes solicitar baja o borrado en{" "}
              <a href="mailto:hello@webhealthiq.com" className="text-primary">
                hello@webhealthiq.com
              </a>
              .
            </p>
          </section>

          <section>
            <h2 className="text-lg font-bold text-ink mb-2">5. Encargados y transferencias</h2>
            <p>
              Usamos proveedores de hosting (p. ej. Vercel, Render), base de datos
              (Postgres/Neon), email (SMTP) y pagos (Stripe) bajo acuerdos de
              tratamiento. Si hay transferencias fuera del EEE, se aplicarán
              salvaguardas adecuadas.
            </p>
          </section>

          <section>
            <h2 className="text-lg font-bold text-ink mb-2">6. Tus derechos</h2>
            <p>
              Acceso, rectificación, supresión, oposición, limitación y portabilidad.
              Escríbenos a{" "}
              <a href="mailto:hello@webhealthiq.com" className="text-primary">
                hello@webhealthiq.com
              </a>
              . También puedes reclamar ante la autoridad de protección de datos
              competente.
            </p>
          </section>

          <section>
            <h2 className="text-lg font-bold text-ink mb-2">7. Cookies</h2>
            <p>
              Detalle en nuestra{" "}
              <a href="/cookies" className="text-primary underline">
                política de cookies
              </a>
              .
            </p>
          </section>
        </div>
      </article>
    </div>
  );
}
