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
    tail = re.sub(r'<script src="js/panda-webmcp\.js"[^>]*></script>\s*', "", tail)
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
