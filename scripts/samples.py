"""Render data/samples.json (trimmed rows from real Actor runs) into index.html."""
import html
import json
import re

START, END = "<!-- gen:samples -->", "<!-- /gen:samples -->"


def run(get, read, write, warn, values, actors):
    samples = json.loads(read("data/samples.json"))
    public = {a["name"] for a in actors}
    parts = []
    for s in samples:
        slug = s["actor"].rstrip("/").rsplit("/", 1)[-1]
        if slug not in public:
            warn.append(f"Sample {s['id']} links an Actor that is not public: {slug}")
        head = "".join(f"<th scope=\"col\">{html.escape(c)}</th>" for c in s["columns"])
        body = []
        for i, r in enumerate(s["rows"]):
            cells = []
            for j, c in enumerate(r):
                txt = html.escape("" if c is None else str(c))
                if j == 2 and s.get("links"):
                    txt = f'<a href="{html.escape(s["links"][i])}" rel="noopener">{txt}</a>'
                cells.append(f"<td>{txt}</td>")
            body.append("<tr>" + "".join(cells) + "</tr>")
        parts.append(
            f'<article class="card sample"><h3>{html.escape(s["title"])}</h3>'
            f'<div class="table-wrap"><table><thead><tr>{head}</tr></thead><tbody>{"".join(body)}</tbody></table></div>'
            f'<p class="note">{html.escape(s["source"])}</p>'
            f'<div class="links"><a href="{html.escape(s["actor"])}" rel="noopener">Open on Apify Store</a></div></article>'
        )
    block = START + "\n" + "\n".join(parts) + "\n" + END
    s = read("index.html")
    if START not in s:
        return []
    s2 = re.sub(re.escape(START) + r".*?" + re.escape(END), lambda m: block, s, flags=re.S)
    return ["index.html"] if write("index.html", s2) else []
