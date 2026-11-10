# Panda Federation — official website

This repository is the official public catalog for [Panda Federation](https://pandafederation.com/).

It is a static site hosted on GitHub Pages at the root of the `PandaFederation/pandafederation.github.io` org repo, with custom domain `pandafederation.com` (CNAME file in repo; GitHub Pages custom domain).

## What is on the site

- **Home** — 3D Federation emblem (three.js, with a still-image fallback), plus paths into every catalog tab
- **MCP Servers** — the four focused domain servers, the umbrella package, and Quiet File Team MCP, with verified GitHub, PyPI, Glama, Official MCP Registry, and directory links
- **Apify Tools** — every public Store Actor, with Agensi skills and free/paid edition switch notes where they apply
- **Apps & Repos** — Steel Panda, Watchdog Panda, Manual Remake, Quiet File Team, Hidden AI Instructions Watch, H.Q., and related modules
- **Books** — Spiral Saga titles that are in progress; no store links until a book is actually published
- **Services** — public Fiverr gigs, Upwork profile, live Agensi skills, dev.to writing, Product Hunt, and X
- **About** — contact is GitHub and X only

Inventory used to build the pages (verified URLs only) lives in this repo as `inventory.json` and, for the team, at `/workspace/promo/site-inventory.json`.

## Local preview

Serve the repo root with any static file server, for example:

```bash
python3 -m http.server 8080
```

Then open `http://localhost:8080/`. The 3D hero needs a web server (not a `file://` page) so the logo texture can load.

## License

MIT. Logo, crest, and headquarters stills are Panda Federation brand assets.
