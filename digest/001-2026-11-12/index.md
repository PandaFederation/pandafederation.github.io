# Digest #1: Server Actors, a release calendar for MCP, and an SEC deadline · Panda Federation

Source: https://pandafederation.com/digest/001-2026-11-12/

Digest #1 · 2026-11-12

# Server Actors, a release calendar for MCP, and an SEC deadline

Five things from the last few days that matter if your agent works with public data, with our take on each, and then what we shipped.

## MCP gets a release calendar (Nov 11)

The MCP maintainers are moving spec releases to a fixed six-month schedule, on the last Tuesday of March and September. The next one is targeted for March 30, 2027. A proposal that isn't ready moves to the next release instead of holding up the spec. **Our take:** this is the most useful MCP news of the week for small server authors. We can plan our server updates around two known dates instead of watching the spec repo. [Read the post](https://blog.modelcontextprotocol.io/posts/mcp-release-cycle/)

## File uploads and downloads are coming to MCP, as an experiment (Nov 10)

An optional extension, `io.modelcontextprotocol/files`, would let clients and tools move files in and out of band. It's explicitly experimental, has no reference implementation yet, and the maintainers hope to stabilize it before the end of the year. **Our take:** PDF table extraction and Excel exports are the clumsiest part of agent data work today, so a standard way to hand a file to a tool would help a lot. We won't build on it until it reaches Beta. [Read the post](https://blog.modelcontextprotocol.io/posts/exploring-file-uploads-and-downloads-in-mcp/)

## Apify makes Server Actors generally available (Nov 10)

At its Run by Apify event, Apify announced general availability of Server Actors: always-ready services that answer requests like an API, without starting a new run for each call. Apify AI also gained the ability to orchestrate several Actors and build new ones from plain-language instructions. **Our take:** for agent tool calls, start-up time matters as much as the data does. Quick lookups such as a single domain check or one VIN are the obvious first candidates for an always-on version. [Read the announcement](https://www.globenewswire.com/news-release/2026/11/10/3399579/0/en/apify-unveils-new-ai-agent-capabilities-and-server-actors-to-support-growing-demand.html)

## Apify MCP server 0.21.5 and 0.21.6 (Nov 10–11)

Two quick releases. 0.21.5 lists only dataset field selections that actually work and explains empty or past-the-end dataset pages. 0.21.6 identifies MCP-server Actors in Actor details. **Our take:** small fixes, but they target a real failure mode. Agents that page past the end of a dataset and read the empty page as "no results" give wrong answers. [Release notes](https://github.com/apify/apify-mcp-server/releases)

## SEC draft 2027 taxonomies: technical feedback closes Nov 16

The SEC posted its draft 2027 taxonomy update on Sept. 14 and is taking technical feedback until 4 p.m. ET on Nov. 16, 2026. It's a draft for comment, not an approved change. **Our take:** anyone who pulls XBRL facts from EDGAR, including our SEC Financials Actor, should read the release notes now, before element changes show up in real filings. [SEC notice](https://www.sec.gov/newsroom/whats-new/260914-draft-2027-sec-taxonomies)

## What we shipped

- [Quiet File Team MCP 0.1.1](https://pypi.org/project/quiet-file-team-mcp/) is on PyPI and the Official MCP Registry. Install with `uvx quiet-file-team-mcp`.
- [SAM.gov Contract Opportunities](https://apify.com/pandadad0214/sam-gov-opportunities) is a new Actor that finds open federal bids from the official public data extract, with no API key.
- The four focused MCP servers reached v0.2.0, and the umbrella package reached v1.8.0 ([all servers](https://pandafederation.com/mcp.html)).
- The [free data broker removal guide + state law map](https://pandafederation.com/data-broker-removal/) has opt-out links checked November 10, 2026.
- The site now has a [What's New](https://pandafederation.com/whats-new/) changelog with an Atom feed, plus real sample output on the homepage.

[All issues](../) · [What's New](../../whats-new/)
