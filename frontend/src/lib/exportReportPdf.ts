import type { jsPDF } from "jspdf";
import { LOGO_SRC } from "@/lib/brandAssets";

type Check = {
  name?: string;
  status?: string;
  message?: string;
  recommendation?: string;
};

type ModuleBlock = {
  score?: number;
  checks?: Check[];
  error?: string;
};

type InsightAction = {
  module?: string;
  status?: string;
  name?: string;
  message?: string;
  recommendation?: string;
};

type AuditResult = {
  url: string;
  overall_score: number;
  timestamp?: string;
  modules?: Record<string, ModuleBlock>;
  insights?: {
    title?: string;
    summary?: string;
    actions?: InsightAction[];
  } | null;
};

const MODULE_ORDER = [
  ["seo", "SEO"],
  ["performance", "Rendimiento"],
  ["accessibility", "Accesibilidad"],
  ["security", "Seguridad"],
  ["gdpr", "RGPD"],
] as const;

const BRAND = {
  primary: [13, 110, 99] as const, // #0d6e63
  primaryDark: [10, 85, 76] as const,
  accent: [228, 87, 46] as const, // #e4572e
  ink: [13, 26, 22] as const,
  muted: [90, 110, 104] as const,
  line: [220, 228, 224] as const,
  surface: [246, 249, 248] as const,
  pass: [22, 101, 52] as const,
  warn: [161, 98, 7] as const,
  fail: [185, 28, 28] as const,
  white: [255, 255, 255] as const,
};

function safeText(value: unknown, max = 240): string {
  const s = String(value ?? "")
    .replace(/\s+/g, " ")
    .trim();
  return s.length > max ? `${s.slice(0, max - 1)}…` : s;
}

function rgb(doc: jsPDF, c: readonly [number, number, number]) {
  doc.setTextColor(c[0], c[1], c[2]);
}

function fill(doc: jsPDF, c: readonly [number, number, number]) {
  doc.setFillColor(c[0], c[1], c[2]);
}

function stroke(doc: jsPDF, c: readonly [number, number, number]) {
  doc.setDrawColor(c[0], c[1], c[2]);
}

function scoreColor(score: number): readonly [number, number, number] {
  if (score >= 80) return BRAND.pass;
  if (score >= 55) return BRAND.warn;
  return BRAND.fail;
}

function statusMeta(status?: string) {
  const s = (status || "").toLowerCase();
  if (s === "pass") return { label: "OK", color: BRAND.pass, bg: [220, 252, 231] as const };
  if (s === "warning") return { label: "AVISO", color: BRAND.warn, bg: [254, 243, 199] as const };
  if (s === "fail") return { label: "FAIL", color: BRAND.fail, bg: [254, 226, 226] as const };
  return { label: "—", color: BRAND.muted, bg: BRAND.surface };
}

async function loadLogoDataUrl(): Promise<string | null> {
  try {
    const res = await fetch(LOGO_SRC);
    if (!res.ok) return null;
    const blob = await res.blob();
    return await new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = () => resolve(String(reader.result || ""));
      reader.onerror = () => reject(reader.error);
      reader.readAsDataURL(blob);
    });
  } catch {
    return null;
  }
}

function wrappedHeight(doc: jsPDF, text: string, maxWidth: number, lineHeight: number): number {
  const lines = doc.splitTextToSize(text, maxWidth) as string[];
  return Math.max(lineHeight, lines.length * lineHeight);
}

function drawWrapped(
  doc: jsPDF,
  text: string,
  x: number,
  y: number,
  maxWidth: number,
  lineHeight = 4.6
): number {
  const lines = doc.splitTextToSize(text, maxWidth) as string[];
  doc.text(lines, x, y);
  return y + lines.length * lineHeight;
}

