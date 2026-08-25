# Thrillerrr Landing Pages — get.thrillerrr.in

Static hero landing pages migrated from Shopify pages (thrillerrr.myshopify.com,
"23-06-2026 down theme" — live theme, not modified) for deployment on the
get.thrillerrr.in subdomain via Vercel.

## Structure
- `pages/<slug>/index.html` — one static page per product/collection landing page
- `pages/index.html` — review index (not meant for production, just for QA)
- `manifest.json` — slug/title/CTA-target data for all pages
- `scripts/extract.py` — regenerates pages/ from raw/ (raw/ is gitignored, not committed)

## Deploy
Point Vercel's project root at `pages/` (or move pages/* to repo root before
connecting) so `get.thrillerrr.in/<slug>` resolves directly.

## Notes
- Each page's CTA button links back to the live Shopify store
  (collection or product page) — verify targets in manifest.json.
- Images are referenced directly from Shopify's CDN, not re-hosted.
- No live Shopify theme or content was modified to produce this.
