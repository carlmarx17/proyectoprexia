#!/usr/bin/env python3
from __future__ import annotations

import html
import json
import shutil
from collections import defaultdict
from pathlib import Path
from urllib.parse import unquote, urlparse


SOURCE_DIR = Path("scraped_site_clean")
OUTPUT_DIR = Path("site")

CSS = """
:root {
  --bg: #f4efe4;
  --panel: rgba(255, 252, 245, 0.82);
  --panel-strong: #fffaf1;
  --ink: #163126;
  --muted: #5a6d62;
  --accent: #1f6b52;
  --accent-2: #c46c2f;
  --line: rgba(22, 49, 38, 0.12);
  --shadow: 0 24px 80px rgba(18, 43, 33, 0.12);
}

* { box-sizing: border-box; }
html { scroll-behavior: smooth; }
body {
  margin: 0;
  font-family: "Source Serif 4", Georgia, serif;
  color: var(--ink);
  background:
    radial-gradient(circle at top left, rgba(196,108,47,0.18), transparent 28%),
    radial-gradient(circle at top right, rgba(31,107,82,0.18), transparent 26%),
    linear-gradient(180deg, #f7f1e7 0%, #f2ebde 55%, #efe6d8 100%);
  min-height: 100vh;
}

a { color: inherit; text-decoration: none; }
img { display: block; max-width: 100%; }

.shell {
  width: min(1180px, calc(100% - 32px));
  margin: 0 auto;
}

.topbar {
  position: sticky;
  top: 0;
  z-index: 20;
  backdrop-filter: blur(16px);
  background: rgba(244, 239, 228, 0.78);
  border-bottom: 1px solid var(--line);
}

.topbar-inner {
  display: flex;
  gap: 18px;
  align-items: center;
  justify-content: space-between;
  padding: 14px 0;
}

.brand {
  display: inline-flex;
  gap: 12px;
  align-items: center;
  font-family: "Alegreya Sans", sans-serif;
  font-weight: 700;
  letter-spacing: 0.04em;
  text-transform: uppercase;
}

.brand-mark {
  width: 14px;
  height: 14px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--accent), var(--accent-2));
  box-shadow: 0 0 0 7px rgba(31, 107, 82, 0.08);
}

.nav-links {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.nav-links a,
.button {
  padding: 10px 14px;
  border-radius: 999px;
  border: 1px solid var(--line);
  background: rgba(255, 255, 255, 0.55);
  font-family: "Alegreya Sans", sans-serif;
  font-size: 0.95rem;
}

.button.primary {
  background: linear-gradient(135deg, var(--accent), #2a8767);
  color: #fff;
  border-color: transparent;
}

.hero {
  padding: 52px 0 32px;
}

.hero-grid {
  display: grid;
  grid-template-columns: minmax(0, 1.2fr) minmax(280px, 0.8fr);
  gap: 24px;
  align-items: stretch;
}

.hero-panel,
.card,
.page-panel,
.gallery,
.sidebar-card {
  background: var(--panel);
  border: 1px solid rgba(255,255,255,0.6);
  border-radius: 28px;
  box-shadow: var(--shadow);
}

.hero-panel {
  padding: 36px;
}

.eyebrow {
  margin: 0 0 12px;
  color: var(--accent);
  font-family: "Alegreya Sans", sans-serif;
  font-weight: 800;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}

h1, h2, h3 {
  margin: 0;
  line-height: 1.05;
  font-weight: 700;
}

h1 { font-size: clamp(2.6rem, 6vw, 5.4rem); }
h2 { font-size: clamp(1.7rem, 3vw, 2.5rem); }
h3 { font-size: 1.25rem; }

.lead {
  margin: 18px 0 0;
  max-width: 58ch;
  color: var(--muted);
  font-size: 1.08rem;
  line-height: 1.7;
}

.stats {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 16px;
  padding: 24px;
}

.stat {
  padding: 22px;
  border-radius: 22px;
  background: linear-gradient(180deg, rgba(255,255,255,0.74), rgba(255,255,255,0.46));
  border: 1px solid var(--line);
}

.stat strong {
  display: block;
  font-size: 2rem;
  font-family: "Alegreya Sans", sans-serif;
}

.section {
  padding: 18px 0 28px;
}

.section-header {
  display: flex;
  align-items: end;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 18px;
}

.section-header p {
  margin: 0;
  color: var(--muted);
  max-width: 55ch;
}

.grid {
  display: grid;
  grid-template-columns: repeat(12, minmax(0, 1fr));
  gap: 18px;
}

.card {
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.card.span-4 { grid-column: span 4; }
.card.span-6 { grid-column: span 6; }
.card.span-8 { grid-column: span 8; }
.card.span-12 { grid-column: span 12; }

.chip-row {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.chip {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 7px 11px;
  border-radius: 999px;
  background: rgba(31, 107, 82, 0.08);
  color: var(--accent);
  font-family: "Alegreya Sans", sans-serif;
  font-size: 0.9rem;
}

.card p,
.page-copy p,
.meta,
.sidebar-card p,
.footer {
  color: var(--muted);
  line-height: 1.7;
}

.cover {
  aspect-ratio: 16 / 10;
  border-radius: 20px;
  overflow: hidden;
  background: linear-gradient(135deg, rgba(31,107,82,0.16), rgba(196,108,47,0.16));
}

.cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.page-layout {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 320px;
  gap: 24px;
  padding: 34px 0 56px;
}

.page-panel {
  padding: 34px;
}

.breadcrumb {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-bottom: 18px;
  font-family: "Alegreya Sans", sans-serif;
  color: var(--muted);
}

.breadcrumb span::after {
  content: "/";
  margin-left: 10px;
  color: rgba(22, 49, 38, 0.28);
}

.breadcrumb span:last-child::after { display: none; }

.page-copy {
  margin-top: 28px;
  display: grid;
  gap: 14px;
}

.page-copy .kicker {
  font-family: "Alegreya Sans", sans-serif;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.12em;
  color: var(--accent);
  margin-top: 8px;
}

.gallery {
  padding: 24px;
  margin-top: 28px;
}

.gallery-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
}

.gallery-grid a {
  display: block;
  border-radius: 18px;
  overflow: hidden;
  aspect-ratio: 1 / 1;
  background: #e6dfd0;
}

.gallery-grid img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.sidebar {
  display: grid;
  gap: 16px;
  align-content: start;
}

.sidebar-card {
  padding: 22px;
}

.sidebar-list {
  display: grid;
  gap: 10px;
  margin-top: 14px;
}

.sidebar-link {
  padding: 12px 14px;
  border-radius: 16px;
  border: 1px solid var(--line);
  background: rgba(255,255,255,0.5);
}

.sidebar-link.active {
  background: rgba(31, 107, 82, 0.1);
  color: var(--accent);
}

.footer {
  padding: 18px 0 44px;
  font-size: 0.95rem;
}

@media (max-width: 980px) {
  .hero-grid,
  .page-layout {
    grid-template-columns: 1fr;
  }

  .card.span-4,
  .card.span-6,
  .card.span-8,
  .card.span-12 {
    grid-column: span 12;
  }
}

@media (max-width: 720px) {
  .shell { width: min(100% - 20px, 1180px); }
  .topbar-inner,
  .section-header { align-items: start; flex-direction: column; }
  .hero-panel,
  .page-panel,
  .gallery,
  .card,
  .sidebar-card { padding: 22px; border-radius: 22px; }
  .stats { grid-template-columns: 1fr 1fr; padding: 0; }
  .gallery-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
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


def build_site() -> None:
    manifest = load_manifest()
    if OUTPUT_DIR.exists():
        shutil.rmtree(OUTPUT_DIR)
    (OUTPUT_DIR / "pages").mkdir(parents=True)
    (OUTPUT_DIR / "images").mkdir(parents=True)
    (OUTPUT_DIR / "assets").mkdir(parents=True)
    shutil.copytree(SOURCE_DIR / "images", OUTPUT_DIR / "images", dirs_exist_ok=True)
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
        nav = """
