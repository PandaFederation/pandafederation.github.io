"""Site chrome: one nav, one footer link row and the analytics beacon,
applied to every HTML page so they never drift apart."""
import glob
import os
import re

SITE = "https://pandafederation.com"
NAV = [
    ("index.html", "Home"),
    ("mcp.html", "MCP Servers"),
    ("apify.html", "Apify Tools"),
    ("apps.html", "Apps &amp; Repos"),
    ("services.html", "Services"),
    ("data-broker-removal/", "Data Broker Removal"),
    ("whats-new/", "What&#39;s New"),
    ("about.html", "About"),
]
SECTION = {
    "index.html": "index.html", "mcp.html": "mcp.html", "quiet-file-team-mcp/index.html": "mcp.html",
    "apify.html": "apify.html", "apps.html": "apps.html", "quiet-file-team/index.html": "apps.html",
    "services.html": "services.html", "agensi.html": "services.html",
    "data-broker-removal/index.html": "data-broker-removal/", "whats-new/index.html": "whats-new/",
    "about.html": "about.html",
}
FOOT_LINKS = [
    ("https://github.com/pandadad0214", "GitHub"),
    ("https://x.com/PandaFedHQ", "Follow on X: @PandaFedHQ"),
    ("https://apify.com/pandadad0214", "Apify Store"),
    ("whats-new/", "What&#39;s New"),
    ("feed.xml", "Atom feed"),
    ("books.html", "Books"),
    ("about.html", "About / contact"),
]
BEACON_TOKEN = "4c08ba2f90764497865713996270e0e5"  # Cloudflare Web Analytics site token (public, cookie-free); empty = off
SKIP = ("node_modules/", ".git/")


def _prefix(path):
    depth = path.count("/")
    return "../" * depth


def _section(path):
    if path.startswith("digest/"):
        return "whats-new/"
    return SECTION.get(path)


def run(get, read, write, warn, values, actors):
    changed = []
    pages = sorted(p for p in glob.glob("**/*.html", recursive=True) if not p.startswith(SKIP))
    for p in pages:
        s = read(p)
        pre = _prefix(p)
        cur = _section(p)
        links = "".join(
            f'<a href="{pre}{href}"{" aria-current=\"page\"" if href == cur else ""}>{label}</a>' for href, label in NAV
        )
        s2 = re.sub(r'<nav class="tabs" aria-label="Primary">.*?</nav>',
                    lambda m: f'<nav class="tabs" aria-label="Primary">{links}</nav>', s, count=1, flags=re.S)
        foot = " ·\n      ".join(
            f'<a href="{h if h.startswith("http") else pre + h}">{t}</a>' for h, t in FOOT_LINKS
        )
        s2 = re.sub(r'(<div class="foot-inner">\s*<div>.*?</div>\s*<div>)(.*?)(</div>)',
                    lambda m: m.group(1) + "\n      " + foot + "\n    " + m.group(3), s2, count=1, flags=re.S)
        s2 = re.sub(r"\n?<!-- cf-beacon -->.*?<!-- /cf-beacon -->", "", s2, flags=re.S)
        if BEACON_TOKEN and "</body>" in s2:
            beacon = ('<!-- cf-beacon --><script defer src="https://static.cloudflareinsights.com/beacon.min.js" '
                      f"data-cf-beacon='{{\"token\": \"{BEACON_TOKEN}\"}}'></script><!-- /cf-beacon -->")
            s2 = s2.replace("</body>", beacon + "\n</body>", 1)
        if write(p, s2):
            changed.append(p)

    # sitemap.xml is written by scripts/agents.py (last build step)
    return changed
