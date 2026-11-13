"""Agent-facing files, generated so they cannot drift from the site:

- llms.txt: counts, MCP servers (install, PyPI, Registry), every public Apify
  Actor (live from the Apify Store), apps, planned modules, updates (What's New,
  Atom feed, digest), About and Agensi.
- pricing.md and visible list-rate lines on apify.html cards: the same Apify
  Store API rates as the SoftwareApplication offers in JSON-LD and llms.txt.
- Markdown mirrors of each public HTML page, llms-full.txt, and
  .well-known/ai-catalog.json.
- JSON-LD on every page we own (Organization/WebSite, AboutPage, ItemLists,
  Blog/BlogPosting, SoftwareApplication offers), plus PyPI/Registry facts on
  the Quiet File Team MCP page.
- PyPI and Registry fields in the WebMCP catalogs.
- sitemap.xml (runs last, so new digest issues are included on the same build).

Machine-readable text must match what people see. Do not put a rate in
JSON-LD, llms.txt, or pricing.md unless the matching visible page shows it.
"""
import glob
import html as H
import json
import os
import re
from datetime import date
from html.parser import HTMLParser

SITE = "https://pandafederation.com"
OWNER = "pandadad0214"
REG = "https://registry.modelcontextprotocol.io/v0/servers?search=io.github.%s/" % OWNER
FAMILY = [("research", "Research"), ("funding", "Public funding"), ("leads", "Leads"),
          ("security", "Web and email security"), ("apps", "Apps and kits")]
SAME_AS = [
    "https://github.com/pandadad0214", "https://x.com/PandaFedHQ", "https://apify.com/pandadad0214",
    "https://www.agensi.io/creators/panda-federation", "https://dev.to/pandadad0214",
    "https://www.producthunt.com/products/panda-federation-tools", "https://www.fiverr.com/pandafederation",
    "https://www.upwork.com/freelancers/~010efd521970a9d3e1",
    "https://peerlist.io/pandadad0214/project/panda-federation-tools",
]
LD_RE = re.compile(r'\n?[ \t]*<script type="application/ld\+json">.*?</script>', re.S)
SKIP = ("node_modules/", ".git/")
# pages whose JSON-LD is hand-written for that product; only facts get patched
OWN_LD = ("data-broker-removal/index.html", "quiet-file-team/index.html", "quiet-file-team-mcp/index.html")


def _text(s):
    return re.sub(r"\s+", " ", H.unescape(re.sub(r"<[^>]+>", "", s))).strip()


def _meta_desc(read, p):
    m = re.search(r'<meta name="description" content="([^"]*)"', read(p))
    return H.unescape(m.group(1)) if m else ""


def _issues(read):
    out = []
    for p in sorted(glob.glob("digest/issues/*.md")):
        m = re.match(r"---\n(.*?)\n---\n(.*)", read(p), re.S)
        if not m:
            continue
        meta = {k.strip(): v.split("#", 1)[0].strip() for k, v in (l.split(":", 1) for l in m.group(1).splitlines() if ":" in l)}
        if meta.get("status") != "published":
            continue
        meta["slug"] = f"{int(meta['number']):03d}-{meta['date']}"
        meta["lede"] = next((l.strip() for l in m.group(2).splitlines() if l.strip() and not l.startswith("#")), "")
        out.append(meta)
    return sorted(out, key=lambda x: x["date"], reverse=True)


def _usd(x):
    return ("%.6f" % x).rstrip("0").rstrip(".")


def pricing(a):
    """Live Apify Store pricing for one Actor -> (offer JSON-LD, short text) or (None, None).

    Rates come from currentPricingInfo in the Apify Store API on every build.
    For tiered events the list rate is the Apify free-plan tier; paid Apify plans pay less.
    """
    pi = a.get("currentPricingInfo") or {}
    model = pi.get("pricingModel")
    store = f"https://apify.com/{OWNER}/{a['name']}"
    if model == "FREE":
        return ({"@type": "Offer", "url": store, "price": "0", "priceCurrency": "USD", "isAccessibleForFree": True}, "free")
    if model != "PAY_PER_EVENT":
        return None, None
    specs, text, main = [], [], None
    events = (pi.get("pricingPerEvent") or {}).get("actorChargeEvents") or {}
    for key, ev in events.items():
        tiers = ev.get("eventTieredPricingUsd") or {}
        price = ev.get("eventPriceUsd")
        low = None
        if price is None and tiers:
            price = (tiers.get("FREE") or {}).get("tieredEventPriceUsd")
            vals = [t.get("tieredEventPriceUsd") for t in tiers.values() if t.get("tieredEventPriceUsd") is not None]
            low = min(vals) if vals else None
        if price is None:
            continue
        title = ev.get("eventTitle") or key
        spec = {"@type": "UnitPriceSpecification", "price": _usd(price), "priceCurrency": "USD",
                "unitText": title, "referenceQuantity": {"@type": "QuantitativeValue", "value": 1, "unitText": title}}
        if low is not None and low < price:
            spec["description"] = f"Apify free-plan rate; paid Apify plans pay down to {_usd(low)} USD"
        specs.append(spec)
        if key != "apify-actor-start":
            text.append(f"{_usd(price)} USD per {title.lower()}" + (f" (down to {_usd(low)} on paid Apify plans)" if low is not None and low < price else ""))
            main = main or price
    if not specs:
        return None, None
    offer = {"@type": "Offer", "url": store, "priceCurrency": "USD", "price": _usd(main if main is not None else float(specs[0]["price"])),
             "priceSpecification": specs,
             "description": "Pay per event on Apify. Rates are read from the Apify Store API when this site builds; the Store page is authoritative."}
    return offer, "; ".join(text)


