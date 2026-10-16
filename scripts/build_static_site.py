#!/usr/bin/env python3
"""
build_static_site.py
Generador estático profesional para la migración de PREXIA Google Sites a HTML/Git.
Aplica el sistema de diseño editorial anti-slop (Taste Skill) con Libre Franklin + Source Serif 4,
e incorpora la documentación completa del Sistema de Evaluación Prexia (Puntos y Multiplicadores).
"""
from __future__ import annotations

import html
import json
import shutil
from collections import defaultdict
from pathlib import Path
from urllib.parse import unquote, urlparse


PROJECT_ROOT = Path(__file__).resolve().parent.parent
SOURCE_DIR = PROJECT_ROOT / "scraped_site_clean"
OUTPUT_DIR = PROJECT_ROOT / "site"

CSS = """
:root {
  --bg: #f7f7f5;
  --surface: #ecebe6;
  --surface-alt: #e3e2dc;
  --surface-card: #fdfdfc;
  --ink: #1f1a3a;
  --muted: #4e4a68;
  --line: rgba(31, 26, 58, 0.12);
  --mint-dark: #15803d;
  --mint-light: #84fbaa;
  --field-navy: #1f1a3a;
  --field-navy-surface: #2b244d;
  --field-navy-ink: #f7f7f5;
  --field-navy-muted: #b8b3d1;
  --radius: 2px;
  --margin: clamp(1.25rem, 3.2vw, 3rem);
  --gutter: clamp(1rem, 2vw, 2rem);
  --font-display: 'Libre Franklin', -apple-system, BlinkMacSystemFont, sans-serif;
  --font-text: 'Source Serif 4', Georgia, serif;
  --ease-out: cubic-bezier(0.22, 1, 0.36, 1);
}

*, *::before, *::after {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

html {
  scroll-behavior: smooth;
  background: var(--bg);
  color: var(--ink);
}

body {
  margin: 0;
  font-family: var(--font-text);
  font-size: 17px;
  line-height: 1.62;
  color: var(--ink);
  background: var(--bg);
  -webkit-font-smoothing: antialiased;
  overflow-x: clip;
}

a {
  color: inherit;
  text-decoration: none;
}

img {
  display: block;
  max-width: 100%;
  height: auto;
}

.shell {
  width: min(1200px, calc(100% - var(--margin) * 2));
  margin: 0 auto;
}

/* ── TOPBAR EDITORIAL ── */
.topbar {
  background: var(--bg);
  padding: 24px 0 20px;
}

.topbar-inner {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: var(--gutter);
  flex-wrap: wrap;
}

.brand {
  display: flex;
  align-items: baseline;
  gap: 10px;
  font-family: var(--font-display);
  font-size: 1.15rem;
  font-weight: 800;
  letter-spacing: -0.02em;
  color: var(--ink);
}

.brand-sub {
  font-family: var(--font-text);
  font-size: 14px;
  font-weight: 400;
  color: var(--muted);
}

.nav-links {
  display: flex;
  align-items: baseline;
  gap: 24px;
  flex-wrap: wrap;
}

.nav-links a {
  font-family: var(--font-display);
  font-size: 14px;
  font-weight: 700;
  color: var(--muted);
  transition: color 0.2s ease-out;
}

.nav-links a:hover,
.nav-links a.active {
  color: var(--ink);
}

.nav-action {
  font-family: var(--font-display);
  font-size: 14px;
  font-weight: 700;
  color: var(--ink);
  text-decoration: underline;
  text-underline-offset: 4px;
}

/* ── HERO ARCHIVO / CATÁLOGO ── */
.archive-hero {
  padding: 64px 0 48px;
}

.archive-hero-grid {
  display: grid;
  grid-template-columns: minmax(0, 55%) 1fr;
  gap: var(--gutter);
  align-items: end;
}

.archive-hero-title {
  font-family: var(--font-display);
  font-size: clamp(2.8rem, 8.2vw, 6.4rem);
  font-weight: 800;
  line-height: 0.95;
  letter-spacing: -0.035em;
  color: var(--ink);
  margin-bottom: 20px;
}

.archive-lead {
  font-size: 1.15rem;
  line-height: 1.6;
  color: var(--muted);
  max-width: 50ch;
}

.archive-stats-box {
  background: var(--surface);
  padding: 32px;
  border-radius: var(--radius);
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

.stat-unit strong {
  display: block;
  font-family: var(--font-display);
  font-size: 2.4rem;
  font-weight: 800;
  line-height: 1;
  color: var(--ink);
  margin-bottom: 4px;
}

.stat-unit span {
  font-size: 14px;
  color: var(--muted);
}

/* ── SECCIONES Y GRILLAS ── */
.section {
  padding: 56px 0;
}

.section-header {
  margin-bottom: 32px;
}

.section-title {
  font-family: var(--font-display);
  font-size: clamp(1.8rem, 2.8vw, 2.6rem);
  font-weight: 800;
  letter-spacing: -0.02em;
  color: var(--ink);
  margin-bottom: 8px;
}

.section-desc {
  font-size: 1.1rem;
  color: var(--muted);
  max-width: 58ch;
}

.grid-cards {
  display: grid;
  grid-template-columns: repeat(12, minmax(0, 1fr));
  gap: 24px;
}

.card {
  background: var(--surface);
  padding: 28px;
  border-radius: var(--radius);
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.card.span-4 { grid-column: span 4; }
.card.span-6 { grid-column: span 6; }
.card.span-12 { grid-column: span 12; }

.card-cover {
  aspect-ratio: 16/10;
  overflow: hidden;
  margin-bottom: 20px;
  background: #dedcd5;
}

.card-cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  filter: grayscale(1) contrast(1.05);
  transition: filter 0.3s var(--ease-out);
}

.card:hover .card-cover img {
  filter: none;
}

.card-meta-tag {
  font-family: var(--font-display);
  font-size: 13px;
  font-weight: 700;
  color: #166534;
  margin-bottom: 8px;
}

.card-title {
  font-family: var(--font-display);
  font-size: 1.35rem;
  font-weight: 800;
  line-height: 1.2;
  color: var(--ink);
  margin-bottom: 12px;
}

.card-excerpt {
  font-size: 16px;
  line-height: 1.58;
  color: var(--ink);
  margin-bottom: 20px;
}

.btn-card {
  font-family: var(--font-display);
  font-size: 14px;
  font-weight: 700;
  color: var(--ink);
  text-decoration: underline;
  text-underline-offset: 4px;
  margin-top: auto;
}

/* ── LAYOUT DE PÁGINA INDIVIDUAL ── */
.page-layout {
  display: grid;
  grid-template-columns: minmax(0, 68%) 1fr;
  gap: calc(var(--gutter) * 2);
  padding: 56px 0 96px;
  align-items: start;
}

.page-article {
  background: var(--bg);
}

.breadcrumb-trail {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  font-size: 14px;
  color: var(--muted);
  margin-top: 14px;
  margin-bottom: 24px;
}

.breadcrumb-trail span + span::before {
  content: " / ";
  color: var(--muted);
  padding: 0 4px;
}

.breadcrumb-trail a {
  color: var(--muted);
  text-decoration: underline;
  text-underline-offset: 3px;
}

.breadcrumb-trail a:hover {
  color: var(--ink);
}

.page-title {
  font-family: var(--font-display);
  font-size: clamp(2.2rem, 3.6vw, 3.6rem);
  font-weight: 800;
  line-height: 1.05;
  letter-spacing: -0.03em;
  color: var(--ink);
  margin-bottom: 8px;
}

.meta-original {
  font-size: 14px;
  color: var(--muted);
  margin-bottom: 32px;
  padding-bottom: 12px;
}

.reveal-item {
  opacity: 0;
  transform: translateY(14px);
  transition: opacity 0.5s cubic-bezier(0.16, 1, 0.3, 1), transform 0.5s cubic-bezier(0.16, 1, 0.3, 1);
}

.reveal-item.is-visible {
  opacity: 1;
  transform: none;
}

@media (prefers-reduced-motion: reduce) {
  .reveal-item {
    opacity: 1 !important;
    transform: none !important;
    transition: none !important;
  }
}

.meta-original a {
  text-decoration: underline;
}

.page-copy {
  max-width: 68ch;
}

.page-copy p {
  font-size: 17px;
  line-height: 1.68;
  color: var(--ink);
  margin-bottom: 22px;
}

.page-copy h2,
.page-copy h3,
.editorial-subhead {
  font-family: var(--font-display);
  font-size: 1.35rem;
  font-weight: 800;
  line-height: 1.25;
  color: var(--ink);
  margin-top: 36px;
  margin-bottom: 14px;
}

.page-copy ul,
.page-copy ol {
  margin: 16px 0 24px 24px;
}

.page-copy li {
  margin-bottom: 8px;
  line-height: 1.55;
}

/* ── GALERÍA DE IMÁGENES ── */
.gallery-section {
  margin-top: 56px;
  padding-top: 36px;
  border-top: 1px solid var(--line); /* taste-skill-ignore */
}

.gallery-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 16px;
  margin-top: 20px;
}

.gallery-thumb {
  aspect-ratio: 1/1;
  overflow: hidden;
  background: var(--surface);
  border-radius: var(--radius);
}

.gallery-thumb img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  filter: grayscale(1) contrast(1.05);
  transition: filter 0.3s var(--ease-out);
}

.gallery-thumb:hover img {
  filter: none;
}

/* ── SIDEBAR EDITORIAL ── */
.sidebar {
  display: flex;
  flex-direction: column;
  gap: 32px;
  position: sticky;
  top: 32px;
}

.sidebar-box {
  background: var(--surface);
  padding: 24px;
  border-radius: var(--radius);
}

.sidebar-heading {
  font-family: var(--font-display);
  font-size: 14px;
  font-weight: 800;
  letter-spacing: 0.04em;
  color: var(--ink);
  margin-bottom: 14px;
}

.sidebar-nav-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.sidebar-nav-item {
  font-size: 14px;
  color: var(--muted);
  padding: 6px 0;
  line-height: 1.4;
  transition: color 0.15s ease-out;
}

.sidebar-nav-item:hover {
  color: var(--ink);
}

.sidebar-nav-item.active {
  font-weight: 700;
  color: var(--ink);
}

/* ── TABLAS FORMALES (PDF PREXIA) ── */
.prexia-table {
  width: 100%;
  border-collapse: collapse;
  margin: 28px 0;
  font-size: 15px;
}

.prexia-table th,
.prexia-table td {
  padding: 12px 14px;
  text-align: left;
  border-bottom: 1px solid var(--line); /* taste-skill-ignore */
}

.prexia-table th {
  font-family: var(--font-display);
  font-weight: 800;
  color: var(--ink);
  background: var(--surface);
}

.prexia-table tr:hover td {
  background: rgba(0,0,0,0.02);
}

/* ── FOOTER SITIO ── */
.site-footer {
  background: var(--field-navy);
  color: var(--field-navy-ink);
  padding: 64px 0 48px;
  margin-top: 80px;
}

.footer-inner {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  flex-wrap: wrap;
  gap: 24px;
}

.footer-info h4 {
  font-family: var(--font-display);
  font-size: 1.25rem;
  font-weight: 800;
  margin-bottom: 8px;
}

.footer-info p {
  font-size: 14px;
  color: var(--field-navy-muted);
  max-width: 48ch;
  line-height: 1.5;
}

.footer-links-row {
  display: flex;
  gap: 24px;
  flex-wrap: wrap;
}

.footer-links-row a {
  font-size: 14px;
  color: var(--field-navy-muted);
}

.footer-links-row a:hover {
  color: var(--field-navy-ink);
}

@media (max-width: 900px) {
  .archive-hero-grid,
  .page-layout {
    grid-template-columns: 1fr;
  }
  .card.span-4,
  .card.span-6 {
    grid-column: span 12;
  }
}
"""


