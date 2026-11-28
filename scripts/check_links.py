#!/usr/bin/env python3
"""Weekly link and sitemap check (no third-party packages).

Fails (exit 1) when:
- an internal href/src points at a file that does not exist,
- a sitemap.xml URL on our own domain does not answer 200,
- an external link on a "stable" host (GitHub, PyPI, Apify, our own domains) answers 404/410/5xx.

Hosts that block bots (403/429: Fiverr, Upwork, Product Hunt, AlternativeTo, data-broker opt-out pages,
fonts, startup directories) are skipped on purpose; they are real pages that refuse scripts.
"""
import glob
import os
import re
import sys
import urllib.request
import urllib.error
from concurrent.futures import ThreadPoolExecutor

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
STABLE = ("github.com", "pypi.org", "apify.com", "docs.apify.com", "pandafederation.com",
          "pandadad0214.github.io", "registry.modelcontextprotocol.io", "glama.ai")
UA = {"User-Agent": "Mozilla/5.0 (pandafederation link check)"}


def fetch(url):
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=25) as r:
            return r.status
    except urllib.error.HTTPError as e:
        return e.code
    except Exception as e:  # network trouble is not a broken link
        return f"skip:{type(e).__name__}"


def main():
    problems, ext = [], {}
    for f in glob.glob("**/*.html", recursive=True):
        s = open(f, encoding="utf-8", errors="ignore").read()
        for m in re.finditer(r'(?:href|src)="([^"#]+)', s):
            u = m.group(1)
            if u.startswith(("mailto:", "javascript:", "data:", "tel:", "//")):
                continue
            if u.startswith("http"):
                ext.setdefault(u, f)
                continue
            p = u.split("?")[0]
            path = p.lstrip("/") if p.startswith("/") else os.path.normpath(os.path.join(os.path.dirname(f), p))
            if p == "/" or path in ("", "."):
                continue
            if os.path.isdir(path):
                path = os.path.join(path, "index.html")
            if not (os.path.exists(path) or os.path.exists(path + ".html")):
                problems.append(f"{f}: missing internal target {u}")
    sitemap = re.findall(r"<loc>([^<]+)", open("sitemap.xml", encoding="utf-8").read())
    targets = [(u, "sitemap.xml") for u in sitemap]
    for u, f in ext.items():
        host = re.sub(r"^https?://([^/:]+).*", r"\1", u).lower()
        if any(host == h or host.endswith("." + h) for h in STABLE):
            targets.append((u, f))
    with ThreadPoolExecutor(10) as ex:
        codes = list(ex.map(lambda t: fetch(t[0]), targets))
    for (u, f), c in zip(targets, codes):
        if isinstance(c, int) and (c in (404, 410) or c >= 500):
            problems.append(f"{f}: {u} answered {c}")
    print(f"checked {len(targets)} URLs and internal links; {len(problems)} problem(s)")
    for p in problems:
        print("PROBLEM:", p)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