def _ld(obj):
    return '<script type="application/ld+json">\n' + json.dumps(obj, indent=2, ensure_ascii=False) + "\n</script>"


def run(get, read, write, warn, values, actors):
    changed = []
    cat = json.loads(read("webmcp-catalog.json"))
    fam = {a["id"]: a.get("family") for a in cat.get("actors", [])}

    # ---------- catalogs: PyPI + Registry facts from live lookups
    def patch_servers(servers):
        for s in servers:
            v = values.get(f"pypi:{s['id']}")
            if v:
                s["pypi"] = f"https://pypi.org/project/{s['id']}/"
                s["pypi_version"] = v
            if values.get(f"registry:{s['id']}"):
                s["registry"] = REG + s["id"]
    for p in ["webmcp-catalog.json"] + sorted(glob.glob("*/webmcp-catalog.json")):
        c = cat if p == "webmcp-catalog.json" else json.loads(read(p))
        before = json.dumps(c, sort_keys=True)
        patch_servers(c.get("servers", []))
        if p == "webmcp-catalog.json":
            c["site"]["description"] = _meta_desc(read, "index.html")
        if json.dumps(c, sort_keys=True) == before:
            continue  # keep the file's own formatting when nothing changed
        if write(p, json.dumps(c, indent=2, ensure_ascii=False) + "\n"):
            changed.append(p)

    inv = json.loads(read("inventory.json"))
    inv.setdefault("brand", {})["tagline"] = _meta_desc(read, "index.html")
    if write("inventory.json", json.dumps(inv, indent=2, ensure_ascii=False) + "\n"):
        changed.append("inventory.json")

    servers = cat.get("servers", [])
    headline = _text(re.search(r"<h1[^>]*>(.*?)</h1>", read("index.html"), re.S).group(1))
    site_desc = _meta_desc(read, "index.html")
    about_art = re.search(r'<article class="prose">(.*?)</article>', read("about.html"), re.S)
    about_lede = _text(re.search(r"<p>(.*?)</p>", about_art.group(1), re.S).group(1)) if about_art else ""
    issues = _issues(read)
    models = {a["name"]: (a.get("currentPricingInfo") or {}).get("pricingModel") for a in actors}
    n_free = sum(1 for m in models.values() if m == "FREE")
    n_ppe = sum(1 for m in models.values() if m == "PAY_PER_EVENT")

    # ---------- llms.txt
    L = [f"# Panda Federation", "", f"> {headline} {site_desc} Official site: {SITE}/", ""]
    L += [f"At a glance: {values['apify_actors']} public Apify Actors, {values['mcp_servers']} MCP servers "
          f"({values['tools:total']} tools across the four focused domain servers), {values['apps']} apps and repos, "
          f"{values['agensi_skills']} Agensi skills. These numbers are rebuilt from the Apify Store, PyPI, the MCP Registry "
          f"and GitHub on every site build.", ""]
    L += ["This site includes read-only WebMCP tools (list_servers, list_tools, "
          "search_tools, get_install_command, get_links, list_actors, list_apps, list_editions) "
          "when a browser exposes document.modelContext. Catalog: "
          f"{SITE}/webmcp-catalog.json", ""]
    L += ["## MCP servers", ""]
    for s in servers:
        bits = [f"- {s['name']} ({s.get('tool_count')} tools): `{s['install']['uvx']}`"]
        bits.append(f" — {s['description']}")
        links = [s.get("repo")]
        if s.get("homepage") and s["homepage"] != s.get("repo"):
            links.append(s["homepage"])
        if s.get("pypi"):
            links.append(f"PyPI {s.get('pypi_version')}: {s['pypi']}")
        if values.get(f"registry:{s['id']}"):
            links.append(f"Official MCP Registry: io.github.{OWNER}/{s['id']}")
        need = s["install"].get("requires") or []
        bits.append(" Needs " + ", ".join(f"`{x}`" for x in need) + "." if need else " No token needed.")
        L.append("".join(bits) + " " + " · ".join(x for x in links if x))
    L += ["", f"Install and client-config snippets for every server: {SITE}/mcp.html", ""]

    L += ["## Apify Actors", "",
          f"{len(actors)} public Actors, read live from the Apify Store. {n_ppe} are pay-per-event and {n_free} is free. "
          "Per-event rates below are read from the Apify Store API each time this site builds (list rate = Apify free plan; "
          "paid Apify plans pay less). Every run also has Apify's small Actor-start event. The Store page is authoritative. "
          f"Sources are official or public. Cards with descriptions: {SITE}/apify.html", ""]
    by = {}
    for a in actors:
        f = fam.get(a["name"])
        if f is None:
            warn.append(f"llms.txt: Actor {a['name']} has no family in webmcp-catalog.json")
        by.setdefault(f, []).append(a)
    for key, label in FAMILY + [(None, "Other")]:
        if not by.get(key):
            continue
        L.append(f"### {label}")
        for a in sorted(by[key], key=lambda x: x["title"].lower()):
            _, rate = pricing(a)
            if rate is None:
                warn.append(f"llms.txt: no live pricing for {a['name']}")
            L.append(f"- {a['title']}: https://apify.com/{OWNER}/{a['name']}" + (f" — {rate}" if rate else ""))
        L.append("")

    L += ["## Local-first apps and repos", ""]
    for a in cat.get("apps", []):
        url = a.get("homepage") or a.get("repo")
        L.append(f"- {a['name']}: {a['description']} {url}" + (f" (repo: {a['repo']})" if a.get("homepage") and a.get("repo") else ""))
    planned = cat.get("planned_modules", [])
    if planned:
        L.append("- Planned, not shipped yet: " + ", ".join(f"{p['id'].replace('_', ' ')} ({p['repo']})" for p in planned)
                 + ". Placeholder repos with no code.")
    L += ["", f"More: {SITE}/apps.html. Quiet File Team plain-text notes: {SITE}/quiet-file-team/llms.txt and "
          f"{SITE}/quiet-file-team-mcp/llms.txt", ""]

    L += ["## Free guides", "",
          f"- Free data broker removal guide + US state law map (not legal advice): {SITE}/data-broker-removal/ — "
          f"plain-text notes and JSON: {SITE}/data-broker-removal/llms.txt", ""]

    L += ["## Updates", "",
          f"- What's New (changelog from our releases, Registry listings, new Actors and site launches): {SITE}/whats-new/",
          f"- Atom feed: {SITE}/feed.xml",
          f"- Weekly digest (MCP, Apify and public-data news with our take): {SITE}/digest/"]
    if issues:
        i = issues[0]
        L.append(f"- Latest digest: #{i['number']} ({i['date']}), {i.get('title', '')}: {SITE}/digest/{i['slug']}/")
    L.append("")

    shop_line = _shop_line(get, warn)
    L += ["## About", "", f"{about_lede} {SITE}/about.html", "",
          "Free and paid editions of the same tool always name each other and say how to switch. "
          f"Apify list rates are on each tool card and on {SITE}/pricing.md. The Store page is authoritative. "
          "Fiverr, Upwork and Agensi package prices stay on those listings.", ""]
    L += ["## Services and skills", "",
          f"- Services: {SITE}/services.html",
          f"- {values['agensi_skills']} Agensi skills, each linked to its related Apify Actor: {SITE}/agensi.html", ""]
    L += ["## Other entry points", "",
          f"- Apify Store: https://apify.com/{OWNER}",
          f"- Official MCP Registry: https://registry.modelcontextprotocol.io/v0/servers?search=io.github.{OWNER}",
          f"- GitHub: https://github.com/{OWNER}",
          "- X: https://x.com/PandaFedHQ  (Follow on X: @PandaFedHQ)",
          "- Product Hunt: https://www.producthunt.com/products/panda-federation-tools",
          f"- Pricing (same list rates as the Apify cards): {SITE}/pricing.md",
          f"- Full page markdown: {SITE}/llms-full.txt",
          f"- AI catalog: {SITE}/.well-known/ai-catalog.json",
          f"- WebMCP manifest: {SITE}/.well-known/webmcp.json",
          f"- Inventory: {SITE}/inventory.json",
          f"- Sitemap: {SITE}/sitemap.xml",
          f"- Full tool notes: https://{OWNER}.github.io/panda-federation-tools/llms.txt",
          f"- {shop_line}", ""]
    if write("llms.txt", "\n".join(L)):
        changed.append("llms.txt")

    apify_html = read("apify.html")
    apify2, price_lines = inject_apify_prices(apify_html, actors, warn)
    if write("apify.html", apify2):
        changed.append("apify.html")
    pricing_md = build_pricing_md(actors, fam, servers, values, shop_line, price_lines)
    if write("pricing.md", pricing_md):
        changed.append("pricing.md")

    # ---------- JSON-LD
    org = {"@type": "Organization", "@id": f"{SITE}/#org", "name": "Panda Federation", "url": f"{SITE}/",
           "logo": f"{SITE}/assets/logo.png", "description": site_desc, "sameAs": SAME_AS}
    ctx = "https://schema.org"

    def _card_bodies(page):
        return re.findall(r'<article class="card"[^>]*>(.*?)</article>', read(page), re.S)

    def _abs_url(href, page=""):
        if not href:
            return None
        if href.startswith("http://") or href.startswith("https://"):
            return href
        if href.startswith("/"):
            return SITE + href
        base = f"{SITE}/" + (page.rsplit("/", 1)[0] + "/" if "/" in page else "")
        return base + href

    def _plain(frag):
        return re.sub(r"\s+", " ", H.unescape(re.sub(r"<[^>]+>", " ", frag or ""))).strip()

    def _is_tool_url(u):
        low = (u or "").lower()
        return any(h in low for h in (
            "apify.com", "github.com", "pypi.org", "agensi.io",
            "npmjs.com", "modelcontextprotocol.io", "gitlab.com",
        ))

    def page_ld(p):
        url = f"{SITE}/" + (p[:-len("index.html")] if p.endswith("index.html") else p)
        desc = _meta_desc(read, p)
        if p == "index.html":
            website = {"@type": "WebSite", "@id": f"{SITE}/#site", "name": "Panda Federation",
                       "url": f"{SITE}/", "description": f"{headline} {site_desc}", "publisher": {"@id": f"{SITE}/#org"}}
            items = []
            for n, body in enumerate(_card_bodies("index.html"), 1):
                heading = re.search(r"<h[23][^>]*>(.*?)</h[23]>", body, re.S)
                lede = re.search(r"<p>(.*?)</p>", body, re.S)
                hrefs = re.findall(r'href="([^"]+)"', body)
                item_url = _abs_url(hrefs[0], "index.html") if hrefs else None
                if not heading or not item_url:
                    continue
                entry = {"@type": "WebPage", "name": _plain(heading.group(1)), "url": item_url}
                if lede:
                    entry["description"] = _plain(lede.group(1))
                items.append({"@type": "ListItem", "position": n, "item": entry})
            if items:
                website["mainEntity"] = {"@type": "ItemList", "name": "Catalogs and guides on this site",
                                         "numberOfItems": len(items), "itemListElement": items}
            return {"@context": ctx, "@graph": [org, website]}
        if p == "about.html":
            return {"@context": ctx, "@graph": [org, {"@type": "AboutPage", "url": url, "name": "About Panda Federation",
                    "description": about_lede, "about": {"@id": f"{SITE}/#org"}}]}
        if p == "apify.html":
            items = []
            for n, a in enumerate(sorted(actors, key=lambda x: x["title"].lower()), 1):
                app = {"@type": "SoftwareApplication", "name": a["title"], "url": f"https://apify.com/{OWNER}/{a['name']}",
                       "applicationCategory": "DeveloperApplication", "operatingSystem": "Apify platform (cloud)",
                       "description": a.get("description", ""), "publisher": {"@id": f"{SITE}/#org"}}
                offer, _ = pricing(a)
                if offer:
                    app["offers"] = offer
                items.append({"@type": "ListItem", "position": n, "item": app})
            return {"@context": ctx, "@graph": [org, {"@type": "CollectionPage", "url": url, "name": "Apify Tools",
                    "description": desc, "mainEntity": {"@type": "ItemList", "numberOfItems": len(items), "itemListElement": items}}]}
        if p == "mcp.html":
            items = []
            for n, s in enumerate(servers, 1):
                app = {"@type": "SoftwareApplication", "name": s["name"], "applicationCategory": "DeveloperApplication",
                       "description": s["description"], "url": s.get("homepage") or s.get("repo"), "codeRepository": s.get("repo"),
                       "isAccessibleForFree": True, "publisher": {"@id": f"{SITE}/#org"}}
                if s.get("pypi_version"):
                    app["softwareVersion"] = s["pypi_version"]
                    app["downloadUrl"] = s["pypi"]
                items.append({"@type": "ListItem", "position": n, "item": app})
            return {"@context": ctx, "@graph": [org, {"@type": "CollectionPage", "url": url, "name": "MCP Servers",
                    "description": desc, "mainEntity": {"@type": "ItemList", "numberOfItems": len(items), "itemListElement": items}}]}
        if p == "apps.html":
            items = []
            for n, a in enumerate(cat.get("apps", []), 1):
                item_url = a.get("homepage") or a.get("repo")
                item_url = _abs_url(item_url, "apps.html") if item_url else None
                app = {"@type": "SoftwareApplication", "name": a["name"],
                       "applicationCategory": "DeveloperApplication",
                       "description": a.get("description") or "",
                       "url": item_url, "publisher": {"@id": f"{SITE}/#org"}}
                if a.get("repo"):
                    app["codeRepository"] = a["repo"]
                if (a.get("description") or "").lower().startswith("free "):
                    app["isAccessibleForFree"] = True
                items.append({"@type": "ListItem", "position": n, "item": app})
            return {"@context": ctx, "@graph": [org, {"@type": "CollectionPage", "url": url, "name": "Apps & Repos",
                    "description": desc, "mainEntity": {"@type": "ItemList", "numberOfItems": len(items), "itemListElement": items}}]}
        if p == "agensi.html":
            items = []
            for n, body in enumerate(_card_bodies("agensi.html"), 1):
                heading = re.search(r"<h3[^>]*>(.*?)</h3>", body, re.S)
                hrefs = re.findall(r'href="([^"]+)"', body)
                item_url = next((h for h in hrefs if "agensi.io/" in h), hrefs[0] if hrefs else None)
                if not heading or not item_url:
                    warn.append(f"agensi.html card {n}: missing name or url")
                    continue
                app = {"@type": "SoftwareApplication", "name": _plain(heading.group(1)),
                       "url": item_url, "applicationCategory": "DeveloperApplication",
                       "publisher": {"@id": f"{SITE}/#org"}}
                if re.search(r"Free skill", body):
                    app["isAccessibleForFree"] = True
                items.append({"@type": "ListItem", "position": n, "item": app})
            expected = int(values["agensi_skills"])
            if len(items) != expected:
                warn.append(f"agensi.html JSON-LD listed {len(items)} skills, page has {expected}")
            return {"@context": ctx, "@graph": [org, {"@type": "CollectionPage", "url": url, "name": "Agensi skills",
                    "description": desc, "mainEntity": {"@type": "ItemList", "numberOfItems": len(items), "itemListElement": items}}]}
        if p == "whats-new/index.html":
            return {"@context": ctx, "@graph": [org, {"@type": "CollectionPage", "url": url, "name": "What's New",
                    "description": desc, "isPartOf": {"@id": f"{SITE}/#site"}}]}
        if p == "digest/index.html":
            return {"@context": ctx, "@graph": [org, {"@type": "Blog", "url": url, "name": "Panda Federation weekly digest",
                    "description": desc, "publisher": {"@id": f"{SITE}/#org"},
                    "blogPost": [{"@type": "BlogPosting", "headline": f"Digest #{i['number']}: {i.get('title', '')}",
                                  "datePublished": i["date"], "url": f"{SITE}/digest/{i['slug']}/"} for i in issues]}]}
        m = re.match(r"digest/(\d{3}-\d{4}-\d{2}-\d{2})/index\.html$", p)
        if m:
            i = next((x for x in issues if x["slug"] == m.group(1)), None)
            if i:
                return {"@context": ctx, "@graph": [org, {"@type": "BlogPosting", "url": url,
                        "headline": f"Digest #{i['number']}: {i.get('title', '')}", "description": i["lede"],
                        "datePublished": i["date"], "author": {"@id": f"{SITE}/#org"}, "publisher": {"@id": f"{SITE}/#org"},
                        "isPartOf": {"@type": "Blog", "url": f"{SITE}/digest/"}}]}
        # Automatic catalog fallback: any page with visible article.card
        # elements (books, services, and any future catalog) gets an ItemList
        # built from those cards. Do not invent urls or prices.
        cards = _card_bodies(p)
        if cards:
            h1 = re.search(r"<h1[^>]*>(.*?)</h1>", read(p), re.S)
            name = _plain(h1.group(1)) if h1 else p
            items = []
            for n, body in enumerate(cards, 1):
                heading = re.search(r"<h[23][^>]*>(.*?)</h[23]>", body, re.S)
                if not heading:
                    warn.append(f"{p} card {n}: missing heading")
                    continue
                lede = re.search(r"<p>(.*?)</p>", body, re.S)
                hrefs = re.findall(r'href="([^"]+)"', body)
                item_url = _abs_url(hrefs[0], p) if hrefs else None
                typ = "SoftwareApplication" if item_url and _is_tool_url(item_url) else (
                    "WebPage" if item_url else "Thing"
                )
                entry = {"@type": typ, "name": _plain(heading.group(1))}
                if item_url:
                    entry["url"] = item_url
                if typ == "SoftwareApplication":
                    entry["applicationCategory"] = "DeveloperApplication"
                    entry["publisher"] = {"@id": f"{SITE}/#org"}
                if lede:
                    entry["description"] = _plain(lede.group(1))
                items.append({"@type": "ListItem", "position": n, "item": entry})
            if items:
                return {"@context": ctx, "@graph": [org, {
                    "@type": "CollectionPage", "url": url, "name": name,
                    "description": desc,
                    "mainEntity": {
                        "@type": "ItemList", "name": name,
                        "numberOfItems": len(items), "itemListElement": items,
                    },
                }]}
        return {"@context": ctx, **org}

    pages = sorted(p for p in glob.glob("**/*.html", recursive=True) if not p.startswith(SKIP))
    for p in pages:
        s = read(p)
        if 'http-equiv="refresh"' in s or "</head>" not in s:
            continue
        if p in OWN_LD:
            if p == "quiet-file-team-mcp/index.html":
                def fix(m):
                    d = json.loads(m.group(1))
                    q = next((x for x in servers if x["id"] == "quiet-file-team-mcp"), {})
                    if q.get("pypi_version"):
                        d["softwareVersion"] = q["pypi_version"]
                        d["downloadUrl"] = q["pypi"]
                    d["sameAs"] = [u for u in (q.get("pypi"), q.get("registry")) if u]
                    return '<script type="application/ld+json">\n' + json.dumps(d, indent=2, ensure_ascii=False) + "\n</script>"
                s2 = re.sub(r'<script type="application/ld\+json">\s*(.*?)\s*</script>', fix, s, count=1, flags=re.S)
            else:
                continue
        else:
            s2 = LD_RE.sub("", s)
            s2 = s2.replace("</head>", _ld(page_ld(p)) + "\n</head>", 1)
        if write(p, s2):
            changed.append(p)

    # ---------- canonical check: one non-www canonical per indexable page, matching its own URL
    for p in pages:
        h = read(p)
        if p == "404.html" or 'http-equiv="refresh"' in h:
            continue
        want = f"{SITE}/" + (p[:-len("index.html")] if p.endswith("index.html") else p)
        got = re.findall(r'<link rel="canonical" href="([^"]*)"', h)
        if got != [want]:
            warn.append(f"canonical on {p}: {got} (expected {want})")

    md_changed = write_markdown_mirrors(read, write, warn, pages)
    catalog_json = build_ai_catalog(values, servers)
    if write(".well-known/ai-catalog.json", json.dumps(catalog_json, indent=2, ensure_ascii=False) + "\n"):
        md_changed.append(".well-known/ai-catalog.json")

    # ---------- sitemap (last step, so it sees pages built by earlier modules)
    urls = []
    for p in pages:
        if p == "404.html" or 'http-equiv="refresh"' in read(p):
            continue
        urls.append(f"{SITE}/" + (p[:-len("index.html")] if p.endswith("index.html") else p))
    urls += [
        f"{SITE}/feed.xml",
        f"{SITE}/llms.txt",
        f"{SITE}/llms-full.txt",
        f"{SITE}/pricing.md",
        f"{SITE}/.well-known/ai-catalog.json",
        f"{SITE}/.well-known/webmcp.json",
    ]
    skip_md = ("README.md", "LICENSE")
    for md in glob.glob("**/*.md", recursive=True):
        if md.startswith(SKIP) or md.startswith("digest/issues/") or md.startswith("scripts/"):
            continue
        if os.path.basename(md) in skip_md:
            continue
        urls.append(f"{SITE}/{md}")
    urls = sorted(set(urls), key=lambda u: (u.count("/"), u))
    sm = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    sm += [f"  <url><loc>{u}</loc></url>" for u in urls]
    sm.append("</urlset>\n")
    if write("sitemap.xml", "\n".join(sm)):
        changed.append("sitemap.xml")
    changed += md_changed
    return changed