def load_manifest() -> dict:
    return json.loads((SOURCE_DIR / "manifest.json").read_text(encoding="utf-8"))


def parse_markdown(path: Path) -> tuple[list[str], list[str]]:
    text = path.read_text(encoding="utf-8").splitlines()
    lines: list[str] = []
    images: list[str] = []
    mode = None
    for line in text:
        if line == "## Texto extraido":
            mode = "text"
            continue
        if line == "## Imagenes":
            mode = "images"
            continue
        if not line.strip():
            continue
        if mode == "text":
            lines.append(line.strip())
        elif mode == "images" and line.startswith("- "):
            image_path = line[2:].split(" (", 1)[0].strip()
            if image_path:
                images.append(image_path)
    return lines, images


def normalize_text_lines(lines: list[str]) -> list[str]:
    merged: list[str] = []
    for line in lines:
        line = " ".join(line.split())
        if not line:
            continue
        if not merged:
            merged.append(line)
            continue

        previous = merged[-1]
        should_merge = False
        if (
            previous
            and not previous.endswith((".", ":", "?", "!"))
            and not previous.isupper()
            and (line[:1].islower() or len(previous) < 26)
        ):
            should_merge = True

        if should_merge:
            merged[-1] = f"{previous} {line}"
        else:
            merged.append(line)
    return merged


