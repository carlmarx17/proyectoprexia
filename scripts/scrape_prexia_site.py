#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import re
import sys
import unicodedata
from collections import deque
from pathlib import Path
from typing import Iterable
from urllib.parse import quote, urljoin, urlparse, urlunparse
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from bs4 import BeautifulSoup


BASE_URL = "https://sites.google.com/unal.edu.co/prexiaforum/home"
SITE_PREFIX = "https://sites.google.com/unal.edu.co/prexiaforum/"
OUTPUT_DIR = Path("scraped_site")
USER_AGENT = "Mozilla/5.0 (compatible; PrexiaSiteScraper/1.0)"


def fetch(url: str) -> bytes:
    request = Request(url, headers={"User-Agent": USER_AGENT})
    with urlopen(request, timeout=30) as response:
        return response.read()


def normalize_url(url: str) -> str:
    parsed = urlparse(url)
    cleaned = parsed._replace(
        path=quote(parsed.path, safe="/%"),
        fragment="",
        query="",
    )
    return urlunparse(cleaned)


def absolute_site_url(href: str, current_url: str) -> str | None:
    joined = normalize_url(urljoin(current_url, href))
    if not joined.startswith(SITE_PREFIX):
        return None
    return joined


def slugify(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value)
    ascii_value = normalized.encode("ascii", "ignore").decode("ascii")
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", ascii_value).strip("-").lower()
    return slug or "page"


def page_slug(url: str) -> str:
    path = urlparse(url).path.strip("/")
    parts = [slugify(part) for part in path.split("/") if part]
    return "__".join(parts) or "home"


def unique_lines(lines: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for line in lines:
        cleaned = " ".join(line.split())
        if not cleaned or cleaned in seen:
            continue
        seen.add(cleaned)
        result.append(cleaned)
    return result


def extract_text(soup: BeautifulSoup) -> list[str]:
    sections = soup.select("section.yaqOZd")
    raw_lines: list[str] = []
    for section in sections:
        text = section.get_text("\n", strip=True)
        if not text:
            continue
        raw_lines.extend(part.strip() for part in text.splitlines())

    filtered = []
    skip_exact = {
        "Search this site",
        "Skip to main content",
        "Skip to navigation",
        "Report abuse",
        "Page details",
        "Page updated",
    }
    for line in unique_lines(raw_lines):
        if line in skip_exact:
            continue
        if line.startswith("Image:"):
            continue
        filtered.append(line)
    return filtered


def extract_images(soup: BeautifulSoup) -> list[dict[str, str]]:
    images: list[dict[str, str]] = []
    seen: set[str] = set()
    for img in soup.find_all("img", src=True):
        src = img["src"].strip()
        if "googleusercontent.com" not in src:
            continue
        src = normalize_url(src)
        if src in seen:
            continue
        seen.add(src)
        alt = " ".join(img.get("alt", "").split())
        images.append({"src": src, "alt": alt})
    return images


def extract_links(soup: BeautifulSoup, current_url: str) -> list[str]:
    links: list[str] = []
    seen: set[str] = set()
    for anchor in soup.find_all("a", href=True):
        link = absolute_site_url(anchor["href"], current_url)
        if not link or link in seen:
            continue
        seen.add(link)
        links.append(link)
    return links


def page_title(soup: BeautifulSoup, fallback_url: str) -> str:
    meta = soup.find("meta", attrs={"property": "og:title"})
    if meta and meta.get("content"):
        return " ".join(meta["content"].split())
    heading = soup.find(["h1", "h2"])
    if heading:
        return " ".join(heading.get_text(" ", strip=True).split())
    return page_slug(fallback_url)


def save_markdown(
    output_dir: Path,
    url: str,
    title: str,
    text_lines: list[str],
    image_files: list[dict[str, str]],
) -> str:
    slug = page_slug(url)
    markdown_path = output_dir / "pages" / f"{slug}.md"
    markdown_path.parent.mkdir(parents=True, exist_ok=True)

    body: list[str] = [f"# {title}", "", f"URL original: {url}", ""]
    if text_lines:
        body.append("## Texto extraido")
        body.append("")
        body.extend(text_lines)
        body.append("")
    if image_files:
        body.append("## Imagenes")
        body.append("")
        for image in image_files:
            alt = f" ({image['alt']})" if image["alt"] else ""
            body.append(f"- {image['path']}{alt}")
        body.append("")

    markdown_path.write_text("\n".join(body).rstrip() + "\n", encoding="utf-8")
    return str(markdown_path.relative_to(output_dir))


def download_image(output_dir: Path, page_slug_value: str, image: dict[str, str], index: int) -> dict[str, str]:
    src = image["src"]
    digest = hashlib.sha1(src.encode("utf-8")).hexdigest()[:12]
    image_name = f"{page_slug_value}__{index:02d}__{digest}.jpg"
    relative_path = Path("images") / image_name
    destination = output_dir / relative_path
    destination.parent.mkdir(parents=True, exist_ok=True)
    record = {"src": src, "alt": image["alt"], "path": str(relative_path)}
    if destination.exists():
        return record
    try:
        destination.write_bytes(fetch(src))
    except (HTTPError, URLError):
        record["path"] = ""
        record["error"] = "download_failed"
    return record


def scrape(base_url: str, output_dir: Path) -> dict[str, object]:
    output_dir.mkdir(parents=True, exist_ok=True)
    queue = deque([normalize_url(base_url)])
    visited: set[str] = set()
    pages: list[dict[str, object]] = []
    errors: list[dict[str, str]] = []

    while queue:
        url = queue.popleft()
        if url in visited:
            continue
        visited.add(url)

        try:
            html = fetch(url)
        except (HTTPError, URLError) as exc:
            errors.append({"url": url, "error": str(exc)})
            continue
        soup = BeautifulSoup(html, "html.parser")
        title = page_title(soup, url)
        text_lines = extract_text(soup)
        images = extract_images(soup)
        slug = page_slug(url)
        downloaded = [download_image(output_dir, slug, image, i + 1) for i, image in enumerate(images)]
        markdown_file = save_markdown(output_dir, url, title, text_lines, downloaded)

        pages.append(
            {
                "url": url,
                "title": title,
                "slug": slug,
                "markdown": markdown_file,
                "text_line_count": len(text_lines),
                "image_count": len(downloaded),
                "images": downloaded,
            }
        )

        for link in extract_links(soup, url):
            if link not in visited:
                queue.append(link)

    manifest = {
        "base_url": normalize_url(base_url),
        "page_count": len(pages),
        "image_count": sum(page["image_count"] for page in pages),
        "error_count": len(errors),
        "errors": errors,
        "pages": pages,
    }
    (output_dir / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return manifest


def main() -> int:
    base_url = sys.argv[1] if len(sys.argv) > 1 else BASE_URL
    output_dir = Path(sys.argv[2]) if len(sys.argv) > 2 else OUTPUT_DIR
    manifest = scrape(base_url, output_dir)
    print(json.dumps({"page_count": manifest["page_count"], "image_count": manifest["image_count"]}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
