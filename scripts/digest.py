"""Weekly digest: digest/issues/NNNN-YYYY-MM-DD.md -> digest/<slug>/index.html.

Each issue starts with a front-matter block:
---
number: 1
date: 2026-11-16
title: This week in public-data agents
status: draft        # only "published" issues are rendered and linked
---
Body is simple Markdown: "## " headings, paragraphs, "- " bullets, [text](url) links.
Drafts are never rendered, so a draft can sit in a branch or a local folder safely.
"""
import glob
import html
import os
import re

SITE = "https://pandafederation.com"


def _load_page(path):
    ns = {"__file__": path}
    with open(path, encoding="utf-8") as f:
        exec(compile(f.read(), path, "exec"), ns)  # noqa: S102
    return ns["shell"]


def parse(text):
    m = re.match(r"---\n(.*?)\n---\n(.*)", text, re.S)
    if not m:
        return None, text
    meta = {}
    for line in m.group(1).splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            meta[k.strip()] = v.split("#", 1)[0].strip()
    return meta, m.group(2)


def inline(s):
    s = html.escape(s)
    s = re.sub(r"\[([^\]]+)\]\((https?://[^)\s]+)\)", r'<a href="\2" rel="noopener">\1</a>', s)
    s = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", s)
    return s


def md(body):
    out, para, items = [], [], []

    def flush():
        if para:
            out.append("<p>" + inline(" ".join(para)) + "</p>")
            para.clear()
        if items:
            out.append("<ul>" + "".join(f"<li>{inline(i)}</li>" for i in items) + "</ul>")
            items.clear()

    for line in body.splitlines():
        if line.startswith("## "):
            flush(); out.append(f"<h2>{inline(line[3:])}</h2>")
        elif line.startswith("- "):
            if para:
                flush()
            items.append(line[2:])
        elif not line.strip():
            flush()
        else:
            para.append(line.strip())
    flush()
    return "\n".join(out)


def run(get, read, write, warn, values, actors):
    shell = _load_page(os.path.join(os.path.dirname(os.path.abspath(__file__)), "page.py"))
    published = []
    for p in sorted(glob.glob("digest/issues/*.md")):
        meta, body = parse(read(p))
        if not meta or meta.get("status") != "published":
            continue
        slug = f"{int(meta['number']):03d}-{meta['date']}"
        published.append((meta, slug))
        page = shell(read, title=f"Digest #{meta['number']}: {meta.get('title', '')}",
                     description=f"Panda Federation weekly digest #{meta['number']}, {meta['date']}: MCP, Apify and public-data news with our take.",
                     canonical=f"{SITE}/digest/{slug}/", prefix="../../", current="whats-new/",
                     body=f'<article class="prose"><p class="kicker">Digest #{html.escape(meta["number"])} · <time datetime="{meta["date"]}">{meta["date"]}</time></p>'
                          f'<h1>{html.escape(meta.get("title", ""))}</h1>{md(body)}'
                          f'<p class="note"><a href="../">All issues</a> · <a href="../../whats-new/">What\'s New</a></p></article>')
        write(f"digest/{slug}/index.html", page)
    published.sort(key=lambda x: x[0]["date"], reverse=True)
    if published:
        lis = "".join(f'<li><time datetime="{m["date"]}">{m["date"]}</time> <a href="{s}/">#{html.escape(m["number"])}: {html.escape(m.get("title", ""))}</a></li>' for m, s in published)
        listing = f'<ul class="changelog">{lis}</ul>'
    else:
        listing = '<p class="note">The first issue is in review. Until then, everything we ship shows up on <a href="../whats-new/">What\'s New</a> and in the <a href="../feed.xml">Atom feed</a>.</p>'
    body = f"""<header class="page-head">
    <p class="kicker">Weekly digest</p>
    <h1>This week in public-data agents.</h1>
    <p>A short weekly read: three to six dated items on MCP, Apify and official public-data sources, each with our own take and a link to the source, plus what we shipped.</p>
  </header>
  {listing}"""
    page = shell(read, title="Weekly digest", description="Panda Federation weekly digest: MCP, Apify and public-data source news with our own take.",
                 canonical=f"{SITE}/digest/", prefix="../", body=body, current="whats-new/")
    return ["digest/index.html"] if write("digest/index.html", page) else []