function drawFooter(
  doc: jsPDF,
  page: number,
  total: number,
  brand: string,
  pageW: number,
  pageH: number
) {
  const y = pageH - 12;
  stroke(doc, BRAND.line);
  doc.setLineWidth(0.3);
  doc.line(16, y - 4, pageW - 16, y - 4);
  doc.setFont("helvetica", "normal");
  doc.setFontSize(7.5);
  rgb(doc, BRAND.muted);
  doc.text(`${brand} · webhealthiq.com`, 16, y);
  doc.text(`${page} / ${total}`, pageW - 16, y, { align: "right" });
}

function drawScoreRing(
  doc: jsPDF,
  cx: number,
  cy: number,
  r: number,
  score: number
) {
  const color = scoreColor(score);
  stroke(doc, BRAND.line);
  doc.setLineWidth(3.2);
  doc.circle(cx, cy, r, "S");

  // Approximate arc with thick colored segment via pie slices
  const pct = Math.max(0, Math.min(100, score)) / 100;
  const steps = Math.max(2, Math.round(48 * pct));
  fill(doc, color);
  for (let i = 0; i < steps; i++) {
    const a0 = -90 + (360 * pct * i) / steps;
    const a1 = -90 + (360 * pct * (i + 1)) / steps;
    // jsPDF doesn't have arc easily; draw thin wedges as lines on circle
    const rad0 = (a0 * Math.PI) / 180;
    const rad1 = (a1 * Math.PI) / 180;
    stroke(doc, color);
    doc.setLineWidth(3.2);
    doc.line(
      cx + Math.cos(rad0) * r,
      cy + Math.sin(rad0) * r,
      cx + Math.cos(rad1) * r,
      cy + Math.sin(rad1) * r
    );
  }

  fill(doc, BRAND.white);
  doc.circle(cx, cy, r - 4.5, "F");
  doc.setFont("helvetica", "bold");
  doc.setFontSize(22);
  rgb(doc, color);
  doc.text(String(score), cx, cy + 2, { align: "center" });
  doc.setFont("helvetica", "normal");
  doc.setFontSize(7);
  rgb(doc, BRAND.muted);
  doc.text("/ 100", cx, cy + 8, { align: "center" });
}

