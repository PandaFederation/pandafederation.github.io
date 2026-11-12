#!/usr/bin/env python3
"""Rebuild the generated parts of pandafederation.com from live public data.

Sources (all public, no secrets):
  - Apify Store API: public Actors by pandadad0214
  - GitHub: panda-federation-tools domains.py (tool counts per focused server)
  - PyPI JSON API: latest version of each Python package
  - Official MCP Registry: which servers are listed
Generated values live in <span data-gen="KEY">VALUE</span> markers inside the HTML
files, plus the "counts" blocks of webmcp-catalog.json and inventory.json.
Run from the repo root:  python3 scripts/build.py
"""
from __future__ import annotations

import glob
import json
import os
import re
import sys
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
OWNER = "pandadad0214"
UA = {"User-Agent": "pandafederation-site-build"}
WARN: list[str] = []


def get(url: str, *, raw: bool = False, headers: dict | None = None):
    h = dict(UA)
    if headers:
        h.update(headers)
    tok = os.environ.get("GITHUB_TOKEN")
    if tok and "api.github.com" in url:
        h["Authorization"] = f"Bearer {tok}"
    req = urllib.request.Request(url, headers=h)
    with urllib.request.urlopen(req, timeout=60) as r:
        data = r.read().decode("utf-8")
    return data if raw else json.loads(data)


def read(p: str) -> str:
    with open(p, encoding="utf-8") as f:
        return f.read()


