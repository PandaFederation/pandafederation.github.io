"""Agent-facing files, generated so they cannot drift from the site:

- llms.txt: counts, MCP servers (install, PyPI, Registry), every public Apify
  Actor (live from the Apify Store), apps, planned modules, updates (What's New,
  Atom feed, digest), About and Agensi. No prices: live prices stay on stores.
- JSON-LD on every page we own (Organization/WebSite, AboutPage, ItemLists,
  Blog/BlogPosting), plus PyPI/Registry facts on the Quiet File Team MCP page.
- PyPI and Registry fields in the WebMCP catalogs.
- sitemap.xml (runs last, so new digest issues are included on the same build).
"""
import glob
import html as H
import json
import re

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
    L += ["Use WebMCP tools on this site when a browser or scanner exposes document.modelContext (list_servers, list_tools, "
          "search_tools, get_install_command, get_links, list_actors, list_apps, list_editions). Machine-readable catalog: "
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
          f"{len(actors)} public Actors, read live from the Apify Store. {n_ppe} are pay-per-event and {n_free} is free; "
          "live prices are on each Store page, never on this site. Sources are official or public. "
          f"Cards with descriptions: {SITE}/apify.html", ""]
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
            free = " (free)" if models.get(a["name"]) == "FREE" else ""
            L.append(f"- {a['title']}{free}: https://apify.com/{OWNER}/{a['name']}")
        L.append("")

    L += ["## Local-first apps and repos", ""]
    for a in cat.get("apps", []):
        url = a.get("homepage") or a.get("repo")
        L.append(f"- {a['name']}: {a['description']} {url}" + (f" (repo: {a['repo']})" if a.get("homepage") and a.get("repo") else ""))
    planned = cat.get("planned_modules", [])
    if planned:
        L.append("- Planned, not shipped yet: " + ", ".join(f"{p['id'].replace('_', ' ')} ({p['repo']})" for p in planned)
                 + ". Placeholder repos with no code.")
    L += ["", f"More: {SITE}/apps.html. Quiet File Team agent notes: {SITE}/quiet-file-team/llms.txt and "
          f"{SITE}/quiet-file-team-mcp/llms.txt", ""]

    L += ["## Free guides", "",
          f"- Free data broker removal guide + US state law map (not legal advice): {SITE}/data-broker-removal/ — "
          f"agent notes and JSON: {SITE}/data-broker-removal/llms.txt", ""]

    L += ["## Updates", "",
          f"- What's New (changelog from our releases, Registry listings, new Actors and site launches): {SITE}/whats-new/",
          f"- Atom feed: {SITE}/feed.xml",
          f"- Weekly digest (MCP, Apify and public-data news with our take): {SITE}/digest/"]
    if issues:
        i = issues[0]
        L.append(f"- Latest digest: #{i['number']} ({i['date']}), {i.get('title', '')}: {SITE}/digest/{i['slug']}/")
    L.append("")

    L += ["## About", "", f"{about_lede} {SITE}/about.html", "",
          "Free and paid editions of the same tool always name each other and say how to switch. Prices live on the store listing.", ""]
    L += ["## Services and skills", "",
          f"- Services: {SITE}/services.html",
          f"- {values['agensi_skills']} Agensi skills, each linked to its related Apify Actor: {SITE}/agensi.html", ""]
    L += ["## Other entry points", "",
          f"- Apify Store: https://apify.com/{OWNER}",
          f"- Official MCP Registry: https://registry.modelcontextprotocol.io/v0/servers?search=io.github.{OWNER}",
          f"- GitHub: https://github.com/{OWNER}",
          "- X: https://x.com/PandaFedHQ  (Follow on X: @PandaFedHQ)",
          "- Product Hunt: https://www.producthunt.com/products/panda-federation-tools",
          f"- Inventory: {SITE}/inventory.json",
          f"- Sitemap: {SITE}/sitemap.xml",
          f"- Full tool notes: https://{OWNER}.github.io/panda-federation-tools/llms.txt", ""]
    if write("llms.txt", "\n".join(L)):
        changed.append("llms.txt")

    # ---------- JSON-LD
    org = {"@type": "Organization", "@id": f"{SITE}/#org", "name": "Panda Federation", "url": f"{SITE}/",
           "logo": f"{SITE}/assets/logo.png", "description": site_desc, "sameAs": SAME_AS}
    ctx = "https://schema.org"

    def page_ld(p):
        url = f"{SITE}/" + (p[:-len("index.html")] if p.endswith("index.html") else p)
        desc = _meta_desc(read, p)
        if p == "index.html":
            return {"@context": ctx, "@graph": [org, {"@type": "WebSite", "@id": f"{SITE}/#site", "name": "Panda Federation",
                    "url": f"{SITE}/", "description": f"{headline} {site_desc}", "publisher": {"@id": f"{SITE}/#org"}}]}
        if p == "about.html":
            return {"@context": ctx, "@graph": [org, {"@type": "AboutPage", "url": url, "name": "About Panda Federation",
                    "description": about_lede, "about": {"@id": f"{SITE}/#org"}}]}
        if p == "apify.html":
            items = [{"@type": "ListItem", "position": n, "name": a["title"], "url": f"https://apify.com/{OWNER}/{a['name']}"}
                     for n, a in enumerate(sorted(actors, key=lambda x: x["title"].lower()), 1)]
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
            items = [{"@type": "ListItem", "position": n, "name": a["name"], "url": a.get("homepage") or a.get("repo")}
                     for n, a in enumerate(cat.get("apps", []), 1)]
            return {"@context": ctx, "@graph": [org, {"@type": "CollectionPage", "url": url, "name": "Apps & Repos",
                    "description": desc, "mainEntity": {"@type": "ItemList", "numberOfItems": len(items), "itemListElement": items}}]}
        if p == "agensi.html":
            return {"@context": ctx, "@graph": [org, {"@type": "CollectionPage", "url": url, "name": "Agensi skills",
                    "description": desc, "mainEntity": {"@type": "ItemList", "numberOfItems": int(values["agensi_skills"])}}]}
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

    # ---------- sitemap (last step, so it sees pages built by earlier modules)
    urls = []
    for p in pages:
        if p == "404.html" or 'http-equiv="refresh"' in read(p):
            continue
        urls.append(f"{SITE}/" + (p[:-len("index.html")] if p.endswith("index.html") else p))
    urls += [f"{SITE}/feed.xml", f"{SITE}/llms.txt"]
    urls = sorted(set(urls), key=lambda u: (u.count("/"), u))
    sm = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    sm += [f"  <url><loc>{u}</loc></url>" for u in urls]
    sm.append("</urlset>\n")
    if write("sitemap.xml", "\n".join(sm)):
        changed.append("sitemap.xml")
    return changed