export async function downloadAuditPdf(
  result: AuditResult,
  opts: { title: string; brand?: string }
): Promise<void> {
  const { jsPDF } = await import("jspdf");
  const doc = new jsPDF({ unit: "mm", format: "a4" });
  const margin = 16;
  const pageW = doc.internal.pageSize.getWidth();
  const pageH = doc.internal.pageSize.getHeight();
  const contentW = pageW - margin * 2;
  const brand = (opts.brand || "WebHealthIQ").trim() || "WebHealthIQ";
  const logo = await loadLogoDataUrl();

  let y = 0;

  const newPage = () => {
    doc.addPage();
    y = margin + 6;
  };

  const ensureSpace = (needed: number) => {
    if (y + needed > pageH - 22) newPage();
  };

  // ——— Cover / header ———
  fill(doc, BRAND.primary);
  doc.rect(0, 0, pageW, 42, "F");
  fill(doc, BRAND.accent);
  doc.rect(0, 42, pageW, 1.6, "F");

  if (logo) {
    try {
      doc.addImage(logo, "PNG", margin, 10, 14, 14);
    } catch {
      // ignore broken logo
    }
  }

  doc.setFont("helvetica", "bold");
  doc.setFontSize(16);
  rgb(doc, BRAND.white);
  doc.text(brand, logo ? margin + 18 : margin, 16);
  doc.setFont("helvetica", "normal");
  doc.setFontSize(9);
  doc.text(opts.title || "Informe de auditoría", logo ? margin + 18 : margin, 23);

  // Score card
  y = 54;
  fill(doc, BRAND.surface);
  stroke(doc, BRAND.line);
  doc.setLineWidth(0.4);
  doc.roundedRect(margin, y, contentW, 38, 3, 3, "FD");

  drawScoreRing(doc, margin + 24, y + 19, 12, result.overall_score);

  doc.setFont("helvetica", "bold");
  doc.setFontSize(11);
  rgb(doc, BRAND.ink);
  doc.text("Puntuación global", margin + 44, y + 12);
  doc.setFont("helvetica", "normal");
  doc.setFontSize(9);
  rgb(doc, BRAND.muted);
  const urlLine = safeText(result.url, 70);
  doc.text(urlLine, margin + 44, y + 19);
  if (result.timestamp) {
    doc.text(safeText(result.timestamp, 40), margin + 44, y + 26);
  }
  doc.setFontSize(8);
  doc.text("Auditoría automatizada · SEO · Perf · A11y · Seguridad · RGPD", margin + 44, y + 32);

  y = 102;

  // Module score strip
  const modulesPresent = MODULE_ORDER.filter(([key]) => result.modules?.[key]);
  if (modulesPresent.length) {
    const gap = 3;
    const boxW = (contentW - gap * (modulesPresent.length - 1)) / modulesPresent.length;
    modulesPresent.forEach(([key, label], i) => {
      const mod = result.modules?.[key];
      const score = typeof mod?.score === "number" ? mod.score : 0;
      const x = margin + i * (boxW + gap);
      fill(doc, BRAND.white);
      stroke(doc, BRAND.line);
      doc.roundedRect(x, y, boxW, 18, 2, 2, "FD");
      const c = scoreColor(score);
      fill(doc, c);
      doc.roundedRect(x, y, 2.2, 18, 1, 1, "F");
      doc.setFont("helvetica", "bold");
      doc.setFontSize(8);
      rgb(doc, BRAND.ink);
      doc.text(label, x + 5, y + 7);
      doc.setFontSize(11);
      rgb(doc, c);
      doc.text(String(score), x + 5, y + 14);
    });
    y += 26;
  }

  // Insights
  const insights = result.insights;
  if (insights?.summary || (insights?.actions && insights.actions.length)) {
    ensureSpace(28);
    fill(doc, [255, 247, 237]);
    stroke(doc, BRAND.accent);
    doc.setLineWidth(0.5);
    doc.roundedRect(margin, y, contentW, 8, 2, 2, "S");
    fill(doc, BRAND.accent);
    doc.roundedRect(margin, y, contentW, 8, 2, 2, "F");
    doc.setFont("helvetica", "bold");
    doc.setFontSize(10);
    rgb(doc, BRAND.white);
    doc.text(safeText(insights.title || "Plan de acción", 60), margin + 4, y + 5.5);
    y += 12;

    if (insights.summary) {
      doc.setFont("helvetica", "normal");
      doc.setFontSize(9);
      rgb(doc, BRAND.ink);
      y = drawWrapped(doc, safeText(insights.summary, 320), margin, y, contentW, 4.5);
      y += 3;
    }

    for (const action of (insights.actions || []).slice(0, 6)) {
      const meta = statusMeta(action.status);
      const title = safeText(action.name || action.module || "Acción", 70);
      const body = safeText(action.recommendation || action.message || "", 200);
      const h =
        7 +
        wrappedHeight(doc, title, contentW - 22, 4.4) +
        (body ? wrappedHeight(doc, body, contentW - 10, 4.2) : 0);
      ensureSpace(h + 4);
      fill(doc, BRAND.white);
      stroke(doc, BRAND.line);
      doc.setLineWidth(0.35);
      doc.roundedRect(margin, y, contentW, h, 2, 2, "FD");
      fill(doc, meta.bg);
      doc.roundedRect(margin + 3, y + 2.5, 14, 5, 1, 1, "F");
      doc.setFont("helvetica", "bold");
      doc.setFontSize(6.5);
      rgb(doc, meta.color);
      doc.text(meta.label, margin + 10, y + 5.8, { align: "center" });
      doc.setFontSize(9);
      rgb(doc, BRAND.ink);
      let yy = drawWrapped(doc, title, margin + 20, y + 5.5, contentW - 24, 4.4);
      if (body) {
        doc.setFont("helvetica", "normal");
        doc.setFontSize(8);
        rgb(doc, BRAND.muted);
        yy = drawWrapped(doc, body, margin + 4, yy + 1, contentW - 8, 4.2);
      }
      y += h + 3;
    }
    y += 2;
  }

  // Modules detail
  for (const [key, label] of MODULE_ORDER) {
    const mod = result.modules?.[key];
    if (!mod) continue;

    ensureSpace(22);
    const score = typeof mod.score === "number" ? mod.score : null;
    const c = score == null ? BRAND.muted : scoreColor(score);

    fill(doc, BRAND.primary);
    doc.roundedRect(margin, y, contentW, 9, 2, 2, "F");
    doc.setFont("helvetica", "bold");
    doc.setFontSize(11);
    rgb(doc, BRAND.white);
    doc.text(label, margin + 4, y + 6);
    if (score != null) {
      fill(doc, BRAND.white);
      doc.roundedRect(pageW - margin - 22, y + 1.8, 18, 5.4, 1.5, 1.5, "F");
      doc.setFontSize(9);
      rgb(doc, c);
      doc.text(`${score}`, pageW - margin - 13, y + 5.5, { align: "center" });
    }
    y += 13;

    if (mod.error) {
      doc.setFont("helvetica", "normal");
      doc.setFontSize(9);
      rgb(doc, BRAND.fail);
      y = drawWrapped(doc, safeText(mod.error, 400), margin, y, contentW, 4.5);
      y += 6;
      continue;
    }

    const checks = Array.isArray(mod.checks) ? mod.checks : [];
    for (const check of checks.slice(0, 14)) {
      const meta = statusMeta(check.status);
      const name = safeText(check.name || "Check", 90);
      const message = check.message ? safeText(check.message, 220) : "";
      const rec =
        check.status !== "pass" && check.recommendation
          ? safeText(check.recommendation, 220)
          : "";

      doc.setFont("helvetica", "bold");
      doc.setFontSize(9);
      const nameH = wrappedHeight(doc, name, contentW - 24, 4.4);
      doc.setFont("helvetica", "normal");
      doc.setFontSize(8);
      const msgH = message ? wrappedHeight(doc, message, contentW - 8, 4.1) : 0;
      const recH = rec ? wrappedHeight(doc, `→ ${rec}`, contentW - 8, 4.1) : 0;
      const boxH = 8 + nameH + msgH + recH;

      ensureSpace(boxH + 3);
      fill(doc, BRAND.white);
      stroke(doc, BRAND.line);
      doc.setLineWidth(0.3);
      doc.roundedRect(margin, y, contentW, boxH, 1.8, 1.8, "FD");

      fill(doc, meta.bg);
      doc.roundedRect(margin + 2.5, y + 2.2, 16, 5, 1.2, 1.2, "F");
      doc.setFont("helvetica", "bold");
      doc.setFontSize(6.5);
      rgb(doc, meta.color);
      doc.text(meta.label, margin + 10.5, y + 5.5, { align: "center" });

      doc.setFontSize(9);
      rgb(doc, BRAND.ink);
      let yy = drawWrapped(doc, name, margin + 22, y + 5.5, contentW - 26, 4.4);

      if (message) {
        doc.setFont("helvetica", "normal");
        doc.setFontSize(8);
        rgb(doc, BRAND.muted);
        yy = drawWrapped(doc, message, margin + 4, yy + 0.8, contentW - 8, 4.1);
      }
      if (rec) {
        doc.setFont("helvetica", "italic");
        doc.setFontSize(8);
        rgb(doc, BRAND.primaryDark);
        drawWrapped(doc, `→ ${rec}`, margin + 4, yy + 0.6, contentW - 8, 4.1);
      }
      y += boxH + 2.5;
    }
    y += 4;
  }

  // Page footers
  const total = doc.getNumberOfPages();
  for (let i = 1; i <= total; i++) {
    doc.setPage(i);
    drawFooter(doc, i, total, brand, pageW, pageH);
  }

  const host = result.url
    .replace(/^https?:\/\//, "")
    .replace(/[^\w.-]+/g, "_")
    .slice(0, 40);
  doc.save(`webhealthiq-${host || "report"}.pdf`);
}
