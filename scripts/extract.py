#!/usr/bin/env python3
"""
Extract the <main> hero-section content from each raw Shopify page and
generate a standalone static HTML file per landing page.
"""
import re
import os
import html
import json

RAW_DIR = "raw"
OUT_DIR = "pages"
SLUGS_FILE = "slugs.txt"

os.makedirs(OUT_DIR, exist_ok=True)

with open(SLUGS_FILE) as f:
    slugs = [l.strip() for l in f if l.strip()]

PAGE_TEMPLATE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta property="og:title" content="{title}">
<link rel="canonical" href="https://get.thrillerrr.in/{slug}">
<style>
  html,body{{margin:0;padding:0;background:#000;}}
  * {{ box-sizing: border-box; }}
</style>
</head>
<body class="{body_class}">
{main_content}
</body>
</html>
"""

report = []

for slug in slugs:
    raw_path = os.path.join(RAW_DIR, f"{slug}.html")
    if not os.path.exists(raw_path):
        report.append((slug, "MISSING RAW FILE"))
        continue

    with open(raw_path, "r", encoding="utf-8", errors="replace") as f:
        raw = f.read()

    # body class
    m = re.search(r'<body class="([^"]*)"', raw)
    body_class = m.group(1) if m else ""

    # title
    m = re.search(r'<meta property="og:title" content="([^"]*)"', raw)
    title = html.unescape(m.group(1)) if m else slug

    # main content block
    m = re.search(r'<main id="MainContent".*?>(.*?)</main>', raw, re.DOTALL)
    if not m:
        report.append((slug, "NO <main> MATCH"))
        continue
    main_content = m.group(1).strip()

    # sanity: does it contain a headline + CTA?
    has_h1 = "<h1" in main_content
    cta_match = re.search(r'href="([^"]*)"\s*class="yellowcta_deb"', main_content)
    cta_href = cta_match.group(1) if cta_match else None
    headline_match = re.search(r'<h1[^>]*>(.*?)</h1>', main_content, re.DOTALL)
    headline = re.sub('<[^<]+?>', '', headline_match.group(1)).strip() if headline_match else None

    out_html = PAGE_TEMPLATE.format(
        title=html.escape(title),
        slug=slug,
        body_class=html.escape(body_class),
        main_content=main_content,
    )

    page_dir = os.path.join(OUT_DIR, slug)
    os.makedirs(page_dir, exist_ok=True)
    with open(os.path.join(page_dir, "index.html"), "w", encoding="utf-8") as f:
        f.write(out_html)

    report.append((slug, "OK", headline, cta_href, has_h1))

manifest = [
    {"slug": r[0], "title": r[2], "cta_href": r[3]}
    for r in report if r[1] == "OK"
]
with open("manifest.json", "w") as f:
    json.dump(manifest, f, indent=2)

# root index for quick review of all pages
index_rows = "\n".join(
    f'<tr><td><a href="/{m["slug"]}/">{m["slug"]}</a></td>'
    f'<td>{html.escape(m["title"] or "")}</td>'
    f'<td>{html.escape(m["cta_href"] or "")}</td></tr>'
    for m in manifest
)
index_html = f"""<!doctype html>
<html><head><meta charset="utf-8"><title>Thrillerrr Landing Pages — Review Index</title>
<style>body{{font-family:sans-serif;background:#111;color:#eee;padding:24px;}}
table{{border-collapse:collapse;width:100%}}
td{{padding:8px;border-bottom:1px solid #333}}
a{{color:#eb4687}}</style></head>
<body>
<h1>{len(manifest)} landing pages (review index — not part of final deploy)</h1>
<table><tr><th>Slug</th><th>Headline</th><th>CTA target</th></tr>
{index_rows}
</table>
</body></html>
"""
with open(os.path.join(OUT_DIR, "index.html"), "w") as f:
    f.write(index_html)

# Print report
print(f"{'slug':<18} {'status':<10} {'has_h1':<7} {'cta_href':<32} headline")
for row in report:
    if row[1] == "OK":
        slug, status, headline, cta_href, has_h1 = row
        print(f"{slug:<18} {status:<10} {str(has_h1):<7} {str(cta_href):<32} {headline}")
    else:
        print(f"{row[0]:<18} {row[1]}")