def title_case_from_segment(segment: str) -> str:
    raw = unquote(segment).replace("-", " ")
    return " ".join(part.capitalize() for part in raw.split())


def page_output_name(slug: str) -> str:
    return f"{slug}.html"


def page_href(slug: str) -> str:
    return f"pages/{page_output_name(slug)}"


def build_evaluation_page(root_prefix: str = "../") -> str:
    """Genera la página completa dedicada al Sistema de Evaluación Prexia (PDF)."""
    return f"""
<main class="shell page-layout">
  <article class="page-article">
    <h1 class="page-title">Sistema de Evaluación Prexia: Puntos y Multiplicadores</h1>
    <nav class="breadcrumb-trail" aria-label="Ruta de navegación">
      <span><a href="{root_prefix}index.html">Directorio</a></span>
      <span><a href="{root_prefix}../index.html">Inicio PREXIA</a></span>
      <span>Sistema de Evaluación (PP)</span>
    </nav>
    <div class="eval-hero-actions" style="margin: 20px 0 28px; display: flex; gap: 16px; flex-wrap: wrap;">
      <a href="#simulador" class="btn-primary" style="display:inline-flex; align-items:center; height:46px; padding:0 24px; background:var(--ink); color:var(--bg); font-family:var(--font-display); font-size:15px; font-weight:700; border-radius:var(--radius); text-decoration:none;">Simulador de Puntos Prexia</a>
      <a href="{root_prefix}index.html" class="btn-secondary" style="display:inline-flex; align-items:center; height:46px; padding:0 24px; background:var(--surface); color:var(--ink); font-family:var(--font-display); font-size:15px; font-weight:700; border-radius:var(--radius); text-decoration:none;">Catálogo de Páginas Migradas</a>
    </div>
    <p class="meta-original">
      Documento oficial de gestión del rendimiento y reconocimiento formativo en la Facultad de Minas, Universidad Nacional de Colombia.
    </p>

    <div class="page-copy">
      <h2>1. Propósito y Fundamentación Teórica</h2>
      <p>
        El sistema mide el aporte de cada integrante de la línea de Consultoría en <strong>Puntos Prexia (PP)</strong>, no en horas reloj, y ajusta la exigencia al nivel de avance real de su carrera de ingeniería.
      </p>
      <p>
        Medir únicamente horas presenciales en una facultad de ingeniería presenta distorsiones graves: castiga a quien cursa materias de alta exigencia (Cálculo, Álgebra Lineal, Física) cuyo tiempo libre es fragmentado, y premia la permanencia pasiva sin entregables concretos.
      </p>
      <p>
        El modelo se sustenta en dos pilares organizacionales contrastados:
      </p>
      <ul>
        <li><strong>Teoría de las Características del Puesto (Hackman & Oldham):</strong> Estructuración de tareas con significado claro, autonomía en la ejecución y retroalimentación directa por resultados.</li>
        <li><strong>Motivación Intrínseca (Daniel Pink):</strong> Tres palancas centrales: <em>Autonomía</em> (gestión de tiempos acordados), <em>Maestría</em> (crecimiento de rol formativo) y <em>Propósito</em> (impacto directo en organizaciones reales).</li>
      </ul>

      <h2>2. Los Cuatro Niveles de Avance de Carrera</h2>
      <p>
        En planes curriculares de diez semestres (160 a 180 créditos), el perfil del estudiante evoluciona profundamente. La exigencia se clasifica en cuatro ciclos de formación:
      </p>

      <table class="prexia-table" data-ui>
        <thead>
          <tr>
            <th>Nivel</th>
            <th>Avance (%)</th>
            <th>Semestres</th>
            <th>Rol Formativo</th>
            <th>Tipo de Aporte Esperado</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td><strong>Nivel 1: Fundamentación</strong></td>
            <td>0% a 25%</td>
            <td>1 a 2</td>
            <td>Operativo</td>
            <td>Tareas operativas cortas, apoyo logístico a eventos, recopilación de cápsulas de conocimiento y difusión.</td>
          </tr>
          <tr>
            <td><strong>Nivel 2: Transición</strong></td>
            <td>26% a 50%</td>
            <td>3 a 5</td>
            <td>Gestor</td>
            <td>Liderazgo en mesas temáticas, marketing digital, eventos de bienestar, comunidad y simulaciones de ventas.</td>
          </tr>
          <tr>
            <td><strong>Nivel 3: Profesionalización</strong></td>
            <td>51% a 75%</td>
            <td>6 a 8</td>
            <td>Consultor Junior</td>
            <td>Diagnóstico empresarial a MiPymes, diseño curricular de casos de simulación, analítica y meta del 80% de productividad de línea.</td>
          </tr>
          <tr>
            <td><strong>Nivel 4: Cierre y Proyección</strong></td>
            <td>> 75%</td>
            <td>9 a 10</td>
            <td>Líder</td>
            <td>Gerencia de proyectos, mentoría a pares, enlace con expertos externos y acuerdos de retribución sobre impacto económico.</td>
          </tr>
        </tbody>
      </table>

      <h2>3. Curva Semanal Progresiva de Metas</h2>
      <p>
        Al inicio de cada semestre, cada estudiante suscribe un pacto horario voluntario (POA). La meta base semanal de cada integrante nace de esa concertación:
      </p>
      <p style="background:var(--surface);padding:18px;border-radius:var(--radius);font-family:var(--font-display);font-weight:700;">
        1 Hora Pactada = 100 Puntos Prexia (PP) base por semana.<br>
        Ejemplo: 4 horas semanales pactadas = 400 PP base.
      </p>
      <p>
        La meta no es estática: sube 1% de la base cada semana lectiva hasta alcanzar el <strong>110% en la semana diez</strong> (cierre de semestre). Para cubrir ese incremento sin trabajar más horas reloj, los integrantes activan <em>multiplicadores de calidad</em>.
      </p>

      <h2>4. Matriz Oficial de Factores Multiplicadores</h2>
      <p>
        Cada multiplicador bonifica un porcentaje sobre la meta base semanal y responde directamente a un indicador del Plan Operativo Anual (POA):
      </p>

      <table class="prexia-table" data-ui>
        <thead>
          <tr>
            <th>Nivel</th>
            <th>Multiplicador</th>
            <th>Bono</th>
            <th>Criterio y Condición de Acreditación</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td><strong>Nivel 1</strong></td>
            <td>Excelencia en Contenido</td>
            <td>+3%</td>
            <td>Calendario de publicaciones cumplido al 100% sin retrasos ni objeciones de fondo.</td>
          </tr>
          <tr>
            <td><strong>Nivel 1</strong></td>
            <td>Generación de Valor</td>
            <td>+3%</td>
            <td>Cada cápsula de conocimiento adicional documentada, editada y publicada.</td>
          </tr>
          <tr>
            <td><strong>Nivel 1</strong></td>
            <td>Cultura Consultor</td>
            <td>+2%</td>
            <td>Participación en el diseño de material pedagógico sobre la cultura PREXIA.</td>
          </tr>
          <tr>
            <td><strong>Nivel 2</strong></td>
            <td>Tracción Web y Redes</td>
            <td>+3%</td>
            <td>Crecimiento medido de audiencia en canales del semillero superior al 10%.</td>
          </tr>
          <tr>
            <td><strong>Nivel 2</strong></td>
            <td>Poder de Convocatoria</td>
            <td>+3%</td>
            <td>Asistencia y participación efectiva del 80% o más de integrantes en eventos.</td>
          </tr>
          <tr>
            <td><strong>Nivel 2</strong></td>
            <td>Celebración y Bienestar</td>
            <td>+2%</td>
            <td>100% de fechas conmemorativas celebradas y reconocimientos individuales otorgados.</td>
          </tr>
          <tr>
            <td><strong>Nivel 3</strong></td>
            <td>Efectividad Analítica</td>
            <td>+5%</td>
            <td>Informe final de consultoría entregado con calidad profesional, superando expectativas del cliente.</td>
          </tr>
          <tr>
            <td><strong>Nivel 3</strong></td>
            <td>Diseño Curricular</td>
            <td>+3%</td>
            <td>Estructuración de casos de simulación con datos e indicadores reales de la industria.</td>
          </tr>
          <tr>
            <td><strong>Nivel 3</strong></td>
            <td>Productividad Extra</td>
            <td>+2%</td>
            <td>Ejecución de tareas anticipadas a la planificación o vinculación de nuevos proyectos.</td>
          </tr>
          <tr>
            <td><strong>Nivel 4</strong></td>
            <td>Impacto Económico</td>
            <td>+10%</td>
            <td>Cierre de acuerdos de retribución sobre utilidades generadas en las empresas asesoradas.</td>
          </tr>
          <tr>
            <td><strong>Nivel 4</strong></td>
            <td>Relaciones Públicas</td>
            <td>+3%</td>
            <td>Vinculación efectiva de profesores o conferencistas internacionales invitados.</td>
          </tr>
          <tr>
            <td><strong>Nivel 4</strong></td>
            <td>Finalización de Curso</td>
            <td>+2%</td>
            <td>Culminación satisfactoria del curso de formación de consultores con certificación superior al 80%.</td>
          </tr>
        </tbody>
      </table>

      <h2>5. Metodología de Aplicación Práctica</h2>
      <ol>
        <li><strong>Inicio de Semestre:</strong> El coordinador de línea cruza el nivel curricular con la disponibilidad horaria del estudiante y se firma el pacto POA.</li>
        <li><strong>Evaluación Quincenal:</strong> La evaluación no se hace cada semana para no saturar al equipo evaluador; se audita quincenalmente en la matriz compartida de Google Sheets.</li>
        <li><strong>Acreditación de Insignias:</strong> Cada multiplicador validado genera una insignia visible que eleva el promedio de desempeño individual.</li>
        <li><strong>Reconocimiento Institucional:</strong> Las insignias alimentan el programa de bienestar del semillero y se publican en las actas de fin de periodo.</li>
      </ol>

      <section id="simulador" style="margin-top: 48px; padding: 32px; background: var(--surface); border-radius: var(--radius);" data-ui>
        <h2 style="margin-top: 0; font-size: 1.5rem;">Simulador Interactivo de Puntos Prexia (PP)</h2>
        <p style="font-size: 15px; color: var(--muted); margin-bottom: 24px;">Calcule la meta y bonificaciones del POA según las horas pactadas y el avance de carrera.</p>
        
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 24px;">
          <div>
            <label style="display:block; font-family:var(--font-display); font-size:13px; font-weight:700; margin-bottom:6px;">NIVEL FORMATIVO</label>
            <select id="sim-nivel" style="width:100%; padding:10px 12px; font-family:inherit; font-size:14px; background:var(--bg); border:none; border-radius:var(--radius);">
              <option value="1">Nivel 1: Fundamentación (0-25%)</option>
              <option value="2">Nivel 2: Transición (26-50%)</option>
              <option value="3" selected>Nivel 3: Profesionalización (51-75%)</option>
              <option value="4">Nivel 4: Cierre y Proyección (>75%)</option>
            </select>
          </div>
          <div>
            <label style="display:block; font-family:var(--font-display); font-size:13px; font-weight:700; margin-bottom:6px;">HORAS PACTADAS SEMANALES</label>
            <input type="number" id="sim-horas" value="4" min="1" max="20" style="width:100%; padding:10px 12px; font-family:inherit; font-size:14px; background:var(--bg); border:none; border-radius:var(--radius);">
          </div>
          <div>
            <label style="display:block; font-family:var(--font-display); font-size:13px; font-weight:700; margin-bottom:6px;">SEMANA DEL SEMESTRE (1-10)</label>
            <input type="number" id="sim-semana" value="5" min="1" max="10" style="width:100%; padding:10px 12px; font-family:inherit; font-size:14px; background:var(--bg); border:none; border-radius:var(--radius);">
          </div>
        </div>

        <div style="margin-bottom: 24px;">
          <div style="font-family:var(--font-display); font-size:13px; font-weight:700; margin-bottom:8px;">MULTIPLICADORES ACTIVADOS</div>
          <div id="sim-mult-container" style="display: flex; flex-direction: column; gap: 8px;">
            <!-- Generado por JS -->
          </div>
        </div>

        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 16px; background: var(--bg); padding: 20px; border-radius: var(--radius);">
          <div>
            <span style="font-size:12px; color:var(--muted); display:block;">META BASE SEMANAL</span>
            <strong id="res-base" style="font-family:var(--font-display); font-size:1.5rem; color:var(--ink);">400 PP</strong>
          </div>
          <div>
            <span style="font-size:12px; color:var(--muted); display:block;">EXIGENCIA SEMANAL</span>
            <strong id="res-meta-semana" style="font-family:var(--font-display); font-size:1.5rem; color:var(--ink);">420 PP (105%)</strong>
          </div>
          <div>
            <span style="font-size:12px; color:var(--muted); display:block;">BONIFICACIÓN</span>
            <strong id="res-bono" style="font-family:var(--font-display); font-size:1.5rem; color:var(--mint-dark);">+0 PP</strong>
          </div>
          <div>
            <span style="font-size:12px; color:var(--muted); display:block;">PUNTOS FINALES</span>
            <strong id="res-total" style="font-family:var(--font-display); font-size:1.5rem; color:var(--ink);">400 PP</strong>
          </div>
        </div>
      </section>

      <section class="eval-photos" style="margin: 48px 0 32px;">
        <h2 style="font-size: 1.4rem; margin-bottom: 16px;">Registro Gráfico e Institucional PREXIA</h2>
        <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 16px;">
          <figure style="margin:0; background:var(--surface); padding:8px; border-radius:var(--radius);">
            <img src="{root_prefix}../assets/photos/grupo-prexia-2024.png" alt="Equipo de Consultoría y Semillero Prexia 2024" style="width:100%; aspect-ratio:16/10; object-fit:cover; border-radius:calc(var(--radius) - 2px);" loading="lazy">
            <figcaption style="font-size:13px; color:var(--muted); margin-top:8px;">Equipo de Consultoría Prexia · Facultad de Minas</figcaption>
          </figure>
          <figure style="margin:0; background:var(--surface); padding:8px; border-radius:var(--radius);">
            <img src="{root_prefix}../assets/photos/encuentro-2023-auditorio.png" alt="Encuentro Internacional de Semilleros EISI en Auditorio UNAL" style="width:100%; aspect-ratio:16/10; object-fit:cover; border-radius:calc(var(--radius) - 2px);" loading="lazy">
            <figcaption style="font-size:13px; color:var(--muted); margin-top:8px;">Auditorio Principal · Sesión de ponencias y evaluación</figcaption>
          </figure>
          <figure style="margin:0; background:var(--surface); padding:8px; border-radius:var(--radius);">
            <img src="{root_prefix}../assets/photos/semillero-equipo-completo.png" alt="Jornada de Formación y Planeación PREXIA" style="width:100%; aspect-ratio:16/10; object-fit:cover; border-radius:calc(var(--radius) - 2px);" loading="lazy">
            <figcaption style="font-size:13px; color:var(--muted); margin-top:8px;">Jornada de Concertación POA y Metas de Semestre</figcaption>
          </figure>
          <figure style="margin:0; background:var(--surface); padding:8px; border-radius:var(--radius);">
            <img src="{root_prefix}../assets/photos/jose-ignacio-maya.jpg" alt="Profesor José Ignacio Maya · Dirección Académica PREXIA" style="width:100%; aspect-ratio:16/10; object-fit:cover; border-radius:calc(var(--radius) - 2px);" loading="lazy">
            <figcaption style="font-size:13px; color:var(--muted); margin-top:8px;">Dirección Académica · Metodología de Puntos Prexia</figcaption>
          </figure>
        </div>
      </section>
    </div>
  </article>

  <aside class="sidebar">
    <div class="sidebar-box">
      <div class="sidebar-heading">HERRAMIENTAS</div>
      <div class="sidebar-nav-list">
        <a class="sidebar-nav-item" href="#simulador">Simulador Interactivo PP</a>
        <a class="sidebar-nav-item" href="{root_prefix}index.html">Catálogo de Páginas Migradas</a>
        <a class="sidebar-nav-item" href="{root_prefix}pages/unal-edu-co__prexiaforum__home__l-c3-adneas-prexia__prexia-consultor-c3-ada.html">Línea de Consultoría</a>
      </div>
    </div>
    <div class="sidebar-box">
      <div class="sidebar-heading">DATOS DEL DOCUMENTO</div>
      <p style="font-size:14px;color:var(--muted);line-height:1.5;">
        Fuente: Sistema de Evaluación Prexia Puntos y Multiplicadores(1).PDF<br>
        Facultad de Minas · UNAL Medellín<br>
        5 Páginas oficializadas
      </p>
    </div>
  </aside>
</main>

<script>
  (function() {{
    const multByLevel = {{
      1: [
        {{ label: "Excelencia en Contenido (+3%)", pct: 3 }},
        {{ label: "Generación de Valor (+3%)", pct: 3 }},
        {{ label: "Cultura Consultor (+2%)", pct: 2 }}
      ],
      2: [
        {{ label: "Tracción Web y Redes (+3%)", pct: 3 }},
        {{ label: "Poder de Convocatoria (+3%)", pct: 3 }},
        {{ label: "Celebración y Bienestar (+2%)", pct: 2 }}
      ],
      3: [
        {{ label: "Efectividad Analítica (+5%)", pct: 5 }},
        {{ label: "Diseño Curricular (+3%)", pct: 3 }},
        {{ label: "Productividad Extra (+2%)", pct: 2 }}
      ],
      4: [
        {{ label: "Impacto Económico (+10%)", pct: 10 }},
        {{ label: "Relaciones Públicas (+3%)", pct: 3 }},
        {{ label: "Finalización de Curso (+2%)", pct: 2 }}
      ]
    }};

    const nivelSelect = document.getElementById('sim-nivel');
    const horasInput = document.getElementById('sim-horas');
    const semanaInput = document.getElementById('sim-semana');
    const multContainer = document.getElementById('sim-mult-container');
    const resBase = document.getElementById('res-base');
    const resMetaSemana = document.getElementById('res-meta-semana');
    const resBono = document.getElementById('res-bono');
    const resTotal = document.getElementById('res-total');

    function renderCheckboxes() {{
      const level = nivelSelect.value;
      const mults = multByLevel[level] || [];
      multContainer.innerHTML = mults.map(m => `
        <label style="display:flex; align-items:center; gap:8px; font-size:14px; cursor:pointer;">
          <input type="checkbox" class="sim-check" data-pct="${{m.pct}}" style="accent-color:var(--ink);">
          <span>${{m.label}}</span>
        </label>
      `).join('');
      attachListeners();
      recalc();
    }}

    function attachListeners() {{
      multContainer.querySelectorAll('.sim-check').forEach(chk => {{
        chk.addEventListener('change', recalc);
      }});
    }}

    function recalc() {{
      const horas = Math.max(1, parseInt(horasInput.value || 4, 10));
      const semana = Math.min(10, Math.max(1, parseInt(semanaInput.value || 5, 10)));
      const base = horas * 100;
      const semanaFactor = 1.0 + ((semana - 1) * 0.01);
      const metaSemana = Math.round(base * semanaFactor);

      let bonusPct = 0;
      multContainer.querySelectorAll('.sim-check:checked').forEach(chk => {{
        bonusPct += parseFloat(chk.getAttribute('data-pct') || 0);
      }});

      const bonusPP = Math.round(base * (bonusPct / 100));
      const finalPP = base + bonusPP;

      resBase.textContent = base + ' PP';
      resMetaSemana.textContent = `${{metaSemana}} PP (${{Math.round(semanaFactor * 100)}}%)`;
      resBono.textContent = `+${{bonusPP}} PP (${{bonusPct}}%)`;
      resTotal.textContent = `${{finalPP}} PP`;
      resTotal.style.color = finalPP >= metaSemana ? 'var(--mint-dark)' : 'var(--ink)';
    }}

    nivelSelect.addEventListener('change', renderCheckboxes);
    horasInput.addEventListener('input', recalc);
    semanaInput.addEventListener('input', recalc);

    renderCheckboxes();
  }})();
</script>
"""


