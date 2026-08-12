import Link from "next/link";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Política de cookies — WebHealthIQ",
  description: "Cookies y almacenamiento local usados por WebHealthIQ.",
  alternates: { canonical: "https://webhealthiq.com/cookies" },
};

export default function CookiesPage() {
  return (
    <div className="min-h-screen pt-28 pb-16 px-4">
      <article className="max-w-2xl mx-auto">
        <p className="text-sm mb-4">
          <Link href="/" className="text-primary hover:underline">
            ← Volver al inicio
          </Link>
        </p>
        <h1 className="font-display text-3xl font-bold text-ink mb-2">
          Política de cookies
        </h1>
        <p className="text-sm text-muted mb-8">
          Última actualización: agosto 2026 · WebHealthIQ ·{" "}
          <a href="https://webhealthiq.com" className="text-primary">
            webhealthiq.com
          </a>
        </p>

        <div className="space-y-6 text-ink text-[15px] leading-relaxed">
          <p>
            Esta página explica qué cookies y almacenamiento local usa WebHealthIQ y
            para qué.
          </p>

          <section>
            <h2 className="text-lg font-bold text-ink mb-2">1. Qué usamos</h2>
            <ul className="list-disc pl-5 space-y-2">
              <li>
                <strong>Sesión (localStorage)</strong>: token de acceso y datos básicos
                de usuario para mantenerte conectado.
              </li>
              <li>
                <strong>Preferencia de idioma</strong>: idioma de la interfaz (ES / EN /
                EU).
              </li>
              <li>
                Cookies técnicas del hosting o CDN si el proveedor las requiere para
                seguridad o rendimiento.
              </li>
            </ul>
          </section>

          <section>
            <h2 className="text-lg font-bold text-ink mb-2">2. Finalidad</h2>
            <p>
              Solo usamos almacenamiento necesario para autenticación, preferencias y
              operación del servicio. No usamos cookies publicitarias de terceros en la
              web de producto.
            </p>
          </section>

          <section>
            <h2 className="text-lg font-bold text-ink mb-2">3. Cómo gestionarlas</h2>
            <p>
              Puedes borrar el almacenamiento del sitio desde tu navegador o cerrar
              sesión. Si bloqueas el almacenamiento local, es posible que no puedas
              iniciar sesión.
            </p>
          </section>

          <section>
            <h2 className="text-lg font-bold text-ink mb-2">4. Más información</h2>
            <p>
              Consulta la{" "}
              <a href="/privacy" className="text-primary underline">
                política de privacidad
              </a>{" "}
              o escribe a{" "}
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
