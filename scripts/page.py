"""Shared page shell for generated pages (copies the header/footer from about.html)."""
import html
import re


def _prefix_links(fragment: str, prefix: str) -> str:
    if not prefix:
        return fragment

    def fix(m):
        url = m.group(2)
        if re.match(r"^(https?:|mailto:|#|/)", url):
            return m.group(0)
        return f'{m.group(1)}="{prefix}{url}"'

    return re.sub(r'(href|src)="([^"]*)"', fix, fragment)


def shell(read, *, title, description, canonical, prefix, body, current=None, extra_head=""):
    about = read("about.html")
    header = about[about.index('<header class="nav">'):about.index("</header>") + 9]
    header = header.replace(' aria-current="page"', "")
    if current:
        header = header.replace(f'<a href="{current}">', f'<a href="{current}" aria-current="page">', 1)
    footer = about[about.index('<footer class="site">'):about.index("</footer>") + 9]
    tail = about[about.index("</footer>") + 9:about.index("</body>")]
    # Keep the read-only WebMCP helper on generated pages too (standard: every
    # public page ships WebMCP). Its catalog path is page-relative, so prefix it.
    tail = tail.replace('data-webmcp-catalog="webmcp-catalog.json"',
                        f'data-webmcp-catalog="{prefix}webmcp-catalog.json"')
    t = html.escape(title)
    d = html.escape(description)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{t} · Panda Federation</title>
<meta name="description" content="{d}">
<link rel="canonical" href="{canonical}">
<meta name="theme-color" content="#0f1420">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Panda Federation">
<meta property="og:title" content="{t} · Panda Federation">
<meta property="og:description" content="{d}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="https://pandafederation.com/assets/og.png">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:site" content="@PandaFedHQ">
<meta name="twitter:title" content="{t} · Panda Federation">
<meta name="twitter:description" content="{d}">
<meta name="twitter:image" content="https://pandafederation.com/assets/og.png">
<link rel="icon" type="image/png" href="{prefix}assets/favicon.png">
<link rel="apple-touch-icon" href="{prefix}assets/apple-touch-icon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{prefix}css/site.css">
<link rel="alternate" type="application/atom+xml" title="Panda Federation: What's New" href="https://pandafederation.com/feed.xml">
{extra_head}</head>
<body>
<a class="skip" href="#main">Skip to content</a>
{_prefix_links(header, prefix)}
<main id="main" class="wrap">
{body}
</main>
{_prefix_links(footer, prefix)}
{_prefix_links(tail.strip(), prefix)}
</body>
</html>
"""


def md_to_prose(src: str) -> str:
    """Convert the site's simple pricing.md (headings, lists, links, quotes) to HTML."""
    def inline(s: str) -> str:
        parts = []
        i = 0
        tok = re.compile(
            r"\[([^\]]+)\]\(([^)]+)\)|\*\*(.+?)\*\*|`([^`]+)`|(https?://[^\s<]+)"
        )
        for m in tok.finditer(s):
            if m.start() > i:
                parts.append(html.escape(s[i:m.start()]))
            if m.group(1) is not None:
                parts.append(
                    f'<a href="{html.escape(m.group(2), quote=True)}">{html.escape(m.group(1))}</a>'
                )
            elif m.group(3) is not None:
                parts.append(f"<strong>{html.escape(m.group(3))}</strong>")
            elif m.group(4) is not None:
                parts.append(f"<code>{html.escape(m.group(4))}</code>")
            else:
                url = m.group(5).rstrip(".,;:)")
                parts.append(f'<a href="{html.escape(url, quote=True)}">{html.escape(url)}</a>')
                # if we stripped trailing punctuation, put it back after the link
                extra = m.group(5)[len(url):]
                if extra:
                    parts.append(html.escape(extra))
            i = m.end()
        if i < len(s):
            parts.append(html.escape(s[i:]))
        return "".join(parts)

    lines = src.splitlines()
    out = []
    i = 0
    n = len(lines)
    while i < n:
        line = lines[i]
        if line.strip() == "":
            i += 1
            continue
        if line.startswith("> "):
            qs = [line[2:]]
            i += 1
            while i < n and lines[i].startswith("> "):
                qs.append(lines[i][2:])
                i += 1
            out.append("<blockquote><p>" + inline(" ".join(qs)) + "</p></blockquote>")
            continue
        hm = re.match(r"^(#{1,3})\s+(.*)$", line)
        if hm:
            level = len(hm.group(1))
            out.append(f"<h{level}>{inline(hm.group(2))}</h{level}>")
            i += 1
            continue
        if line.startswith("- "):
            items = []
            while i < n and lines[i].startswith("- "):
                items.append("<li>" + inline(lines[i][2:]) + "</li>")
                i += 1
            out.append("<ul>\n" + "\n".join(items) + "\n</ul>")
            continue
        para = [line]
        i += 1
        while i < n and lines[i].strip() and not lines[i].startswith(("#", "- ", "> ")):
            para.append(lines[i])
            i += 1
        out.append("<p>" + inline(" ".join(para)) + "</p>")
    return "\n".join(out)


def write_pricing_html(read, write) -> bool:
    """Rebuild pricing.html from pricing.md so the HTML page cannot go stale."""
    body = "  <article class=\"prose\">\n" + md_to_prose(read("pricing.md")) + "\n  </article>\n"
    extra = (
        "<!-- agent-discovery -->\n"
        "<link rel=\"alternate\" type=\"text/plain\" href=\"llms.txt\" title=\"llms.txt\">\n"
        "<link rel=\"describedby\" href=\"llms.txt\">\n"
        "<link rel=\"alternate\" type=\"text/markdown\" href=\"pricing.md\">\n"
        "<link rel=\"ai-catalog\" href=\".well-known/ai-catalog.json\" type=\"application/ai-catalog+json\">\n"
        "<!-- /agent-discovery -->\n"
    )
    page = shell(
        read,
        title="Pricing",
        description=(
            "List rates for Panda Federation Apify Actors, MCP servers, and other listings, "
            "rebuilt from the Apify Store API. The Store page is authoritative."
        ),
        canonical="https://pandafederation.com/pricing.html",
        prefix="",
        body=body,
        extra_head=extra,
    )
    beacon = (
        "<!-- cf-beacon --><script defer src=\"https://static.cloudflareinsights.com/beacon.min.js\" "
        "data-cf-beacon='{\"token\": \"4c08ba2f90764497865713996270e0e5\"}'></script><!-- /cf-beacon -->\n"
    )
    if "cf-beacon" not in page and "</body>" in page:
        page = page.replace("</body>", beacon + "</body>", 1)
    return write("pricing.html", page)