def build_site() -> None:
    manifest = load_manifest()
    if OUTPUT_DIR.exists():
        shutil.rmtree(OUTPUT_DIR)
    (OUTPUT_DIR / "pages").mkdir(parents=True)
    (OUTPUT_DIR / "images").mkdir(parents=True)
    (OUTPUT_DIR / "assets").mkdir(parents=True)
    shutil.copytree(SOURCE_DIR / "images", OUTPUT_DIR / "images", dirs_exist_ok=True)
    if (PROJECT_ROOT / "assets").exists():
        shutil.copytree(PROJECT_ROOT / "assets", OUTPUT_DIR / "assets", dirs_exist_ok=True)
    shutil.copy2(SOURCE_DIR / "manifest.json", OUTPUT_DIR / "manifest.json")
    (OUTPUT_DIR / "assets" / "styles.css").write_text(CSS.strip() + "\n", encoding="utf-8")

    pages = manifest["pages"]
    page_by_url = {page["url"]: page for page in pages}
    page_by_slug = {page["slug"]: page for page in pages}
    children_by_url: dict[str, list[dict]] = defaultdict(list)
    group_buckets: dict[str, list[dict]] = defaultdict(list)

    parsed_content: dict[str, tuple[list[str], list[str]]] = {}
    for page in pages:
        markdown_path = SOURCE_DIR / page["markdown"]
        lines, images = parse_markdown(markdown_path)
        parsed_content[page["slug"]] = (normalize_text_lines(lines), images)

    for page in pages:
        path_parts = [part for part in urlparse(page["url"]).path.split("/") if part]
        top_group = path_parts[3] if len(path_parts) > 3 else "home"
        group_buckets[top_group].append(page)
        for parent_url, parent in page_by_url.items():
            if parent_url == page["url"]:
                continue
            if page["url"].startswith(parent_url + "/"):
                children_by_url[parent_url].append(page)

    for parent_url, items in children_by_url.items():
        children_by_url[parent_url] = sorted(items, key=lambda item: item["url"].count("/"))

    def nearest_parent_url(url: str) -> str | None:
        candidates = []
        for candidate in page_by_url:
            if candidate == url:
                continue
            if url.startswith(candidate + "/"):
                candidates.append(candidate)
        if not candidates:
            return None
        return max(candidates, key=len)

    def layout(title: str, body: str, root_prefix: str = "") -> str:
        nav = f"""
<header class="topbar">
  <div class="shell topbar-inner">
    <a class="brand" href="{root_prefix}index.html">
      PREXIA
      <span class="brand-sub">Facultad de Minas · UNAL</span>
    </a>
    <nav class="nav-links">
      <a href="{root_prefix}../index.html">Portada Principal</a>
      <a href="{root_prefix}pages/sistema-evaluacion-prexia.html">Sistema de Evaluación (PP)</a>
      <a href="{root_prefix}index.html#colecciones">Colecciones</a>
      <a href="{root_prefix}index.html#paginas">Directorio</a>
    </nav>
    <a href="{root_prefix}../index.html#contacto" class="nav-action">Solicitar consultoría</a>
  </div>
</header>
"""
        footer = f"""
<footer class="site-footer">
  <div class="shell footer-inner">
    <div class="footer-info">
      <h4>PREXIA · UNAL MINAS</h4>
      <p>Semillero de Investigación adscrito al Área Curricular de Ingeniería Industrial y Administrativa de la Facultad de Minas, Universidad Nacional de Colombia Sede Medellín.</p>
    </div>
    <div class="footer-links-row">
      <a href="{root_prefix}../index.html">Inicio</a>
      <a href="{root_prefix}pages/sistema-evaluacion-prexia.html">Evaluación PP</a>
      <a href="{root_prefix}manifest.json">Manifest</a>
      <a href="https://sites.google.com/unal.edu.co/prexiaforum" target="_blank" rel="noreferrer">Google Sites Original</a>
    </div>
  </div>
</footer>
"""
        return f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(title)} · PREXIA UNAL</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Libre+Franklin:wght@500;700;800&family=Source+Serif+4:ital,wght@0,400;0,600;1,400;1,600&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="{root_prefix}assets/styles.css">
