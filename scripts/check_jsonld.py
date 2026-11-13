#!/usr/bin/env python3
"""Fail the official-site build when catalog JSON-LD is missing, invalid, or disagrees with visible text.

Run from the repo root after scripts/agents.py has written JSON-LD:

    python3 scripts/check_jsonld.py

Used by scripts/build.py and by the Rebuild generated site data workflow
(CI and the daily build). Exit status is 1 when any error is found.
"""
from __future__ import annotations

import glob
import json
import os
import re
import sys

LD_RE = re.compile(r'<script type="application/ld\+json">(.*?)</script>', re.S)
CARD_RE = re.compile(r'<article class="card"[^>]*>(.*?)</article>', re.S)
SKIP_PREFIX = ("node_modules/", ".git/")
OWN_LD = (
    "data-broker-removal/index.html",
    "quiet-file-team/index.html",
    "quiet-file-team-mcp/index.html",
)
# Pages that must always carry ItemList or SoftwareApplication schema.
CATALOG_PAGES = {
    "index.html",
    "apify.html",
    "mcp.html",
    "apps.html",
    "agensi.html",
    "books.html",
    "services.html",
}
TOOL_CATALOGS = {"apify.html", "mcp.html", "apps.html", "agensi.html"}
SKIP_AUTO_CATALOG = set(OWN_LD) | {"404.html"}


def _plain(frag: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", frag or "")).strip()


def _iter_nodes(obj):
    if isinstance(obj, dict):
        yield obj
        for v in obj.values():
            yield from _iter_nodes(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from _iter_nodes(v)


def _types(node: dict) -> set[str]:
    t = node.get("@type")
    if t is None:
        return set()
    if isinstance(t, list):
        return {str(x) for x in t}
    return {str(t)}


def _price_appears(text: str, price: str) -> bool:
    pat = r"(?<![\d.])" + re.escape(price) + r"(?![\d.])"
    return re.search(pat, text) is not None


def _offer_prices(node: dict) -> list[str]:
    """Prices the visible card is expected to show.

    Offer.price and per-event UnitPriceSpecification prices must appear on
    the card. Apify "Actor Start" platform fees are stored on the offer for
    completeness but are intentionally omitted from the visible list-rate
    sentence, so they are not checked against the card.
    """
    out = []
    for n in _iter_nodes(node):
        types = _types(n)
        if "UnitPriceSpecification" in types and "price" in n:
            unit = str(n.get("unitText") or "")
            if re.search(r"actor\s*start", unit, re.I):
                continue
            out.append(str(n["price"]))
        elif "Offer" in types and "price" in n:
            out.append(str(n["price"]))
    return out


def _has_itemlist_or_software(blocks: list) -> bool:
    for b in blocks:
        for n in _iter_nodes(b):
            if _types(n) & {"ItemList", "SoftwareApplication"}:
                return True
    return False


def _card_for_app(html: str, app: dict) -> str | None:
    url = app.get("url") or ""
    name = app.get("name") or ""
    for body in CARD_RE.findall(html):
        if url and url in body:
            return body
        if name and name in _plain(body):
            return body
    return None


def _is_catalog_page(path: str, html: str) -> bool:
    if path in SKIP_AUTO_CATALOG or path.startswith("digest/") or path.startswith("whats-new/"):
        return False
    if path in CATALOG_PAGES:
        return True
    if 'http-equiv="refresh"' in html:
        return False
    return len(CARD_RE.findall(html)) >= 2


def check(root: str) -> list[str]:
    errors: list[str] = []
    os.chdir(root)
    pricing_md = ""
    if os.path.exists("pricing.md"):
        with open("pricing.md", encoding="utf-8") as f:
            pricing_md = f.read()

    pages = sorted(
        p for p in glob.glob("**/*.html", recursive=True)
        if not p.startswith(SKIP_PREFIX)
    )
    for path in pages:
        with open(path, encoding="utf-8") as f:
            html = f.read()
        if 'http-equiv="refresh"' in html:
            continue

        blocks = []
        for i, m in enumerate(LD_RE.finditer(html), 1):
            raw = m.group(1).strip()
            if not raw:
                errors.append(f"{path}: JSON-LD block {i} is empty")
                continue
            try:
                blocks.append(json.loads(raw))
            except json.JSONDecodeError as e:
                errors.append(f"{path}: JSON-LD block {i} does not parse ({e})")

        if _is_catalog_page(path, html) and not _has_itemlist_or_software(blocks):
            errors.append(f"{path}: catalog page has no ItemList or SoftwareApplication JSON-LD")

        for block in blocks:
            for node in _iter_nodes(block):
                types = _types(node)
                if "ItemList" in types:
                    elements = node.get("itemListElement") or []
                    if not isinstance(elements, list):
                        elements = [elements]
                    n = node.get("numberOfItems")
                    if n is not None and int(n) != len(elements):
                        errors.append(
                            f"{path}: ItemList numberOfItems is {n} but itemListElement has {len(elements)}"
                        )
                if "SoftwareApplication" in types:
                    if not (node.get("name") or "").strip():
                        errors.append(f"{path}: SoftwareApplication is missing name")
                    if path in TOOL_CATALOGS or "applicationCategory" in node or node.get("url"):
                        if path in TOOL_CATALOGS:
                            if not node.get("url"):
                                errors.append(
                                    f"{path}: SoftwareApplication {node.get('name')!r} is missing url"
                                )
                            if not node.get("applicationCategory"):
                                errors.append(
                                    f"{path}: SoftwareApplication {node.get('name')!r} is missing applicationCategory"
                                )
                    offers = node.get("offers")
                    if offers:
                        offer_list = offers if isinstance(offers, list) else [offers]
                        for offer in offer_list:
                            if not isinstance(offer, dict):
                                continue
                            if "price" not in offer:
                                errors.append(
                                    f"{path}: Offer on {node.get('name')!r} is missing price"
                                )
                            if not offer.get("priceCurrency"):
                                errors.append(
                                    f"{path}: Offer on {node.get('name')!r} is missing priceCurrency"
                                )
                        visible = _card_for_app(html, node) or html
                        # Apify rates also appear on pricing.md; require the card first.
                        for price in _offer_prices(node):
                            if price in {"0", "0.0", "0.00"}:
                                if not re.search(r"\bfree\b", visible, re.I):
                                    errors.append(
                                        f"{path}: JSON-LD marks {node.get('name')!r} free, but the visible card does not"
                                    )
                                continue
                            if not _price_appears(visible, price) and not _price_appears(pricing_md, price):
                                errors.append(
                                    f"{path}: JSON-LD price {price} for {node.get('name')!r} is not in the visible card or pricing.md"
                                )
                            elif not _price_appears(visible, price):
                                errors.append(
                                    f"{path}: JSON-LD price {price} for {node.get('name')!r} is not in the visible card"
                                )
    return errors


def main() -> int:
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if len(sys.argv) > 1:
        root = os.path.abspath(sys.argv[1])
    errors = check(root)
    if errors:
        for e in errors:
            print("JSON-LD ERROR:", e)
        print(f"JSON-LD check failed ({len(errors)} error(s))")
        return 1
    print("JSON-LD check passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