SHOP = "https://shop.pandafederation.com/"
CARD_RE = re.compile(r'(<article class="card"[^>]*>)(.*?)(</article>)', re.S)


def _shop_line(get, warn):
    """Honest shop inventory sentence from the public product feed."""
    try:
        data = get("https://shop.pandafederation.com/feeds/products.json")
        n = len(data.get("items") or [])
    except Exception as e:  # noqa: BLE001
        warn.append(f"shop feed lookup failed: {e}")
        return (
            f"Panda Federation Shop (cables, racks, and lab gear): {SHOP} — "
            "see that site for current inventory and item prices."
        )
    if n == 0:
        return (
            f"Panda Federation Shop (cables, racks, and lab gear): {SHOP} — "
            "no products listed in the shop feed when this site built. "
            "Item prices, when listed, appear on that site."
        )
    return (
        f"Panda Federation Shop (cables, racks, and lab gear): {SHOP} — "
        f"{n} item{'s' if n != 1 else ''} in the shop feed when this site built. "
        "Item prices appear on that site."
    )


def _rate_sentence(rate):
    if rate == "free":
        return "Free on the Apify Store."
    return f"List rate: {rate}. The Apify Store page is authoritative."


def inject_apify_prices(html, actors, warn):
    """Add a visible list-rate line to each Actor card, matching JSON-LD/llms.txt."""
    rates = {a["name"]: pricing(a)[1] for a in actors}
    price_lines = {}

    def one(m):
        body = m.group(2)
        slugs = re.findall(rf"apify\.com/{OWNER}/([a-z0-9-]+)", body)
        slug = slugs[0] if slugs else None
        if not slug:
            return m.group(0)
        rate = rates.get(slug)
        if rate is None:
            warn.append(f"apify card {slug}: no live pricing")
            text = "Live price is on the Apify Store listing."
        else:
            text = _rate_sentence(rate)
        price_lines[slug] = text
        body = re.sub(r'\n?<p class="price" data-gen="apify-price:[^"]+">.*?</p>', "", body)
        body2, n = re.subn(
            r"(<h3>.*?</h3>\s*<p>.*?</p>)",
            rf'\1\n<p class="price" data-gen="apify-price:{slug}">{H.escape(text)}</p>',
            body,
            count=1,
            flags=re.S,
        )
        if n != 1:
            warn.append(f"apify card {slug}: could not insert price line")
            return m.group(0)
        return m.group(1) + body2 + m.group(3)

    return CARD_RE.sub(one, html), price_lines