</head>
<body>
{nav}
{body}
{footer}
<script>
  if (typeof IntersectionObserver !== 'undefined') {{
    const observer = new IntersectionObserver((entries) => {{
      entries.forEach(entry => {{
        if (entry.isIntersecting) {{
          entry.target.classList.add('is-visible');
        }}
      }});
    }}, {{ threshold: 0.05 }});
    document.querySelectorAll('.page-copy > *, .prexia-table tbody tr, .sidebar-box, .gallery-thumb, .card, .stat-unit, .eval-photos figure, .eval-hero-actions a').forEach((el, i) => {{
      el.classList.add('reveal-item');
      el.style.transitionDelay = `${{(i % 6) * 35}}ms`;
      observer.observe(el);
    }});
  }}
</script>
</body>
</html>
"""

    # Build the dedicated evaluation page
    eval_page_html = layout("Sistema de Evaluación Prexia (Puntos y Multiplicadores)", build_evaluation_page("../"), root_prefix="../")
    (OUTPUT_DIR / "pages" / "sistema-evaluacion-prexia.html").write_text(eval_page_html, encoding="utf-8")

    # Build catalog home page
    home_page = page_by_slug["unal-edu-co__prexiaforum__home"]
    home_lines, _ = parsed_content[home_page["slug"]]
    lead = " ".join(home_lines[:4]).strip()
    collection_cards = []
    for group, items in sorted(group_buckets.items(), key=lambda entry: entry[0]):
        label = "Inicio" if group == "home" else title_case_from_segment(group)
        anchor_page = sorted(items, key=lambda item: item["url"].count("/"))[0]
        card_image = parsed_content[anchor_page["slug"]][1][:1]
        cover = ""
        if card_image:
            cover = f'<div class="card-cover"><img src="{html.escape(card_image[0])}" alt="{html.escape(anchor_page["title"])}"></div>'
        collection_cards.append(
            f"""