def write(p: str, s: str) -> bool:
    if os.path.exists(p) and read(p) == s:
        return False
    os.makedirs(os.path.dirname(p) or ".", exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        f.write(s)
    return True


# ---------------------------------------------------------------- data
def apify_actors() -> list[dict]:
    d = get(f"https://api.apify.com/v2/store?username={OWNER}&limit=200")["data"]
    items = [i for i in d["items"] if i.get("username") == OWNER]
    if len(items) != d.get("total", len(items)):
        WARN.append(f"Apify store total {d.get('total')} != items {len(items)}")
    return items


def domain_tool_counts() -> dict[str, int]:
    src = get(
        f"https://raw.githubusercontent.com/{OWNER}/panda-federation-tools/main/src/panda_federation_tools/domains.py",
        raw=True,
    )
    block = src.split("DOMAINS:", 1)[1].split("\n}\n", 1)[0]
    counts: dict[str, int] = {}
    for m in re.finditer(r'"([a-z-]+)":\s*frozenset\(\s*\{(.*?)\}\s*\)', block, re.S):
        counts[m.group(1)] = len(re.findall(r'"[a-z0-9_]+"', m.group(2)))
    if set(counts) != {"research", "public-funding", "leads", "web-security"}:
        raise SystemExit(f"Unexpected domains parsed: {counts}")
    counts["total"] = sum(counts.values())
    return counts


def pypi_version(pkg: str) -> str | None:
    try:
        return get(f"https://pypi.org/pypi/{pkg}/json")["info"]["version"]
    except Exception as e:  # noqa: BLE001
        WARN.append(f"PyPI lookup failed for {pkg}: {e}")
        return None


def registry_names() -> set[str]:
    names: set[str] = set()
    try:
        d = get(f"https://registry.modelcontextprotocol.io/v0/servers?search=io.github.{OWNER}&limit=100")
        for s in d.get("servers", []):
            names.add(s["server"]["name"])
    except Exception as e:  # noqa: BLE001
        WARN.append(f"MCP Registry lookup failed: {e}")
    return names


# ---------------------------------------------------------------- apply
GEN_RE = re.compile(r'(<span data-gen="([^"]+)">)(.*?)(</span>)', re.S)


def html_files() -> list[str]:
    return sorted(f for f in glob.glob("**/*.html", recursive=True) if not f.startswith((".git", "node_modules")))


def count_cards(path: str, needle: str = '<article class="card"') -> int:
    return read(path).count(needle) if os.path.exists(path) else 0


def main() -> int:
    actors = apify_actors()
    tools = domain_tool_counts()
    catalog = json.loads(read("webmcp-catalog.json"))
    reg = registry_names()

    pkgs = {"panda-research-tools", "panda-public-funding-tools", "panda-leads-tools",
            "panda-web-security-tools", "panda-federation-tools", "quiet-file-team-mcp"}
    for f in html_files():
        pkgs |= {m.group(2).split(":", 1)[1] for m in GEN_RE.finditer(read(f)) if m.group(2).startswith("pypi:")}
    versions = {p: pypi_version(p) for p in sorted(pkgs)}

    agensi_page = "agensi.html" if os.path.exists("agensi.html") else "services.html"
    values: dict[str, str] = {
        "apify_actors": str(len(actors)),
        "mcp_servers": str(len(catalog.get("servers", []))),
        "apps": str(len(catalog.get("apps", []))),
        "agensi_skills": str(count_cards(agensi_page, 'skill</span>')),
    }
    for k, v in tools.items():
        values[f"tools:{k}"] = str(v)
    for n in reg:
        values[f"registry:{n.split('/', 1)[1]}"] = "listed"
    for p, v in versions.items():
        if v:
            values[f"pypi:{p}"] = v

    # Store coverage: every public Actor must have a card on apify.html
    apify_html = read("apify.html")
    linked = set(re.findall(rf"apify\.com/{OWNER}/([a-z0-9-]+)", apify_html))
    for a in actors:
        if a["name"] not in linked:
            WARN.append(f"Public Actor missing from apify.html: {a['name']}")
    for name in ("panda-research-tools", "panda-public-funding-tools", "panda-leads-tools",
                 "panda-web-security-tools", "quiet-file-team-mcp"):
        if reg and f"io.github.{OWNER}/{name}" not in reg:
            WARN.append(f"Not found on the Official MCP Registry: {name}")

    changed = []
    for f in html_files():
        s = read(f)

        def rep(m: re.Match) -> str:
            key = m.group(2)
            if key in values:
                return m.group(1) + values[key] + m.group(4)
            WARN.append(f"{f}: unknown data-gen key {key}")
            return m.group(0)

        if write(f, GEN_RE.sub(rep, s)):
            changed.append(f)

    # JSON count blocks
    c = catalog.setdefault("counts", {})
    c.update({
        "apify_actors_public": len(actors),
        "apps_and_repos": len(catalog.get("apps", [])),
        "focused_tools": tools["total"],
        "research": tools["research"],
        "public_funding": tools["public-funding"],
        "leads": tools["leads"],
        "web_security": tools["web-security"],
    })
    for s in catalog.get("servers", []):
        key = {"panda-research-tools": "research", "panda-public-funding-tools": "public-funding",
               "panda-leads-tools": "leads", "panda-web-security-tools": "web-security"}.get(s.get("id"))
        if key:
            s["tool_count"] = tools[key]
    if write("webmcp-catalog.json", json.dumps(catalog, indent=2, ensure_ascii=False) + "\n"):
        changed.append("webmcp-catalog.json")
    inv = json.loads(read("inventory.json"))
    inv.setdefault("counts", {}).update({
        "apify_actors_public": len(actors),
        "mcp_servers": len(catalog.get("servers", [])),
        "apps_and_repos": len(catalog.get("apps", [])),
        "agensi_skills_live": int(values["agensi_skills"]),
    })
    if write("inventory.json", json.dumps(inv, indent=2, ensure_ascii=False) + "\n"):
        changed.append("inventory.json")

    # extra build steps (changelog, digest, chrome) live in sibling modules
    for mod in ("chrome", "samples", "changelog", "digest", "agents"):
        path = os.path.join(ROOT, "scripts", f"{mod}.py")
        if os.path.exists(path):
            ns: dict = {"__file__": path, "__name__": f"build_{mod}"}
            exec(compile(read(path), path, "exec"), ns)  # noqa: S102
            changed += ns["run"](get=get, read=read, write=write, warn=WARN, values=values, actors=actors)

    print("values:", json.dumps(values, sort_keys=True))
    print("changed:", ", ".join(changed) or "nothing")
    for w in WARN:
        print("WARN:", w)
    return 0


if __name__ == "__main__":
    sys.exit(main())
