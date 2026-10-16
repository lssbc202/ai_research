#!/usr/bin/env python3
"""Discover books, generate mdBook summaries and full-book standalone HTML."""
import html
import tomllib
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BOOKS = ROOT / "books"
DIST = ROOT / "dist"

def title_for(path: Path) -> str:
    text = path.read_text(encoding="utf-8-sig")
    match = re.search(r"^#\s+(.+?)\s*$", text, re.MULTILINE)
    return match.group(1).strip() if match else path.stem.replace("-", " ")

def safe_children(folder: Path):
    return sorted((p for p in folder.iterdir()
                   if not p.name.startswith((".", "_")) and p.name != "SUMMARY.md"),
                  key=lambda p: (p.name.casefold(), p.name))

def collect(src: Path):
    """Return summary lines and ordered leaf Markdown files."""
    lines = ["# Summary", ""]
    pages = []
    homepage = src / "README.md"
    if homepage.exists():
        lines.extend(["[首页](README.md)", ""])
        pages.append(homepage)

    def walk(folder: Path, depth: int):
        for entry in safe_children(folder):
            if entry == homepage:
                continue
            if entry.is_dir():
                # Directory creates a chapter group, without requiring a README file.
                child_pages = list(entry.rglob("*.md"))
                if not any(p.name != "SUMMARY.md" and not any(
                        name.startswith((".", "_")) for name in p.relative_to(entry).parts)
                        for p in child_pages):
                    continue
                indent = "  " * depth
                month = re.fullmatch(r"(\d{4})-(0[1-9]|1[0-2])", entry.name)
                label = f"{month.group(1)}年{int(month.group(2))}月" if month else re.sub(r"^\d+[-_. ]+", "", entry.name).replace("-", " ").replace("_", " ").title()
                lines.append(f"{indent}- [{label}]()")
                walk(entry, depth + 1)
            elif entry.is_file() and entry.suffix.lower() == ".md":
                rel = entry.relative_to(src).as_posix()
                label = title_for(entry).replace("[", r"\[").replace("]", r"\]")
                lines.append(f'{"  " * depth}- [{label}]({rel})')
                pages.append(entry)
    walk(src, 0)
    return "\n".join(lines) + "\n", pages

def combine_markdown(src: Path, pages):
    """Merge pages; rewrite relative image URLs for pandoc's resource embedder."""
    parts = []
    for i, page in enumerate(pages):
        raw = page.read_text(encoding="utf-8-sig")
        # Resolve Markdown inline image paths relative to original Markdown source.
        def image_replace(match):
            prefix, target, suffix = match.groups()
            if re.match(r"^(?:https?://|data:|/|#)", target, re.I):
                return match.group(0)
            resolved = (page.parent / target).resolve()
            if not resolved.is_relative_to(src.resolve()) or not resolved.is_file():
                raise ValueError(f"Missing/outside image: {page}: {target}")
            return prefix + resolved.as_posix() + suffix
        raw = re.sub(r'(!\[[^\]]*\]\()([^\s)]+)(\))', image_replace, raw)
        title = title_for(page)
        section_id = f"document-{i}"
        # A stable unique marker for navigation even when H1 titles are duplicated.
        parts.append(f'\n\n<div id="{section_id}"></div>\n\n' + raw + "\n")
    return "\n".join(parts)

def run():
    DIST.mkdir(exist_ok=True)
    links = []
    for config in sorted(BOOKS.glob("*/book.toml")):
        base = config.parent
        slug = base.name
        src = base / "src"
        if not src.is_dir():
            raise ValueError(f"Missing src for {base}")
        print(f"Building {slug}", flush=True)
        with tempfile.TemporaryDirectory() as tmp:
            work = Path(tmp) / slug
            shutil.copytree(base, work)
            summary, pages = collect(work / "src")
            if not pages:
                raise ValueError(f"No Markdown pages found in {base}")
            (work / "src" / "SUMMARY.md").write_text(summary, encoding="utf-8")
            destination = DIST / slug
            if destination.exists():
                shutil.rmtree(destination)
            subprocess.run(["mdbook", "build", str(work), "--dest-dir", str(destination)], check=True)
            combined = Path(tmp) / "whole-book.md"
            combined.write_text(combine_markdown(work / "src", pages), encoding="utf-8")
            output = destination / "complete.html"
            subprocess.run([
                "pandoc", str(combined), "-o", str(output),
                "--standalone", "--embed-resources", "--toc",
                "--toc-depth=6", "--mathml",
                "--metadata", f"title={tomllib.loads(config.read_text(encoding='utf-8'))['book']['title']}",
            ], check=True)
            # Pandoc's default navigation is internal; all CSS and images are embedded.
            links.append((slug, tomllib.loads(config.read_text(encoding="utf-8"))["book"]["title"]))
    links_html = "\n".join(
        f'<li><a href="{html.escape(slug)}/">{html.escape(title)}</a> '
        f'· <a href="{html.escape(slug)}/complete.html">整本 HTML</a></li>'
        for slug, title in links
    )
    (DIST / "index.html").write_text(
        '<!doctype html><html lang="zh"><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1">'
        '<title>AI Research Library</title>'
        '<style>body{max-width:800px;margin:7vh auto;padding:0 24px;'
        'font:18px/1.8 system-ui,sans-serif}a{color:#1762a0}</style>'
        '<h1>AI Research Library</h1><p>公开研究书籍</p>'
        f'<ul>{links_html}</ul></html>', encoding="utf-8"
    )
    # Backward compatible link for the previous book address.
    redirects = {"rl-data-synthesis": "agent-harness-post-training"}
    for old, new in redirects.items():
        if not (DIST / new / "index.html").exists():
            continue
        folder = DIST / old
        folder.mkdir(exist_ok=True)
        (folder / "index.html").write_text(
            '<!doctype html><html lang="zh"><meta charset="utf-8">'
            '<meta http-equiv="refresh" content="0;url=../' + new + '/">'
            '<link rel="canonical" href="../' + new + '/">'
            '<title>Moved</title><a href="../' + new + '/">前往新书籍地址</a>',
            encoding="utf-8")
    (DIST / ".nojekyll").write_text("", encoding="utf-8")
    print(f"Built {len(links)} book(s).")

if __name__ == "__main__":
    run()
