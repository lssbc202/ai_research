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

def indent_headings(markdown: str) -> str:
    """Move ATX headings one level deeper, skipping fenced code blocks."""
    result = []
    fence = None
    for line in markdown.splitlines(keepends=True):
        marker = re.match(r"^ {0,3}(`{3,}|~{3,})", line)
        if marker:
            char, size = marker.group(1)[0], len(marker.group(1))
            if fence is None:
                fence = (char, size)
            elif char == fence[0] and size >= fence[1]:
                fence = None
            result.append(line)
            continue
        if fence is None:
            heading = re.match(r"^( {0,3})(#{1,6})([ \t]+)(.*)$", line)
            if heading:
                prefix, hashes, space, rest = heading.groups()
                if len(hashes) < 6:
                    line = prefix + "#" + hashes + space + rest
        result.append(line)
    return "".join(result)


def combine_markdown(src: Path, pages):
    """Create one continuous book with month > report > internal heading hierarchy."""
    parts = []
    previous_month = None
    for i, page in enumerate(pages):
        relative = page.relative_to(src)
        month_folder = relative.parts[0] if len(relative.parts) > 1 else None
        month = re.fullmatch(r"(\d{4})-(0[1-9]|1[0-2])", month_folder or "")
        if month_folder != previous_month:
            previous_month = month_folder
            if month:
                month_label = f"{month.group(1)}年{int(month.group(2))}月"
                parts.append(f"\n\n# {month_label}\n\n")
            elif month_folder:
                parts.append(f"\n\n# {month_folder}\n\n")
        raw = page.read_text(encoding="utf-8-sig")
        def image_replace(match):
            prefix, target, suffix = match.groups()
            if re.match(r"^(?:https?://|data:|/|#)", target, re.I):
                return match.group(0)
            resolved = (page.parent / target).resolve()
            if not resolved.is_relative_to(src.resolve()) or not resolved.is_file():
                raise ValueError(f"Missing/outside image: {page}: {target}")
            return prefix + resolved.as_posix() + suffix
        raw = re.sub(r'(!\[[^\]]*\]\()([^\s)]+)(\))', image_replace, raw)
        if month_folder:
            # The report H1 becomes H2 under the monthly H1.
            raw = indent_headings(raw)
        section_id = f"document-{i}"
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
                welcome = work / "src" / "index.md"
                title = tomllib.loads(config.read_text(encoding="utf-8"))["book"]["title"]
                welcome.write_text(
                    f"# {title}\n\n本书尚未发布日报；请在月份目录上传 YYYY-MM-DD.md。\n",
                    encoding="utf-8")
                summary, pages = collect(work / "src")
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
                "--css", str(ROOT / "scripts" / "continuous.css"),
                "--toc-depth=6", "--mathml",
                "--metadata", f"title={tomllib.loads(config.read_text(encoding='utf-8'))['book']['title']}",
            ], check=True)
            # Pandoc's default navigation is internal; all CSS and images are embedded.
            # Embed the table-of-contents controls inside the offline HTML.
            document = output.read_text(encoding="utf-8")
            # Keep Pandoc's TOC separate from a paper-like main content card.
            toc_end = re.search(r'<nav\\b[^>]*\\bid=["\\']TOC["\\'][^>]*>.*?</nav>', document, re.S)
            if toc_end:
                end = toc_end.end()
                document = document[:end] + '<main class="reading-paper">' + document[end:]
                document = document.replace("</body>", "</main>\\n</body>")

            script = (ROOT / "scripts" / "continuous-toc.js").read_text(encoding="utf-8")
            if "</body>" not in document:
                raise ValueError("Pandoc output is missing closing body tag")
            document = document.replace("</body>", "<script>\n" + script + "\n</script>\n</body>")
            output.write_text(document, encoding="utf-8")
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
