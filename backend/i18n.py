"""Traducciones de mensajes de auditoría (es / en / eu)."""
from __future__ import annotations

from typing import Any

SUPPORTED = ("es", "en", "eu")
DEFAULT_LANG = "es"

MESSAGES: dict[str, dict[str, str]] = {
    # --- API errors ---
    "err.url_access": {
        "es": "No se pudo acceder a la URL: {error}",
        "en": "Could not access the URL: {error}",
        "eu": "Ezin izan da URLa atzitu: {error}",
    },
    "err.internal": {
        "es": "Error interno del servidor: {error}",
        "en": "Internal server error: {error}",
        "eu": "Zerbitzariaren barne-errorea: {error}",
    },
    "err.quota": {
        "es": "Has alcanzado el límite de tu plan {plan}: {used}/{limit} auditorías este mes. Sube a Pro para continuar.",
        "en": "You reached your {plan} plan limit: {used}/{limit} audits this month. Upgrade to Pro to continue.",
        "eu": "Zure {plan} planaren muga iritsi duzu: {used}/{limit} auditoretza hilabete honetan. Igo Pro-ra jarraitzeko.",
    },
    # --- Shared ---
    "common.ok": {"es": "Correcto.", "en": "Correct.", "eu": "Zuzena."},
    "common.perfect": {"es": "Perfecto.", "en": "Perfect.", "eu": "Bikain."},
    "common.na": {"es": "N/A", "en": "N/A", "eu": "E/E"},
    "common.unknown": {"es": "Desconocido", "en": "Unknown", "eu": "Ezezaguna"},
    "common.good_length": {
        "es": "Mantiene buena longitud.",
        "en": "Good length.",
        "eu": "Luzera egokia.",
    },
    # --- SEO ---
    "seo.title.name": {"es": "Etiqueta Title", "en": "Title tag", "eu": "Title etiketa"},
    "seo.title.missing": {
        "es": "No se encontró etiqueta title",
        "en": "Title tag not found",
        "eu": "Ez da title etiketarik aurkitu",
    },
    "seo.title.missing_rec": {
        "es": "Añade una etiqueta <title> descriptiva en el <head>.",
        "en": "Add a descriptive <title> tag in the <head>.",
        "eu": "Gehitu <title> deskriptibo bat <head> atalean.",
    },
    "seo.title.ok": {
        "es": "Title correcto ({n} chars)",
        "en": "Title looks good ({n} chars)",
        "eu": "Title zuzena ({n} karaktere)",
    },
    "seo.title.warn": {
        "es": "Title subóptimo ({n} chars)",
        "en": "Suboptimal title ({n} chars)",
        "eu": "Title hobegarria ({n} karaktere)",
    },
    "seo.title.warn_rec": {
        "es": "Mantén el título entre 50 y 60 caracteres.",
        "en": "Keep the title between 50 and 60 characters.",
        "eu": "Mantendu titulua 50 eta 60 karaktere artean.",
    },
    "seo.meta.name": {"es": "Meta Description", "en": "Meta description", "eu": "Meta deskribapena"},
    "seo.meta.missing": {
        "es": "No se encontró meta description",
        "en": "Meta description not found",
        "eu": "Ez da meta deskribapenik aurkitu",
    },
    "seo.meta.missing_rec": {
        "es": "Añade una etiqueta <meta name='description' content='...'>.",
        "en": "Add a <meta name='description' content='...'> tag.",
        "eu": "Gehitu <meta name='description' content='...'> etiketa.",
    },
    "seo.meta.ok": {
        "es": "Description correcta ({n} chars)",
        "en": "Description looks good ({n} chars)",
        "eu": "Deskribapen zuzena ({n} karaktere)",
    },
    "seo.meta.warn": {
        "es": "Description subóptima ({n} chars)",
        "en": "Suboptimal description ({n} chars)",
        "eu": "Deskribapen hobegarria ({n} karaktere)",
    },
    "seo.meta.warn_rec": {
        "es": "Mantén la descripción entre 120 y 160 caracteres.",
        "en": "Keep the description between 120 and 160 characters.",
        "eu": "Mantendu deskribapena 120 eta 160 karaktere artean.",
    },
    "seo.h1.name": {"es": "Etiquetas H1", "en": "H1 headings", "eu": "H1 etiketak"},
    "seo.h1.missing": {
        "es": "No se encontró etiqueta H1",
        "en": "No H1 tag found",
        "eu": "Ez da H1 etiketarik aurkitu",
    },
    "seo.h1.missing_rec": {
        "es": "Añade exactamente un <h1> que describa el contenido principal.",
        "en": "Add exactly one <h1> describing the main content.",
        "eu": "Gehitu edukia deskribatzen duen <h1> bakarra.",
    },
    "seo.h1.ok": {
        "es": "Se encontró exactamente un H1",
        "en": "Exactly one H1 found",
        "eu": "H1 bakarra aurkitu da",
    },
    "seo.h1.multi": {
        "es": "Se encontraron {n} etiquetas H1",
        "en": "Found {n} H1 tags",
        "eu": "{n} H1 etiketa aurkitu dira",
    },
    "seo.h1.multi_rec": {
        "es": "Se recomienda usar solo un H1 por página para SEO, aunque HTML5 permita más.",
        "en": "Prefer a single H1 per page for SEO, even if HTML5 allows more.",
        "eu": "SEOrako H1 bakarra erabiltzea gomendatzen da, HTML5ek gehiago onartu arren.",
    },
    "seo.alt.name": {
        "es": "Atributos Alt en Imágenes",
        "en": "Image alt attributes",
        "eu": "Irudien alt atributuak",
    },
    "seo.alt.none": {
        "es": "No hay imágenes",
        "en": "No images found",
        "eu": "Ez dago irudirik",
    },
    "seo.alt.ok": {
        "es": "Todas las imágenes tienen atributo alt",
        "en": "All images have an alt attribute",
        "eu": "Irudi guztiek dute alt atributua",
    },
    "seo.alt.ok_rec": {
        "es": "Buen trabajo.",
        "en": "Good job.",
        "eu": "Lan ona.",
    },
    "seo.alt.missing": {
        "es": "{missing} de {total} imágenes carecen de alt",
        "en": "{missing} of {total} images are missing alt",
        "eu": "{total} iruditatik {missing}ek ez dute altik",
    },
    "seo.alt.missing_rec": {
        "es": "Añade atributos alt descriptivos a todas las imágenes relevantes.",
        "en": "Add descriptive alt attributes to all meaningful images.",
        "eu": "Gehitu alt atributu deskriptiboak irudi garrantzitsuei.",
    },
    "seo.canonical.name": {"es": "Canonical URL", "en": "Canonical URL", "eu": "URL kanonikoa"},
    "seo.canonical.ok": {
        "es": "URL canonical presente",
        "en": "Canonical URL present",
        "eu": "URL kanonikoa presente dago",
    },
    "seo.canonical.missing": {
        "es": "Falta etiqueta canonical",
        "en": "Canonical tag missing",
        "eu": "Canonical etiketa falta da",
    },
    "seo.canonical.missing_rec": {
        "es": "Añade <link rel='canonical'> para evitar contenido duplicado.",
        "en": "Add <link rel='canonical'> to avoid duplicate content.",
        "eu": "Gehitu <link rel='canonical'> edukia bikoiztea saihesteko.",
    },
    "seo.og.name": {"es": "Open Graph", "en": "Open Graph", "eu": "Open Graph"},
    "seo.og.ok": {
        "es": "Etiquetas Open Graph principales presentes",
        "en": "Main Open Graph tags present",
        "eu": "Open Graph etiketa nagusiak presente daude",
    },
    "seo.og.partial": {
        "es": "Faltan algunas etiquetas OG ({tags})",
        "en": "Some OG tags are missing ({tags})",
        "eu": "OG etiketa batzuk falta dira ({tags})",
    },
    "seo.og.partial_rec": {
        "es": "Completa las etiquetas Open Graph para mejorar cómo se comparte tu enlace en redes sociales.",
        "en": "Complete Open Graph tags to improve social sharing.",
        "eu": "Osatu Open Graph etiketak sare sozialetan hobeto partekatzeko.",
    },
    "seo.og.missing": {
        "es": "No se encontraron etiquetas Open Graph",
        "en": "No Open Graph tags found",
        "eu": "Ez da Open Graph etiketarik aurkitu",
    },
    "seo.og.missing_rec": {
        "es": "Implementa etiquetas OG (title, description, image) para redes sociales.",
        "en": "Implement OG tags (title, description, image) for social networks.",
        "eu": "Inplementatu OG etiketak (title, description, image) sare sozialetarako.",
    },
    "seo.schema.name": {"es": "Schema.org", "en": "Schema.org", "eu": "Schema.org"},
    "seo.schema.ok": {
        "es": "Marcado Schema detectado ({type})",
        "en": "Schema markup detected ({type})",
        "eu": "Schema markaketa detektatu da ({type})",
    },
    "seo.schema.invalid": {
        "es": "Script LD+JSON encontrado pero es inválido",
        "en": "LD+JSON script found but invalid",
        "eu": "LD+JSON scripta aurkitu da baina baliogabea da",
    },
    "seo.schema.invalid_rec": {
        "es": "Verifica la sintaxis JSON del schema.",
        "en": "Validate the JSON syntax of the schema.",
        "eu": "Egiaztatu schemaren JSON sintaxia.",
    },
    "seo.schema.missing": {
        "es": "No se encontró marcado Schema.org",
        "en": "No Schema.org markup found",
        "eu": "Ez da Schema.org markaketarik aurkitu",
    },
    "seo.schema.missing_rec": {
        "es": "Añade datos estructurados JSON-LD para mejorar la visibilidad en buscadores.",
        "en": "Add JSON-LD structured data to improve search visibility.",
        "eu": "Gehitu JSON-LD datu egituratuak bilatzaileetan ikusgarritasuna hobetzeko.",
    },
    "seo.robots.name": {"es": "Robots.txt", "en": "Robots.txt", "eu": "Robots.txt"},
    "seo.robots.ok": {
        "es": "Archivo robots.txt accesible",
        "en": "robots.txt file is accessible",
        "eu": "robots.txt fitxategia atzigarria da",
    },
    "seo.robots.status": {
        "es": "Archivo robots.txt devolvió {code}",
        "en": "robots.txt returned {code}",
        "eu": "robots.txt-ek {code} itzuli du",
    },
    "seo.robots.status_rec": {
        "es": "Asegúrate de tener un robots.txt en la raíz del sitio.",
        "en": "Make sure you have a robots.txt at the site root.",
        "eu": "Ziurtatu robots.txt bat duzula gunearen erroan.",
    },
    "seo.robots.error": {
        "es": "No se pudo comprobar robots.txt",
        "en": "Could not check robots.txt",
        "eu": "Ezin izan da robots.txt egiaztatu",
    },
    "seo.robots.error_rec": {
        "es": "Comprueba que la ruta /robots.txt es accesible.",
        "en": "Check that /robots.txt is reachable.",
        "eu": "Egiaztatu /robots.txt atzigarria dela.",
    },
    "seo.sitemap.name": {"es": "Sitemap XML", "en": "XML Sitemap", "eu": "XML Sitemap"},
    "seo.sitemap.ok": {
        "es": "Sitemap.xml accesible",
        "en": "sitemap.xml is accessible",
        "eu": "sitemap.xml atzigarria da",
    },
    "seo.sitemap.missing": {
        "es": "Sitemap.xml no encontrado en ruta estándar",
        "en": "sitemap.xml not found at the standard path",
        "eu": "sitemap.xml ez da bide estandarrean aurkitu",
    },
    "seo.sitemap.missing_rec": {
        "es": "Asegúrate de tener un sitemap.xml referenciado en robots.txt o en la raíz.",
        "en": "Provide a sitemap.xml referenced in robots.txt or at the root.",
        "eu": "Ziurtatu sitemap.xml bat duzula robots.txt-en edo erroan.",
    },
    "seo.sitemap.error": {
        "es": "No se pudo comprobar sitemap.xml",
        "en": "Could not check sitemap.xml",
        "eu": "Ezin izan da sitemap.xml egiaztatu",
    },
    "seo.sitemap.error_rec": {
        "es": "Comprueba que la ruta /sitemap.xml es accesible.",
        "en": "Check that /sitemap.xml is reachable.",
        "eu": "Egiaztatu /sitemap.xml atzigarria dela.",
    },
    # --- Security ---
    "sec.https.name": {"es": "HTTPS activo", "en": "HTTPS enabled", "eu": "HTTPS aktibo"},
    "sec.https.ok": {
        "es": "El sitio carga bajo una conexión segura (HTTPS).",
        "en": "The site loads over a secure connection (HTTPS).",
        "eu": "Gunea konexio seguruan kargatzen da (HTTPS).",
    },
    "sec.https.fail": {
        "es": "El sitio no utiliza conexión segura (HTTP).",
        "en": "The site is not using a secure connection (HTTP).",
        "eu": "Guneak ez du konexio segururik erabiltzen (HTTP).",
    },
    "sec.https.fail_rec": {
        "es": "Habilita HTTPS y redirecciona todo el tráfico HTTP a HTTPS.",
        "en": "Enable HTTPS and redirect all HTTP traffic to HTTPS.",
        "eu": "Gaitu HTTPS eta birbideratu HTTP trafiko guztia HTTPSra.",
    },
    "sec.https.error": {
        "es": "No se pudo acceder: {error}",
        "en": "Could not access: {error}",
        "eu": "Ezin izan da atzitu: {error}",
    },
    "sec.https.error_rec": {
        "es": "Verifica que el servidor esté activo y acepte conexiones HTTPS.",
        "en": "Verify the server is up and accepts HTTPS connections.",
        "eu": "Egiaztatu zerbitzaria aktibo dagoela eta HTTPS onartzen duela.",
    },
    "sec.hsts.name": {"es": "HSTS", "en": "HSTS", "eu": "HSTS"},
    "sec.hsts.ok": {
        "es": "Cabecera HSTS configurada correctamente.",
        "en": "HSTS header is configured correctly.",
        "eu": "HSTS goiburua ondo konfiguratuta dago.",
    },
    "sec.hsts.missing": {
        "es": "Falta la cabecera Strict-Transport-Security.",
        "en": "Strict-Transport-Security header is missing.",
        "eu": "Strict-Transport-Security goiburua falta da.",
    },
    "sec.hsts.missing_rec": {
        "es": "Añade HSTS para forzar conexiones seguras en el navegador.",
        "en": "Add HSTS to force secure browser connections.",
        "eu": "Gehitu HSTS nabigatzailean konexio seguruak behartzeko.",
    },
    "sec.csp.name": {"es": "CSP", "en": "CSP", "eu": "CSP"},
    "sec.csp.ok": {
        "es": "Cabecera Content-Security-Policy presente.",
        "en": "Content-Security-Policy header is present.",
        "eu": "Content-Security-Policy goiburua presente dago.",
    },
    "sec.csp.missing": {
        "es": "Falta cabecera CSP.",
        "en": "CSP header is missing.",
        "eu": "CSP goiburua falta da.",
    },
    "sec.csp.missing_rec": {
        "es": "Implementa CSP para prevenir ataques XSS limitando las fuentes de recursos.",
        "en": "Implement CSP to help prevent XSS by limiting resource sources.",
        "eu": "Inplementatu CSP XSS erasoak saihesteko, baliabide-iturriak mugatuz.",
    },
    "sec.click.name": {
        "es": "Protección Clickjacking",
        "en": "Clickjacking protection",
        "eu": "Clickjacking babesa",
    },
    "sec.click.ok": {
        "es": "Protección contra Clickjacking configurada (X-Frame-Options o CSP).",
        "en": "Clickjacking protection configured (X-Frame-Options or CSP).",
        "eu": "Clickjacking babesa konfiguratuta (X-Frame-Options edo CSP).",
    },
    "sec.click.missing": {
        "es": "Falta protección contra Clickjacking.",
        "en": "Clickjacking protection is missing.",
        "eu": "Clickjacking babesa falta da.",
    },
    "sec.click.missing_rec": {
        "es": "Añade la cabecera X-Frame-Options: SAMEORIGIN o CSP equivalente.",
        "en": "Add X-Frame-Options: SAMEORIGIN or an equivalent CSP directive.",
        "eu": "Gehitu X-Frame-Options: SAMEORIGIN edo CSP baliokidea.",
    },
    "sec.mime.name": {
        "es": "Protección MIME Sniffing",
        "en": "MIME sniffing protection",
        "eu": "MIME sniffing babesa",
    },
    "sec.mime.ok": {
        "es": "Cabecera X-Content-Type-Options configurada.",
        "en": "X-Content-Type-Options header is configured.",
        "eu": "X-Content-Type-Options goiburua konfiguratuta dago.",
    },
    "sec.mime.missing": {
        "es": "Falta X-Content-Type-Options: nosniff.",
        "en": "Missing X-Content-Type-Options: nosniff.",
        "eu": "X-Content-Type-Options: nosniff falta da.",
    },
    "sec.mime.missing_rec": {
        "es": "Añade esta cabecera para prevenir ataques de confusión de tipos MIME.",
        "en": "Add this header to prevent MIME type confusion attacks.",
        "eu": "Gehitu goiburu hau MIME moten nahasmen-erasoak saihesteko.",
    },
    "sec.ssl.name": {"es": "Certificado SSL", "en": "SSL certificate", "eu": "SSL ziurtagiria"},
    "sec.ssl.ok": {
        "es": "Certificado válido (Expira en {days} días).",
        "en": "Valid certificate (expires in {days} days).",
        "eu": "Ziurtagiri balioduna ({days} egunetan iraungitzen da).",
    },
    "sec.ssl.fail": {
        "es": "Problema con certificado SSL: {error}.",
        "en": "SSL certificate issue: {error}.",
        "eu": "SSL ziurtagiriaren arazoa: {error}.",
    },
    "sec.ssl.fail_rec": {
        "es": "Revisa y renueva el certificado SSL.",
        "en": "Review and renew the SSL certificate.",
        "eu": "Berrikusi eta berritu SSL ziurtagiria.",
    },
    "sec.ssl.expired": {
        "es": "Certificado expirado",
        "en": "Certificate expired",
        "eu": "Ziurtagiria iraungita",
    },
    "sec.ssl.unknown": {
        "es": "No se pudo obtener información del certificado",
        "en": "Could not read certificate information",
        "eu": "Ezin izan da ziurtagiriaren informazioa lortu",
    },
    "sec.ssl.soon": {
        "es": "Certificado válido pero caduca pronto ({days} días).",
        "en": "Certificate valid but expires soon ({days} days).",
        "eu": "Ziurtagiria balioduna da baina laster iraungitzen da ({days} egun).",
    },
    "sec.ssl.soon_rec": {
        "es": "Renueva el certificado antes de que expire.",
        "en": "Renew the certificate before it expires.",
        "eu": "Berritu ziurtagiria iraungi aurretik.",
    },
    "sec.hsts.weak": {
        "es": "HSTS presente pero max-age bajo ({max_age}s).",
        "en": "HSTS present but max-age is low ({max_age}s).",
        "eu": "HSTS presente da baina max-age baxua da ({max_age}s).",
    },
    "sec.hsts.weak_rec": {
        "es": "Usa max-age de al menos 15552000 (6 meses), idealmente 31536000.",
        "en": "Use max-age of at least 15552000 (6 months), ideally 31536000.",
        "eu": "Erabili gutxienez 15552000eko max-age (6 hilabete), idealena 31536000.",
    },
    "sec.csp.weak": {
        "es": "CSP presente pero permite {flags}.",
        "en": "CSP present but allows {flags}.",
        "eu": "CSP presente da baina {flags} baimentzen du.",
    },
    "sec.csp.weak_rec": {
        "es": "Evita 'unsafe-inline' y 'unsafe-eval'; usa nonces o hashes.",
        "en": "Avoid 'unsafe-inline' and 'unsafe-eval'; use nonces or hashes.",
        "eu": "Saihestu 'unsafe-inline' eta 'unsafe-eval'; erabili nonce edo hash-ak.",
    },
    "sec.referrer.name": {
        "es": "Referrer-Policy",
        "en": "Referrer-Policy",
        "eu": "Referrer-Policy",
    },
    "sec.referrer.ok": {
        "es": "Referrer-Policy configurada ({value}).",
        "en": "Referrer-Policy set ({value}).",
        "eu": "Referrer-Policy konfiguratuta ({value}).",
    },
    "sec.referrer.missing": {
        "es": "No se encontró cabecera Referrer-Policy.",
        "en": "Referrer-Policy header not found.",
        "eu": "Ez da Referrer-Policy goibururik aurkitu.",
    },
    "sec.referrer.missing_rec": {
        "es": "Añade Referrer-Policy (p. ej. strict-origin-when-cross-origin).",
        "en": "Add Referrer-Policy (e.g. strict-origin-when-cross-origin).",
        "eu": "Gehitu Referrer-Policy (adib. strict-origin-when-cross-origin).",
    },
    "sec.permissions.name": {
        "es": "Permissions-Policy",
        "en": "Permissions-Policy",
        "eu": "Permissions-Policy",
    },
    "sec.permissions.ok": {
        "es": "Permissions-Policy (o Feature-Policy) presente.",
        "en": "Permissions-Policy (or Feature-Policy) present.",
        "eu": "Permissions-Policy (edo Feature-Policy) presente da.",
    },
    "sec.permissions.missing": {
        "es": "No se encontró Permissions-Policy.",
        "en": "Permissions-Policy not found.",
        "eu": "Ez da Permissions-Policy aurkitu.",
    },
    "sec.permissions.missing_rec": {
        "es": "Limita cámara, micrófono, geolocalización, etc. con Permissions-Policy.",
        "en": "Limit camera, mic, geolocation, etc. with Permissions-Policy.",
        "eu": "Mugatu kamera, mikrofonoa, geolokalizazioa, etab. Permissions-Policy-rekin.",
    },
    "sec.cookies.name": {
        "es": "Cookies (Secure / HttpOnly / SameSite)",
        "en": "Cookies (Secure / HttpOnly / SameSite)",
        "eu": "Cookieak (Secure / HttpOnly / SameSite)",
    },
    "sec.cookies.none": {
        "es": "No se detectaron cookies en la respuesta inicial.",
        "en": "No cookies detected on the initial response.",
        "eu": "Hasierako erantzunean ez da cookierik detektatu.",
    },
    "sec.cookies.ok": {
        "es": "{count} cookie(s) con flags de seguridad adecuados.",
        "en": "{count} cookie(s) with proper security flags.",
        "eu": "{count} cookie segurtasun-flag egokiekin.",
    },
    "sec.cookies.weak": {
        "es": "{count} cookie(s): sin Secure={secure}, sin HttpOnly={httponly}, sin SameSite={samesite}.",
        "en": "{count} cookie(s): missing Secure={secure}, HttpOnly={httponly}, SameSite={samesite}.",
        "eu": "{count} cookie: Secure gabe={secure}, HttpOnly gabe={httponly}, SameSite gabe={samesite}.",
    },
    "sec.cookies.weak_rec": {
        "es": "Marca cookies sensibles con Secure, HttpOnly y SameSite=Lax o Strict.",
        "en": "Mark sensitive cookies with Secure, HttpOnly and SameSite=Lax or Strict.",
        "eu": "Markatu cookie sentikorrak Secure, HttpOnly eta SameSite=Lax edo Strict-ekin.",
    },
    "sec.cors.name": {"es": "CORS", "en": "CORS", "eu": "CORS"},
    "sec.cors.none": {
        "es": "Sin Access-Control-Allow-Origin en la respuesta (habitual en sitios web).",
        "en": "No Access-Control-Allow-Origin on the response (common for websites).",
        "eu": "Erantzunean ez dago Access-Control-Allow-Origin (ohikoa webguneetan).",
    },
    "sec.cors.ok": {
        "es": "CORS restringido ({value}).",
        "en": "CORS restricted ({value}).",
        "eu": "CORS mugatua ({value}).",
    },
    "sec.cors.star": {
        "es": "CORS permite cualquier origen (*).",
        "en": "CORS allows any origin (*).",
        "eu": "CORS-ek edozein jatorri (*) baimentzen du.",
    },
    "sec.cors.star_rec": {
        "es": "Limita Access-Control-Allow-Origin a dominios de confianza.",
        "en": "Limit Access-Control-Allow-Origin to trusted domains.",
        "eu": "Mugatu Access-Control-Allow-Origin konfiantzazko domeinuetara.",
    },
    "sec.cors.star_creds": {
        "es": "CORS peligroso: * junto con Access-Control-Allow-Credentials.",
        "en": "Dangerous CORS: * together with Access-Control-Allow-Credentials.",
        "eu": "CORS arriskutsua: * Access-Control-Allow-Credentials-ekin.",
    },
    "sec.cors.star_creds_rec": {
        "es": "Nunca combines ACAO:* con credenciales; usa orígenes explícitos.",
        "en": "Never combine ACAO:* with credentials; use explicit origins.",
        "eu": "Inoiz ez konbinatu ACAO:* kredentzialekin; erabili jatorri esplizituak.",
    },
    "sec.server.name": {
        "es": "Cabecera Server",
        "en": "Server header",
        "eu": "Server goiburua",
    },
    "sec.server.hidden": {
        "es": "No se expone cabecera Server.",
        "en": "Server header not exposed.",
        "eu": "Server goiburua ez da agerian.",
    },
    "sec.server.ok": {
        "es": "Server presente sin versión evidente ({value}).",
        "en": "Server present without an obvious version ({value}).",
        "eu": "Server presente da bertsio argirik gabe ({value}).",
    },
    "sec.server.version": {
        "es": "Server revela software/versión ({value}).",
        "en": "Server reveals software/version ({value}).",
        "eu": "Server-ek softwarea/bertsioa agerian uzten du ({value}).",
    },
    "sec.server.version_rec": {
        "es": "Oculta o generaliza la cabecera Server para no filtrar versión.",
        "en": "Hide or generalize the Server header to avoid leaking version info.",
        "eu": "Ezkutatu edo orokortu Server goiburua bertsioa ez filtratzeko.",
    },
    # --- GDPR ---
    "gdpr.track.name": {
        "es": "Scripts de rastreo",
        "en": "Tracking scripts",
        "eu": "Jarraipen-scriptak",
    },
    "gdpr.track.found": {
        "es": "Se detectaron scripts de terceros ({list}).",
        "en": "Third-party scripts detected ({list}).",
        "eu": "Hirugarrenen scriptak detektatu dira ({list}).",
    },
    "gdpr.track.found_rec": {
        "es": "Asegúrate de bloquear estos scripts hasta que el usuario dé su consentimiento explícito.",
        "en": "Block these scripts until the user gives explicit consent.",
        "eu": "Blokeatu script hauek erabiltzaileak onespen esplizitua eman arte.",
    },
    "gdpr.track.ok": {
        "es": "No se detectaron scripts intrusivos evidentes en la carga inicial.",
        "en": "No obvious intrusive scripts detected on initial load.",
        "eu": "Hasierako kargan ez da script intrusiborik detektatu.",
    },
    "gdpr.track.ok_rec": {
        "es": "Mantén un control estricto sobre los scripts de terceros.",
        "en": "Keep strict control over third-party scripts.",
        "eu": "Kontrol zorrotza mantendu hirugarrenen scriptetan.",
    },
    "gdpr.consent.name": {
        "es": "Google Consent Mode v2",
        "en": "Google Consent Mode v2",
        "eu": "Google Consent Mode v2",
    },
    "gdpr.consent.ok": {
        "es": "Se encontró configuración de Consent Mode (gtag('consent', ...)).",
        "en": "Consent Mode configuration found (gtag('consent', ...)).",
        "eu": "Consent Mode konfigurazioa aurkitu da (gtag('consent', ...)).",
    },
    "gdpr.consent.ok_rec": {
        "es": "Verifica que esté actualizado a la v2 enviando ad_user_data y ad_personalization.",
        "en": "Verify it is updated to v2 sending ad_user_data and ad_personalization.",
        "eu": "Egiaztatu v2ra eguneratuta dagoela ad_user_data eta ad_personalization bidaliz.",
    },
    "gdpr.consent.missing": {
        "es": "No se detectó configuración de Google Consent Mode.",
        "en": "Google Consent Mode configuration was not detected.",
        "eu": "Ez da Google Consent Mode konfiguraziorik detektatu.",
    },
    "gdpr.consent.missing_rec": {
        "es": "Si usas servicios de Google, es obligatorio implementar Consent Mode v2.",
        "en": "If you use Google services, implementing Consent Mode v2 is required.",
        "eu": "Google zerbitzuak erabiltzen badituzu, Consent Mode v2 inplementatzea beharrezkoa da.",
    },
    "gdpr.legal.name": {
        "es": "Páginas legales",
        "en": "Legal pages",
        "eu": "Lege-orriak",
    },
    "gdpr.legal.privacy": {
        "es": "Política de Privacidad",
        "en": "Privacy Policy",
        "eu": "Pribatutasun-politika",
    },
    "gdpr.legal.cookies": {
        "es": "Política de Cookies",
        "en": "Cookie Policy",
        "eu": "Cookie-politika",
    },
    "gdpr.legal.notice": {
        "es": "Aviso Legal",
        "en": "Legal Notice",
        "eu": "Lege-oharra",
    },
    "gdpr.legal.ok": {
        "es": "Se encontraron enlaces a la Política de Privacidad, Cookies y Aviso Legal.",
        "en": "Links to Privacy Policy, Cookies and Legal Notice were found.",
        "eu": "Pribatutasun, Cookie eta Lege-oharren estekak aurkitu dira.",
    },
    "gdpr.legal.missing": {
        "es": "Faltan enlaces legales clave: {list}.",
        "en": "Missing key legal links: {list}.",
        "eu": "Lege-esteka garrantzitsuak falta dira: {list}.",
    },
    "gdpr.legal.missing_rec": {
        "es": "Añade enlaces visibles en el footer a estas políticas. Es un requisito legal estricto.",
        "en": "Add visible footer links to these policies. This is a strict legal requirement.",
        "eu": "Gehitu footer-ean politika horien esteka ikusgaiak. Lege-betebehar zorrotza da.",
    },
    # --- Performance ---
    "perf.lcp.name": {
        "es": "Largest Contentful Paint (LCP)",
        "en": "Largest Contentful Paint (LCP)",
        "eu": "Largest Contentful Paint (LCP)",
    },
    "perf.lcp.msg": {
        "es": "Tiempo LCP: {value}",
        "en": "LCP time: {value}",
        "eu": "LCP denbora: {value}",
    },
    "perf.lcp.rec": {
        "es": "Optimiza la imagen/hero principal, el servidor y el CSS bloqueante.",
        "en": "Optimize the main hero/image, server response and render-blocking CSS.",
        "eu": "Optimizatu hero/irudi nagusia, zerbitzaria eta CSS blokeatzailea.",
    },
    "perf.cls.name": {
        "es": "Cumulative Layout Shift (CLS)",
        "en": "Cumulative Layout Shift (CLS)",
        "eu": "Cumulative Layout Shift (CLS)",
    },
    "perf.cls.msg": {
        "es": "Desplazamiento CLS: {value}",
        "en": "CLS shift: {value}",
        "eu": "CLS desplazamendua: {value}",
    },
    "perf.cls.rec": {
        "es": "Define width/height en imágenes y evita inyectar contenido encima del fold.",
        "en": "Set width/height on images and avoid injecting content above the fold.",
        "eu": "Definitu width/height irudietan eta saihestu foldaren gainean edukia txertatzea.",
    },
    "perf.fcp.name": {
        "es": "First Contentful Paint (FCP)",
        "en": "First Contentful Paint (FCP)",
        "eu": "First Contentful Paint (FCP)",
    },
    "perf.fcp.msg": {
        "es": "Tiempo FCP: {value}",
        "en": "FCP time: {value}",
        "eu": "FCP denbora: {value}",
    },
    "perf.fcp.rec": {
        "es": "Reduce CSS/JS bloqueante y mejora el tiempo hasta el primer contenido.",
        "en": "Reduce render-blocking CSS/JS and improve time to first content.",
        "eu": "Murriztu CSS/JS blokeatzailea eta hobetu lehen edukiaren denbora.",
    },
    "perf.ttfb.name": {
        "es": "Time to First Byte (TTFB)",
        "en": "Time to First Byte (TTFB)",
        "eu": "Time to First Byte (TTFB)",
    },
    "perf.ttfb.msg": {"es": "TTFB: {value}", "en": "TTFB: {value}", "eu": "TTFB: {value}"},
    "perf.ttfb.rec": {
        "es": "Mejora la respuesta del servidor, caché perimetral o hosting.",
        "en": "Improve server response, edge cache or hosting.",
        "eu": "Hobetu zerbitzariaren erantzuna, edge cachea edo hostinga.",
    },
    "perf.inp.name": {
        "es": "Interaction to Next Paint (INP)",
        "en": "Interaction to Next Paint (INP)",
        "eu": "Interaction to Next Paint (INP)",
    },
    "perf.inp.msg": {
        "es": "Retraso de interacción estimado: {value}",
        "en": "Estimated interaction delay: {value}",
        "eu": "Elkarreraginaren atzerapen estimatua: {value}",
    },
    "perf.inp.none": {
        "es": "Sin interacciones durante la medición (carga fría).",
        "en": "No interactions during measurement (cold load).",
        "eu": "Neurtzean ez dago elkarreraginik (karga hotza).",
    },
    "perf.inp.rec": {
        "es": "Reduce trabajo largo en el hilo principal y listeners pesados.",
        "en": "Reduce long main-thread work and heavy event listeners.",
        "eu": "Murriztu hari nagusiko lan luzea eta listener astunak.",
    },
    "perf.inp.none_rec": {
        "es": "INP se mide mejor con uso real; revisa JS pesado en clics/teclado.",
        "en": "INP is best measured with real usage; review heavy JS on click/keyboard.",
        "eu": "INP erabilera errealean neurtzen da hobeto; berrikusi JS astuna klik/teklatuan.",
    },
    "perf.size.name": {
        "es": "Tamaño de recursos",
        "en": "Resource size",
        "eu": "Baliabideen tamaina",
    },
    "perf.size.ok": {
        "es": "Transferencia ~{kb} KB en {n} recursos.",
        "en": "Transfer ~{kb} KB across {n} resources.",
        "eu": "Transferentzia ~{kb} KB {n} baliabidetan.",
    },
    "perf.size.warn": {
        "es": "Transferencia elevada (~{kb} KB, {heavy} recursos >500 KB).",
        "en": "High transfer (~{kb} KB, {heavy} resources >500 KB).",
        "eu": "Transferentzia handia (~{kb} KB, {heavy} baliabide >500 KB).",
    },
    "perf.size.fail": {
        "es": "Página pesada (~{kb} KB, {heavy} recursos >500 KB).",
        "en": "Heavy page (~{kb} KB, {heavy} resources >500 KB).",
        "eu": "Orrialde astuna (~{kb} KB, {heavy} baliabide >500 KB).",
    },
    "perf.size.examples": {
        "es": " Ejemplos: {list}",
        "en": " Examples: {list}",
        "eu": " Adibideak: {list}",
    },
    "perf.size.rec": {
        "es": "Comprime imágenes (WebP/AVIF), minifica assets y elimina JS innecesario.",
        "en": "Compress images (WebP/AVIF), minify assets and remove unused JS.",
        "eu": "Konprimitu irudiak (WebP/AVIF), minifyatu assetak eta kendu JS alferrikakoa.",
    },
    "perf.cache.name": {"es": "Caché HTTP", "en": "HTTP cache", "eu": "HTTP cachea"},
    "perf.cache.ok": {
        "es": "Cabecera Cache-Control presente en la respuesta principal.",
        "en": "Cache-Control header present on the main response.",
        "eu": "Cache-Control goiburua presente dago erantzun nagusian.",
    },
    "perf.cache.ok_rec": {
        "es": "Mantén políticas de caché adecuadas para estáticos.",
        "en": "Keep appropriate cache policies for static assets.",
        "eu": "Mantendu cache-politika egokiak asset estatikoentzat.",
    },
    "perf.cache.missing": {
        "es": "No se detectó Cache-Control útil en la respuesta principal.",
        "en": "No useful Cache-Control detected on the main response.",
        "eu": "Ez da Cache-Control erabilgarririk detektatu erantzun nagusian.",
    },
    "perf.cache.missing_rec": {
        "es": "Añade Cache-Control/ETag para recursos estáticos y HTML cuando proceda.",
        "en": "Add Cache-Control/ETag for static assets and HTML when appropriate.",
        "eu": "Gehitu Cache-Control/ETag asset estatikoetarako eta HTMLrako behar denean.",
    },
    "perf.error": {
        "es": "Error midiendo rendimiento local: {error}",
        "en": "Error measuring local performance: {error}",
        "eu": "Errorea tokiko errendimendua neurtzean: {error}",
    },
    # --- Accessibility ---
    "a11y.ok.name": {
        "es": "Sin violaciones de accesibilidad (Axe Core)",
        "en": "No accessibility violations (Axe Core)",
        "eu": "Irisgarritasun-hausturarik ez (Axe Core)",
    },
    "a11y.ok.msg": {
        "es": "No se encontraron errores críticos de accesibilidad (WCAG).",
        "en": "No critical accessibility issues found (WCAG).",
        "eu": "Ez da irisgarritasun-errore kritikorik aurkitu (WCAG).",
    },
    "a11y.ok.rec": {
        "es": "Sigue manteniendo estas buenas prácticas.",
        "en": "Keep maintaining these good practices.",
        "eu": "Mantendu praktika on hauek.",
    },
    "a11y.issue.name": {
        "es": "Axe: {id}",
        "en": "Axe: {id}",
        "eu": "Axe: {id}",
    },
    "a11y.error": {
        "es": "Error ejecutando Playwright/Axe: {error}. Recuerda ejecutar 'playwright install chromium'.",
        "en": "Error running Playwright/Axe: {error}. Remember to run 'playwright install chromium'.",
        "eu": "Errorea Playwright/Axe exekutatzean: {error}. Exekutatu 'playwright install chromium'.",
    },
    # Common axe rule helps (fallback still uses localized wrapper)
    "a11y.rule.color-contrast": {
        "es": "El contraste entre texto y fondo no cumple WCAG 2 AA.",
        "en": "Text/background contrast does not meet WCAG 2 AA.",
        "eu": "Testu/hondoaren kontrasteak ez du WCAG 2 AA betetzen.",
    },
    "a11y.rule.color-contrast.rec": {
        "es": "Aumenta el contraste del texto hasta cumplir el umbral mínimo.",
        "en": "Increase text contrast to meet the minimum threshold.",
        "eu": "Handitu testuaren kontrastea gutxieneko atalasea betetzeko.",
    },
    "a11y.rule.image-alt": {
        "es": "Hay imágenes sin texto alternativo adecuado.",
        "en": "Images are missing appropriate alternative text.",
        "eu": "Irudi batzuek ez dute ordezko testu egokirik.",
    },
    "a11y.rule.image-alt.rec": {
        "es": "Añade alt descriptivo a las imágenes significativas.",
        "en": "Add descriptive alt text to meaningful images.",
        "eu": "Gehitu alt deskriptiboa irudi esanguratsuei.",
    },
    "a11y.rule.link-name": {
        "es": "Hay enlaces sin texto discernible.",
        "en": "Links without discernible text were found.",
        "eu": "Testu bereizgarririk gabeko estekak aurkitu dira.",
    },
    "a11y.rule.link-name.rec": {
        "es": "Asegura que cada enlace tenga un nombre accesible.",
        "en": "Ensure every link has an accessible name.",
        "eu": "Ziurtatu esteka bakoitzak izen atzigarria duela.",
    },
    "a11y.rule.button-name": {
        "es": "Hay botones sin nombre accesible.",
        "en": "Buttons without an accessible name were found.",
        "eu": "Izen atzigarririk gabeko botoiak aurkitu dira.",
    },
    "a11y.rule.button-name.rec": {
        "es": "Añade texto visible o aria-label a los botones.",
        "en": "Add visible text or aria-label to buttons.",
        "eu": "Gehitu testu ikusgaia edo aria-label botoiei.",
    },
    "a11y.rule.generic": {
        "es": "Problema de accesibilidad detectado ({id}).",
        "en": "Accessibility issue detected ({id}).",
        "eu": "Irisgarritasun-arazoa detektatu da ({id}).",
    },
    "a11y.rule.generic.rec": {
        "es": "Revisa la guía WCAG correspondiente y corrige el elemento afectado.",
        "en": "Review the related WCAG guidance and fix the affected element.",
        "eu": "Berrikusi WCAG gida dagokiona eta zuzendu kaltetutako elementua.",
    },
}


def normalize_lang(lang: str | None) -> str:
    if not lang:
        return DEFAULT_LANG
    code = lang.lower().strip()[:2]
    return code if code in SUPPORTED else DEFAULT_LANG


def t(key: str, lang: str | None = DEFAULT_LANG, **kwargs: Any) -> str:
    lang = normalize_lang(lang)
    entry = MESSAGES.get(key) or {}
    template = entry.get(lang) or entry.get(DEFAULT_LANG) or key
    try:
        return template.format(**kwargs)
    except Exception:
        return template