def build_pricing_md(actors, fam, servers, values, shop_line, price_lines):
    today = date.today().isoformat()
    lines = [
        "# Pricing — Panda Federation tools",
        "",
        "> Apify list rates rebuilt from the Apify Store API when this site builds "
        f"({today}). The same sentences appear on the Apify tool cards at "
        f"{SITE}/apify.html. The Store page is authoritative. For tiered events, "
        "the list rate is the Apify free-plan tier; paid Apify plans pay less. "
        "Every run also has Apify's small Actor-start event.",
        "",
        "## Apify Actors",
        "",
    ]
    by = {}
    for a in actors:
        by.setdefault(fam.get(a["name"]), []).append(a)
    for key, label in FAMILY + [(None, "Other")]:
        if not by.get(key):
            continue
        lines.append(f"### {label}")
        lines.append("")
        for a in sorted(by[key], key=lambda x: x["title"].lower()):
            _, rate = pricing(a)
            sentence = price_lines.get(a["name"]) or (_rate_sentence(rate) if rate else "Live price is on the Apify Store listing.")
            lines.append(f"- [{a['title']}](https://apify.com/{OWNER}/{a['name']}): {sentence}")
        lines.append("")
    lines += [
        "## MCP servers",
        "",
        "Installing a Panda Federation MCP server from PyPI is free. The four focused "
        "domain servers call our Apify Actors, so they need your own `APIFY_TOKEN`; "
        "runs bill to your Apify account at the Actor rates above. Quiet File Team MCP "
        "is free, offline, and needs no token.",
        "",
    ]
    for s in servers:
        need = s.get("install", {}).get("requires") or []
        extra = " Needs " + ", ".join(f"`{x}`" for x in need) + "." if need else " No token needed."
        lines.append(f"- {s['name']}: install with `{s['install']['uvx']}`.{extra} {s.get('homepage') or s.get('repo')}")
    lines += [
        "",
        "## Other listings",
        "",
        "Fiverr, Upwork and Agensi package prices stay on those listings. This file does not repeat them.",
        f"- Services: {SITE}/services.html",
        f"- Agensi skills: {SITE}/agensi.html",
        "",
        "## Hardware shop",
        "",
        shop_line,
        "",
    ]
    return "\n".join(lines)