<article class="card span-4">
  {cover}
  <div>
    <div class="card-meta-tag">{len(items)} páginas · {html.escape(label)}</div>
    <h3 class="card-title"><a href="{html.escape(page_href(anchor_page["slug"]))}">{html.escape(anchor_page["title"])}</a></h3>
    <p class="card-excerpt">{html.escape(parsed_content[anchor_page["slug"]][0][0] if parsed_content[anchor_page["slug"]][0] else "Contenido migrado desde Google Sites.")}</p>
  </div>
  <a class="btn-card" href="{html.escape(page_href(anchor_page["slug"]))}">Consultar sección</a>
</article>
"""
        )

    page_cards = []
    for page in sorted(pages, key=lambda item: (item["url"].count("/"), item["title"])):
        lines, images = parsed_content[page["slug"]]
        excerpt = " ".join(lines[:3]) or "Contenido migrado desde Google Sites."
        cover = f'<div class="card-cover"><img src="{html.escape(images[0])}" alt="{html.escape(page["title"])}"></div>' if images else ""
        path_parts = [part for part in urlparse(page["url"]).path.split("/") if part]
        label = " / ".join(title_case_from_segment(part) for part in path_parts[3:5]) or "Inicio"
        page_cards.append(
            f"""
<article class="card span-6">
  {cover}
  <div>
    <div class="card-meta-tag">{html.escape(label)}</div>
    <h3 class="card-title"><a href="{html.escape(page_href(page["slug"]))}">{html.escape(page["title"])}</a></h3>
    <p class="card-excerpt">{html.escape(excerpt[:240])}</p>
  </div>
  <a class="btn-card" href="{html.escape(page_href(page["slug"]))}">Abrir página</a>
