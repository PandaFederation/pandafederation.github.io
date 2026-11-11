"""What's New: a changelog generated from our own releases, plus an Atom feed.

Sources: GitHub releases of public pandadad0214 repos, Official MCP Registry
publish dates, Apify Actor creation dates for public Actors, and
data/changelog-site.json for site launches. Output: whats-new/index.html, feed.xml.
"""
import datetime as dt
import hashlib
import html
import json
import os

OWNER = "pandadad0214"
SITE = "https://pandafederation.com"
DAYS = 75


def _load_page(path):
    ns = {"__file__": path}
    with open(path, encoding="utf-8") as f:
        exec(compile(f.read(), path, "exec"), ns)  # noqa: S102
    return ns["shell"]


def _t(s, n=160):
    s = (s or "").strip()
    return s if len(s) <= n else s[: n - 1].rsplit(" ", 1)[0].rstrip(",;:") + "…"


def run(get, read, write, warn, values, actors):
    shell = _load_page(os.path.join(os.path.dirname(os.path.abspath(__file__)), "page.py"))
    now = dt.datetime.now(dt.timezone.utc)
    since = now - dt.timedelta(days=DAYS)
    items = []
    seen = set()

    # GitHub releases
    try:
        repos = get(f"https://api.github.com/users/{OWNER}/repos?per_page=100&type=owner&sort=pushed")
        for r in repos:
            if r.get("private") or r.get("fork") or r.get("archived"):
                continue
            try:
                rels = get(f"https://api.github.com/repos/{OWNER}/{r['name']}/releases?per_page=20")
            except Exception as e:  # noqa: BLE001
                warn.append(f"releases {r['name']}: {e}")
                continue
            for rel in rels:
                if rel.get("draft") or rel.get("prerelease") or not rel.get("published_at"):
                    continue
                when = dt.datetime.fromisoformat(rel["published_at"].replace("Z", "+00:00"))
                if when < since:
                    continue
                tag = rel.get("tag_name") or ""
                seen.add((r["name"].lower(), tag.lstrip("v")))
                items.append({
                    "when": when, "kind": "release",
                    "title": f"{r['name']} {tag}",
                    "url": rel["html_url"],
                    "note": _t(r.get("description")),
                })
    except Exception as e:  # noqa: BLE001
        warn.append(f"GitHub releases skipped: {e}")

    # Official MCP Registry
    try:
        d = get(f"https://registry.modelcontextprotocol.io/v0/servers?search=io.github.{OWNER}&limit=100")
        for s in d.get("servers", []):
            srv = s["server"]
            meta = s.get("_meta", {}).get("io.modelcontextprotocol.registry/official", {})
            if not meta.get("publishedAt"):
                continue
            when = dt.datetime.fromisoformat(meta["publishedAt"].replace("Z", "+00:00"))
            short = srv["name"].split("/", 1)[1]
            if when < since or (short.lower(), srv.get("version", "")) in seen:
                continue
            items.append({
                "when": when, "kind": "registry",
                "title": f"{srv.get('title') or short} {srv.get('version', '')} on the Official MCP Registry",
                "url": f"https://registry.modelcontextprotocol.io/v0/servers?search={srv['name']}",
                "note": _t(srv.get("description")),
            })
    except Exception as e:  # noqa: BLE001
        warn.append(f"MCP Registry skipped: {e}")

    # New public Apify Actors
    for a in actors:
        try:
            act = get(f"https://api.apify.com/v2/acts/{OWNER}~{a['name']}")["data"]
        except Exception as e:  # noqa: BLE001
            warn.append(f"Apify actor {a['name']}: {e}")
            continue
        if not act.get("isPublic") or not act.get("createdAt"):
            continue
        when = dt.datetime.fromisoformat(act["createdAt"].replace("Z", "+00:00"))
        if when < since:
            continue
        items.append({
            "when": when, "kind": "actor",
            "title": f"New Apify Actor: {a.get('title') or a['name']}",
            "url": f"https://apify.com/{OWNER}/{a['name']}",
            "note": _t(a.get("description")),
        })

    # Site launches (hand-kept, dated from the site repo history)
    for e in json.loads(read("data/changelog-site.json")):
        when = dt.datetime.fromisoformat(e["date"] + "T19:00:00+00:00")
        items.append({"when": when, "kind": e["kind"], "title": e["title"], "url": e["url"], "note": e.get("note", "")})

    items.sort(key=lambda x: (x["when"], x["title"]), reverse=True)
    if not items:
        warn.append("What's New: no items; leaving pages unchanged")
        return []

    # ---- HTML
    label = {"release": "Release", "registry": "MCP Registry", "actor": "Apify", "site": "Site", "guide": "Guide"}
    rows = []
    for it in items:
        day = it["when"].astimezone(dt.timezone(dt.timedelta(hours=-7))).date().isoformat()
        note = f' — {html.escape(it["note"])}' if it["note"] else ""
        rows.append(
            f'<li><time datetime="{day}">{day}</time> <span class="kind">{label.get(it["kind"], it["kind"])}</span>'
            f'<a href="{html.escape(it["url"])}" rel="noopener">{html.escape(it["title"])}</a>{note}</li>'
        )
    body = f"""<header class="page-head">
    <p class="kicker">What's New</p>
    <h1>Everything we shipped, newest first.</h1>
    <p>Built automatically from our GitHub releases, Official MCP Registry listings, new public Apify Actors and site launches over the last {DAYS} days. Follow it in any feed reader: <a href="../feed.xml">Atom feed</a>.</p>
    <p class="note">Weekly notes on MCP, Apify and public-data sources live in the <a href="../digest/">digest</a>.</p>
  </header>
  <ul class="changelog">
{chr(10).join(rows)}
  </ul>
  <p class="note">{len(items)} entries. Rebuilt {now.astimezone(dt.timezone(dt.timedelta(hours=-7))).strftime('%Y-%m-%d')} (Arizona time).</p>"""
    page = shell(read, title="What's New", description="Changelog of Panda Federation releases: new Apify Actors, MCP server versions, registry listings and site launches.",
                 canonical=f"{SITE}/whats-new/", prefix="../", body=body, current="whats-new/")
    changed = []
    if write("whats-new/index.html", page):
        changed.append("whats-new/index.html")

    # ---- Atom
    def esc(s):
        return html.escape(s, quote=True)
    entries = []
    for it in items[:50]:
        iso = it["when"].astimezone(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        entries.append(f"""  <entry>
    <title>{esc(it['title'])}</title>
    <link href="{esc(it['url'])}"/>
    <id>tag:pandafederation.com,2026:{hashlib.sha1((it['kind'] + it['url'] + it['title']).encode()).hexdigest()}</id>
    <updated>{iso}</updated>
    <summary>{esc(it['note'] or it['title'])}</summary>
  </entry>""")
    updated = items[0]["when"].astimezone(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    feed = f"""<?xml version="1.0" encoding="utf-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <title>Panda Federation: What's New</title>
  <subtitle>Releases, new Apify Actors, MCP Registry listings and site launches.</subtitle>
  <link href="{SITE}/feed.xml" rel="self"/>
  <link href="{SITE}/whats-new/"/>
  <id>{SITE}/whats-new/</id>
  <updated>{updated}</updated>
  <author><name>Panda Federation</name><uri>{SITE}/</uri></author>
{chr(10).join(entries)}
</feed>
"""
    if write("feed.xml", feed):
        changed.append("feed.xml")
    return changed
