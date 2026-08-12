import pytest
from bs4 import BeautifulSoup
from analyzers.seo import SEOAnalyzer

@pytest.fixture
def sample_html():
    return """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <title>WebHealthIQ - Auditoría SEO Perfecta (Ejemplo)</title>
        <meta name="description" content="Esta es una descripción perfecta para la prueba unitaria que tiene más de 120 caracteres para asegurar que el check de longitud pasa sin problemas y de forma exitosa.">
        <link rel="canonical" href="https://example.com/test">
        <meta property="og:title" content="OG Title">
        <meta property="og:description" content="OG Desc">
        <meta property="og:image" content="image.jpg">
        <script type="application/ld+json">
        {
            "@context": "https://schema.org",
            "@type": "WebSite",
            "name": "Ejemplo"
        }
        </script>
    </head>
    <body>
        <h1>Título Principal Único</h1>
        <img src="logo.png" alt="Logo de la empresa">
        <img src="banner.jpg" alt="Banner promocional">
    </body>
    </html>
    """

@pytest.mark.asyncio
async def test_seo_analyzer_all_pass(sample_html):
    # Usamos un URL de prueba y mockearemos los requests asíncronos después si es necesario
    # Para estos tests unitarios, probamos solo el análisis estático
    analyzer = SEOAnalyzer("https://example.com/test", sample_html)
    
    title_res = analyzer._check_title()
    assert title_res["status"] == "pass"
    assert "WebHealthIQ" in title_res["data"]["title"]

    desc_res = analyzer._check_meta_description()
    assert desc_res["status"] == "pass"

    h1_res = analyzer._check_h1()
    assert h1_res["status"] == "pass"
    assert h1_res["data"]["h1"] == "Título Principal Único"

    alt_res = analyzer._check_images_alt()
    assert alt_res["status"] == "pass"

    canonical_res = analyzer._check_canonical()
    assert canonical_res["status"] == "pass"

    og_res = analyzer._check_open_graph()
    assert og_res["status"] == "pass"

    schema_res = analyzer._check_schema_org()
    assert schema_res["status"] == "pass"