</article>
"""
        )

    home_body = f"""
<main class="shell">
  <section class="archive-hero">
    <div style="max-width: 840px; margin-bottom: 32px;">
      <h1 class="archive-hero-title">Archivo PREXIA</h1>
      <p class="archive-lead">{html.escape(lead)}</p>
    </div>
    <div class="archive-stats-box" style="margin-bottom: 32px;">
      <div class="stat-unit">
        <strong>{manifest['page_count']}</strong>
        <span>Páginas migradas</span>
      </div>
      <div class="stat-unit">
        <strong>{manifest['image_count']}</strong>
        <span>Imágenes locales</span>
      </div>
      <div class="stat-unit">
        <strong>{len(group_buckets)}</strong>
        <span>Colecciones temáticas</span>
      </div>
      <div class="stat-unit">
        <strong>100%</strong>
        <span>Disponibilidad estática</span>
      </div>
    </div>
    <div style="display:flex;gap:16px;flex-wrap:wrap;margin-bottom:56px;">
      <a href="pages/sistema-evaluacion-prexia.html" style="display:inline-flex;align-items:center;height:46px;padding:0 24px;background:var(--ink);color:var(--bg);font-family:var(--font-display);font-size:15px;font-weight:700;border-radius:var(--radius);text-decoration:none;">Sistema de Evaluación (PP)</a>
      <a href="../index.html" style="display:inline-flex;align-items:center;height:46px;padding:0 24px;background:var(--surface);color:var(--ink);font-family:var(--font-display);font-size:15px;font-weight:700;border-radius:var(--radius);text-decoration:none;">Volver a Portada</a>
    </div>
  </section>

  <!-- DESTACADO: SISTEMA DE EVALUACIÓN (PDF) -->
  <section class="section" style="background:var(--surface);padding:40px;border-radius:var(--radius);margin-bottom:48px;">
    <div style="display:grid;grid-template-columns:minmax(0,60%) 1fr;gap:var(--gutter);align-items:center;">
      <div>
        <h2 style="font-family:var(--font-display);font-size:clamp(1.4rem, 2.4vw, 2rem);font-weight:800;color:var(--ink);margin-bottom:12px;">Evaluación PP</h2>
        <p style="font-size:16px;color:var(--ink);line-height:1.6;margin-bottom:20px;">
          Manual oficial de operaciones, medición por Puntos Prexia (PP), matriz de multiplicadores de calidad y curva progresiva del 110% en Facultad de Minas.
        </p>
        <a href="pages/sistema-evaluacion-prexia.html" class="nav-action" style="font-size:15px;">Ver documentación completa y tablas oficiales →</a>
      </div>
      <div style="text-align:right;">
        <a href="pages/sistema-evaluacion-prexia.html#simulador" style="display:inline-block;padding:14px 28px;background:var(--ink);color:var(--bg);font-family:var(--font-display);font-weight:700;border-radius:var(--radius);">Probar Simulador Interactivo</a>
      </div>
    </div>
  </section>

  <section class="section" id="colecciones">
    <div class="section-header">
      <h2 class="section-title">Colecciones principales</h2>
      <p class="section-desc">Secciones estructurales que organizan las cuatro líneas de trabajo y las seis ediciones de los Encuentros Internacionales EISI.</p>
    </div>
    <div class="grid-cards">
      {''.join(collection_cards)}
    </div>
  </section>

  <section class="section" id="paginas">
    <div class="section-header">
      <h2 class="section-title">Inventario completo</h2>
      <p class="section-desc">Listado detallado de todas las páginas migradas desde Google Sites con su contenido íntegro y recursos gráficos vinculados.</p>
    </div>
    <div class="grid-cards">
      {''.join(page_cards)}
    </div>
  </section>