def _md_path(page):
    if os.path.basename(page) == "index.html":
        return os.path.join(os.path.dirname(page), "index.md") if os.path.dirname(page) else "index.md"
    if page.endswith(".html"):
        return page[:-5] + ".md"
    return page + ".md"


class _MD(HTMLParser):
    """Best-effort HTML-to-Markdown of visible page content only."""

    SKIP = {"script", "style", "nav", "footer", "noscript"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.out = []
        self.skip = 0
        self.href = None
        self.li = 0
        self.heading = None

    def handle_starttag(self, tag, attrs):
        if tag in self.SKIP:
            self.skip += 1
            return
        if self.skip:
            return
        attrs = dict(attrs)
        if tag in ("h1", "h2", "h3", "h4"):
            self.heading = "#" * int(tag[1])
            self.out.append(f"\n\n{self.heading} ")
        elif tag == "p":
            self.out.append("\n\n")
        elif tag == "br":
            self.out.append("  \n")
        elif tag == "li":
            self.out.append("\n- ")
            self.li += 1
        elif tag == "a":
            self.href = attrs.get("href")
            self.out.append("[")
        elif tag == "code":
            self.out.append("`")
        elif tag in ("strong", "b"):
            self.out.append("**")
        elif tag in ("em", "i"):
            self.out.append("*")
        elif tag == "pre":
            self.out.append("\n\n```\n")

    def handle_endtag(self, tag):
        if tag in self.SKIP:
            self.skip = max(0, self.skip - 1)
            return
        if self.skip:
            return
        if tag in ("h1", "h2", "h3", "h4"):
            self.heading = None
            self.out.append("\n")
        elif tag == "a":
            href = self.href or ""
            self.out.append(f"]({href})" if href else "]")
            self.href = None
        elif tag == "code":
            self.out.append("`")
        elif tag in ("strong", "b"):
            self.out.append("**")
        elif tag in ("em", "i"):
            self.out.append("*")
        elif tag == "pre":
            self.out.append("\n```\n")
        elif tag in ("ul", "ol", "p"):
            self.out.append("\n")

    def handle_data(self, data):
        if self.skip:
            return
        text = re.sub(r"[ \t]+", " ", data)
        if not text.strip() and "\n" in text:
            return
        self.out.append(text)


def html_to_markdown(raw, url, title):
    s = re.sub(r"<script\b.*?</script>", "", raw, flags=re.S | re.I)
    s = re.sub(r"<style\b.*?</style>", "", s, flags=re.S | re.I)
    body_m = re.search(r"<body\b[^>]*>(.*?)</body>", s, re.S | re.I)
    body = body_m.group(1) if body_m else s
    # Keep the hero (it sits outside <main> on the homepage) and the main column.
    body = re.sub(r"<header\b.*?</header>", "", body, flags=re.S | re.I)
    body = re.sub(r"<footer\b.*?</footer>", "", body, flags=re.S | re.I)
    body = re.sub(r"<canvas\b.*?</canvas>", "", body, flags=re.S | re.I)
    body = re.sub(r'<a class="skip".*?</a>', "", body, flags=re.S | re.I)
    parser = _MD()
    try:
        parser.feed(body)
        parser.close()
    except Exception:  # noqa: BLE001
        text = _text(body)
        return f"# {title}\n\nSource: {url}\n\n{text}\n"
    md = "".join(parser.out)
    md = re.sub(r"\n{3,}", "\n\n", md).strip()
    return f"# {title}\n\nSource: {url}\n\n{md}\n"


def write_markdown_mirrors(read, write, warn, pages):
    changed = []
    parts = ["# Panda Federation — full page markdown", "",
             "Plain-text versions of the public pages, generated from the same HTML people see. "
             f"Index: {SITE}/llms.txt. Pricing: {SITE}/pricing.md.", ""]
    for p in pages:
        if p == "404.html" or "http-equiv=\"refresh\"" in read(p):
            continue
        raw = read(p)
        title_m = re.search(r"<title[^>]*>(.*?)</title>", raw, re.S | re.I)
        title = _text(title_m.group(1)) if title_m else p
        url = f"{SITE}/" + (p[:-len("index.html")] if p.endswith("index.html") else p)
        md = html_to_markdown(raw, url, title)
        dest = _md_path(p)
        if write(dest, md):
            changed.append(dest)
        parts.append(md)
        parts.append("\n---\n")
    if write("llms-full.txt", "\n".join(parts).rstrip() + "\n"):
        changed.append("llms-full.txt")
    return changed


def build_ai_catalog(values, servers):
    return {
        "name": "Panda Federation",
        "description": "Official public-data tools for AI agents: MCP servers, Apify Actors, and local kits.",
        "url": f"{SITE}/",
        "llms_txt": f"{SITE}/llms.txt",
        "llms_full": f"{SITE}/llms-full.txt",
        "pricing": f"{SITE}/pricing.md",
        "sitemap": f"{SITE}/sitemap.xml",
        "webmcp": f"{SITE}/.well-known/webmcp.json",
        "catalog": f"{SITE}/webmcp-catalog.json",
        "shop": SHOP,
        "resources": [
            {"type": "llms.txt", "url": f"{SITE}/llms.txt"},
            {"type": "llms-full.txt", "url": f"{SITE}/llms-full.txt"},
            {"type": "pricing", "url": f"{SITE}/pricing.md"},
            {"type": "sitemap", "url": f"{SITE}/sitemap.xml"},
            {"type": "webmcp", "url": f"{SITE}/.well-known/webmcp.json"},
            {"type": "webmcp-catalog", "url": f"{SITE}/webmcp-catalog.json"},
            {"type": "mcp-registry-search",
             "url": f"https://registry.modelcontextprotocol.io/v0/servers?search=io.github.{OWNER}"},
            {"type": "shop", "url": SHOP, "note": "Hardware shop; inventory is on that site."},
        ] + [
            {"type": "mcp-server", "name": s["name"], "install": s["install"]["uvx"],
             "url": s.get("homepage") or s.get("repo")}
            for s in servers
        ],
    }
