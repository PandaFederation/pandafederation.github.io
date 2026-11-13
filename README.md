# Panda Federation — official website

This repository is the official public catalog for [Panda Federation](https://pandafederation.com/).

It is a static site hosted on GitHub Pages at the root of the `PandaFederation/pandafederation.github.io` org repo, with custom domain `pandafederation.com` (CNAME file in repo; GitHub Pages custom domain).

## What is on the site

- **Home** — 3D Federation emblem (three.js, with a still-image fallback), plus paths into every catalog tab
- **MCP Servers** — the four focused domain servers, the umbrella package, and Quiet File Team MCP, with verified GitHub, PyPI, Glama, Official MCP Registry, and directory links
- **Apify Tools** — every public Store Actor, with Agensi skills and free/paid edition switch notes where they apply
- **Apps & Repos** — Steel Panda, Watchdog Panda, Manual Remake, Quiet File Team (product page: https://pandafederation.com/quiet-file-team/), Hidden AI Instructions Watch, H.Q., and related modules
- **Services** — public Fiverr gigs, Upwork profile, live Agensi skills, dev.to writing, Product Hunt, and X
- **What's New** — changelog generated from our releases, with an Atom feed at `/feed.xml`, plus the weekly digest
- **About** — contact is GitHub and X only
- **Books** (footer link) — Spiral Saga titles that are in progress; no store links until a book is actually published

Inventory used to build the pages (verified URLs only) lives in this repo as `inventory.json` and, for the team, at `/workspace/promo/site-inventory.json`.

## Generated content

`scripts/build.py` rebuilds the parts of the site that come from live public data, and the
`Rebuild generated site data` workflow runs it on every push to `main` and daily (6:17 AM Arizona time):

- `<span data-gen="...">` markers: Apify Actor count (Apify Store API), focused-server tool counts
  (`panda-federation-tools` `domains.py` on GitHub), PyPI versions, app / skill / server counts
- `whats-new/index.html` and `feed.xml` (Atom): GitHub releases, Official MCP Registry listings,
  new public Apify Actors, and `data/changelog-site.json`
- `digest/`: weekly digest issues from `digest/issues/*.md`; only `status: published` issues are rendered
- `index.html` sample tables from `data/samples.json` (rows from real Actor test runs)
- nav, footer links, the Cloudflare Web Analytics beacon and `sitemap.xml` on every page (`scripts/chrome.py`)
- `scripts/agents.py` (last build step) writes `llms.txt`, `pricing.md`, `llms-full.txt`, Markdown mirrors of each public page, `.well-known/ai-catalog.json`, the JSON-LD on every page (including visible-matching Apify list rates on tool cards), PyPI/Registry fields in the WebMCP catalogs, and `sitemap.xml`. Edit the generator or its sources (`webmcp-catalog.json`, page copy, digest issues), not those outputs. Machine-readable rates must match the visible card text.

**Catalog schema is automatic.** Every catalog page, and any new page that uses `article.card`, gets SoftwareApplication and/or ItemList JSON-LD from the same visible cards (tool-like links become SoftwareApplication; other cards become WebPage or a name-only item — no invented urls or prices). Hand-written JSON-LD on product landings (`quiet-file-team`, `data-broker-removal`) is left in place and only patched with live facts such as the PyPI version. `scripts/check_jsonld.py` runs at the end of `scripts/build.py` and as a step in the Rebuild generated site data workflow (CI and the daily 6:17 AM Arizona build). The check fails the build if JSON-LD does not parse, a required field is missing, a JSON-LD price differs from the visible card, or a catalog page has no schema.

Run locally with `python3 scripts/build.py`. Warnings (for example a public Actor without a card on
`apify.html`) are printed as `WARN:` lines in the workflow log. A failed JSON-LD check exits non-zero and is not committed.

## Local preview

Serve the repo root with any static file server, for example:

```bash
python3 -m http.server 8080
```

Then open `http://localhost:8080/`. The 3D hero needs a web server (not a `file://` page) so the logo texture can load.

## License

MIT. Logo, crest, and headquarters stills are Panda Federation brand assets.