</main>
"""
    (OUTPUT_DIR / "index.html").write_text(layout("Directorio Migrado", home_body), encoding="utf-8")

    # Build individual subpages
    for page in pages:
        lines, images = parsed_content[page["slug"]]
        parent_url = nearest_parent_url(page["url"])
        parent = page_by_url[parent_url] if parent_url else None
        siblings = []
        if parent:
            for candidate in children_by_url.get(parent["url"], []):
                candidate_parent = nearest_parent_url(candidate["url"])
                if candidate_parent == parent["url"]:
                    siblings.append(candidate)
        else:
            siblings = [candidate for candidate in pages if nearest_parent_url(candidate["url"]) is None]

        breadcrumbs = ['<span><a href="../index.html">Directorio</a></span>']
        if parent:
            lineage = []
            current = parent
            while current:
                lineage.append(current)
                candidate_parent = nearest_parent_url(current["url"])
                current = page_by_url[candidate_parent] if candidate_parent else None
            for item in reversed(lineage):
                breadcrumbs.append(f'<span><a href="{html.escape(page_output_name(item["slug"]))}">{html.escape(item["title"])}</a></span>')
        breadcrumbs.append(f"<span>{html.escape(page['title'])}</span>")

        content_blocks = []
        for line in lines:
            if len(line) < 48 and not line.endswith(".") and not line.endswith(":"):
                content_blocks.append(f'<h3 class="editorial-subhead">{html.escape(line)}</h3>')
            else:
                content_blocks.append(f"<p>{html.escape(line)}</p>")

        gallery = ""
        if images:
            gallery_items = "".join(
                f'<a class="gallery-thumb" href="../{html.escape(image)}" target="_blank" rel="noreferrer"><img src="../{html.escape(image)}" alt="{html.escape(page["title"])}" loading="lazy"></a>'
                for image in images
            )
            gallery = f"""
<section class="gallery-section">
  <h3 class="section-title" style="font-size:1.4rem;">Fotografías y recursos ({len(images)})</h3>
  <div class="gallery-grid">{gallery_items}</div>
</section>
"""

        child_links = []
        for child in children_by_url.get(page["url"], []):
            if nearest_parent_url(child["url"]) == page["url"]:
                child_links.append(
                    f'<a class="sidebar-nav-item" href="{html.escape(page_output_name(child["slug"]))}">{html.escape(child["title"])}</a>'
                )

        sibling_links = []
        for sibling in siblings:
            active_class = " active" if sibling["slug"] == page["slug"] else ""
            sibling_links.append(
                f'<a class="sidebar-nav-item{active_class}" href="{html.escape(page_output_name(sibling["slug"]))}">{html.escape(sibling["title"])}</a>'
            )

        page_body = f"""
<main class="shell page-layout">
  <article class="page-article">
    <h1 class="page-title">{html.escape(page['title'])}</h1>
    <nav class="breadcrumb-trail" aria-label="Ruta de navegación">{''.join(breadcrumbs)}</nav>
    <p class="meta-original">Fuente original migrada: <a href="{html.escape(page['url'])}" target="_blank" rel="noreferrer">{html.escape(page['url'])}</a></p>
    <div class="page-copy">
      {''.join(content_blocks)}
    </div>
    {gallery}
  </article>
  <aside class="sidebar">
    <div class="sidebar-box">
      <div class="sidebar-heading">EN ESTA SECCIÓN</div>
      <div class="sidebar-nav-list">{''.join(child_links) if child_links else '<span style="font-size:14px;color:var(--muted);">No hay subpáginas directas.</span>'}</div>
    </div>
    <div class="sidebar-box">
      <div class="sidebar-heading">PÁGINAS RELACIONADAS</div>
      <div class="sidebar-nav-list">{''.join(sibling_links) if sibling_links else '<span style="font-size:14px;color:var(--muted);">Sin páginas hermanas.</span>'}</div>
    </div>
    <div class="sidebar-box">
      <div class="sidebar-heading">METRICAS</div>
      <p style="font-size:14px;color:var(--muted);line-height:1.5;">
        {len(lines)} bloques de contenido textual<br>
        {len(images)} imágenes locales indexadas
      </p>
    </div>
  </aside>
</main>
"""
        (OUTPUT_DIR / "pages" / page_output_name(page["slug"])).write_text(
            layout(page["title"], page_body, root_prefix="../"),
            encoding="utf-8",
        )


if __name__ == "__main__":
    build_site()
    print("Static site generated successfully.")