<div class="topbar">
  <div class="shell topbar-inner">
    <a class="brand" href="{root}index.html">
      <span class="brand-mark"></span>
      <span>Semillero Prexia</span>
    </a>
    <div class="nav-links">
      <a href="{root}index.html#colecciones">Colecciones</a>
      <a href="{root}index.html#paginas">Paginas</a>
      <a href="{root}manifest.json">Manifest</a>
    </div>
  </div>
</div>
""".format(root=root_prefix)
        return f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(title)}</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Alegreya+Sans:wght@400;500;700;800&family=Source+Serif+4:wght@400;600;700&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="{root_prefix}assets/styles.css">
</head>
<body>
{nav}
{body}
</body>
</html>
"""

    home_page = page_by_slug["unal-edu-co__prexiaforum__home"]
    home_lines, _ = parsed_content[home_page["slug"]]
    lead = " ".join(home_lines[:5]).strip()
    collection_cards = []
    for group, items in sorted(group_buckets.items(), key=lambda entry: entry[0]):
        label = "Inicio" if group == "home" else title_case_from_segment(group)
        anchor_page = sorted(items, key=lambda item: item["url"].count("/"))[0]
        card_image = parsed_content[anchor_page["slug"]][1][:1]
        cover = ""
        if card_image:
            cover = f'<div class="cover"><img src="{html.escape(card_image[0])}" alt="{html.escape(anchor_page["title"])}"></div>'
        collection_cards.append(
            f"""
<article class="card span-4">
  {cover}
  <div class="chip-row">
    <span class="chip">{len(items)} paginas</span>
    <span class="chip">{label}</span>
  </div>
  <h3><a href="{html.escape(page_href(anchor_page["slug"]))}">{html.escape(anchor_page["title"])}</a></h3>
  <p>{html.escape(parsed_content[anchor_page["slug"]][0][0] if parsed_content[anchor_page["slug"]][0] else "Contenido migrado desde Google Sites.")}</p>
  <a class="button" href="{html.escape(page_href(anchor_page["slug"]))}">Entrar</a>
</article>
"""
        )

    page_cards = []
    for page in sorted(pages, key=lambda item: (item["url"].count("/"), item["title"])):
        lines, images = parsed_content[page["slug"]]
        excerpt = " ".join(lines[:3]) or "Contenido migrado desde Google Sites."
        cover = f'<div class="cover"><img src="{html.escape(images[0])}" alt="{html.escape(page["title"])}"></div>' if images else ""
        path_parts = [part for part in urlparse(page["url"]).path.split("/") if part]
        label = " / ".join(title_case_from_segment(part) for part in path_parts[3:5]) or "Inicio"
        page_cards.append(
            f"""
<article class="card span-6">
  {cover}
  <div class="chip-row"><span class="chip">{html.escape(label)}</span></div>
  <h3><a href="{html.escape(page_href(page["slug"]))}">{html.escape(page["title"])}</a></h3>
  <p>{html.escape(excerpt[:240])}</p>
  <a class="button" href="{html.escape(page_href(page["slug"]))}">Ver pagina</a>
</article>
"""
        )

    home_body = f"""
<main class="shell">
  <section class="hero">
    <div class="hero-grid">
      <div class="hero-panel">
        <p class="eyebrow">Archivo Migrado</p>
        <h1>Semillero Prexia en HTML.</h1>
        <p class="lead">{html.escape(lead)}</p>
        <div class="chip-row" style="margin-top:24px">
          <a class="button primary" href="#paginas">Explorar paginas</a>
          <a class="button" href="{html.escape(home_page['url'])}" target="_blank" rel="noreferrer">Ver fuente original</a>
        </div>
      </div>
      <div class="stats">
        <div class="stat"><strong>{manifest['page_count']}</strong><span>paginas migradas</span></div>
        <div class="stat"><strong>{manifest['image_count']}</strong><span>imagenes locales</span></div>
        <div class="stat"><strong>{len(group_buckets)}</strong><span>colecciones principales</span></div>
        <div class="stat"><strong>{manifest.get('error_count', 0)}</strong><span>enlaces rotos detectados</span></div>
      </div>
    </div>
  </section>
  <section class="section" id="colecciones">
    <div class="section-header">
      <div>
        <p class="eyebrow">Colecciones</p>
        <h2>Secciones principales del sitio</h2>
      </div>
      <p>La migracion conserva lineas de investigacion, encuentros internacionales y convocatorias del evento.</p>
    </div>
    <div class="grid">
      {''.join(collection_cards)}
    </div>
  </section>
  <section class="section" id="paginas">
    <div class="section-header">
      <div>
        <p class="eyebrow">Inventario</p>
        <h2>Todas las paginas disponibles</h2>
      </div>
      <p>Cada entrada incluye su texto extraido, imagenes locales y enlace a la URL original en Google Sites.</p>
    </div>
    <div class="grid">
      {''.join(page_cards)}
    </div>
  </section>
  <div class="footer">Sitio estatico generado desde <code>scraped_site_clean/manifest.json</code>.</div>
</main>
"""
    (OUTPUT_DIR / "index.html").write_text(layout("Semillero Prexia", home_body), encoding="utf-8")

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

        breadcrumbs = ['<span><a href="../index.html">Inicio</a></span>']
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
            if len(line) < 42 and not line.endswith(".") and not line.endswith(":"):
                content_blocks.append(f'<div class="kicker">{html.escape(line)}</div>')
            else:
                content_blocks.append(f"<p>{html.escape(line)}</p>")

        gallery = ""
        if images:
            gallery_items = "".join(
                f'<a href="../{html.escape(image)}" target="_blank" rel="noreferrer"><img src="../{html.escape(image)}" alt="{html.escape(page["title"])}"></a>'
                for image in images
            )
            gallery = f"""
<section class="gallery">
  <div class="section-header">
    <div>
      <p class="eyebrow">Galeria</p>
      <h2>Imagenes de esta pagina</h2>
    </div>
  </div>
  <div class="gallery-grid">{gallery_items}</div>
</section>
"""

        child_links = []
        for child in children_by_url.get(page["url"], []):
            if nearest_parent_url(child["url"]) == page["url"]:
                child_links.append(
                    f'<a class="sidebar-link" href="{html.escape(page_output_name(child["slug"]))}">{html.escape(child["title"])}</a>'
                )

        sibling_links = []
        for sibling in siblings:
            css_class = "sidebar-link active" if sibling["slug"] == page["slug"] else "sidebar-link"
            sibling_links.append(
                f'<a class="{css_class}" href="{html.escape(page_output_name(sibling["slug"]))}">{html.escape(sibling["title"])}</a>'
            )

        page_body = f"""
<main class="shell page-layout">
  <article class="page-panel">
    <div class="breadcrumb">{''.join(breadcrumbs)}</div>
    <p class="eyebrow">Pagina Migrada</p>
    <h1>{html.escape(page['title'])}</h1>
    <p class="meta">URL original: <a href="{html.escape(page['url'])}" target="_blank" rel="noreferrer">{html.escape(page['url'])}</a></p>
    <div class="page-copy">
      {''.join(content_blocks)}
    </div>
    {gallery}
  </article>
  <aside class="sidebar">
    <section class="sidebar-card">
      <p class="eyebrow">Contexto</p>
      <h3>Navegacion relacionada</h3>
      <div class="sidebar-list">{''.join(sibling_links) if sibling_links else '<p>Sin paginas relacionadas.</p>'}</div>
    </section>
    <section class="sidebar-card">
      <p class="eyebrow">Subpaginas</p>
      <h3>Descender en la seccion</h3>
      <div class="sidebar-list">{''.join(child_links) if child_links else '<p>No hay subpaginas directas para esta entrada.</p>'}</div>
    </section>
    <section class="sidebar-card">
      <p class="eyebrow">Datos</p>
      <p>{len(lines)} bloques de texto</p>
      <p>{len(images)} imagenes locales</p>
    </section>
  </aside>
</main>
"""
        (OUTPUT_DIR / "pages" / page_output_name(page["slug"])).write_text(
            layout(page["title"], page_body, root_prefix="../"),
            encoding="utf-8",
        )


if __name__ == "__main__":
    build_site()
