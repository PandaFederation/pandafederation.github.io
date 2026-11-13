# Panda Federation · Public-Data MCP Servers & Apify Tools for AI Agents

Source: https://pandafederation.com/

Free public-data tools for AI agents

# Official public data your agent can check, cite and use.

Catch fake or retracted references, find federal grants and bids, pull official lead lists, and audit domains. Every tool reads official sources and runs in the browser on Apify or inside Claude, Cursor and other MCP clients.
[Find a tool](apify.html)[or add the MCP servers →](mcp.html)

6 MCP servers · 43 public Apify Actors · 7 apps & repos · 36 live Agensi skills. Counts update automatically from the Apify Store, PyPI and GitHub. Apify list rates are on each tool card and on [pricing.md](pricing.md); the Store page is authoritative.

## Start free

Free guide

### Data broker removal guide + state law map

Official opt-out links for people-search sites, the steps that actually work, and a state-by-state map of who has a legal right to deletion. Opt-out links checked November 10, 2026. Not legal advice.
[Open the guide](data-broker-removal/) [State map JSON](data-broker-removal/state-law-map.json)

Free kit · MIT

### Quiet File Team

A small Bash kit that lets several AI bots share one computer through plain files: an append-only task queue, pair notes, and an early exit so idle routines stop instead of spending tokens. No server, no chat bus, no model calls.
[Get the free kit](quiet-file-team/) [Free MCP companion](quiet-file-team-mcp/)

## Real output from real runs

Rows copied from our own test runs of the live Actors (not mock-ups). Each table says when it ran and how many rows it returned.

### Reference Checker
Cited titleVerdictWhyIleal-lymphoid-nodular hyperplasia, non-specific colitis, and…RealRetracted (Retraction Watch notice)Hydroxychloroquine or chloroquine with or without a macrolide for…RealRetracted (Retraction Watch notice)Deep residual learning for image recognitionReal, minor mismatchjournal: cited Proc, actual 2016 IEEE Conference on Computer Vision and…Deep learningReal, major mismatchyear: cited 2017, actual 2015Neural lattice frameworks for quantum basket weaving in arid climatesNot foundNo matching record (likely fabricated)

Platform test run of Reference Checker v0.1 (October 2026), 48 references; 5 rows shown.
[Open on Apify Store](https://apify.com/pandadad0214/reference-checker)

### SAM.gov Contract Opportunities
PostedNotice typeTitleAgencySet-aside2026-11-09Award Notice[DA10--New Action: TIC Application Firewall Maintenance Renewal…](https://sam.gov/opp/34024d55d7654668bcdfcb81acc19b68/view)Veterans Affairs, Department ofService-Disabled Veteran-Owned Small Business2026-11-09Presolicitation[C1DA--657-27-209JB Renovate Main Lobby, Bldgs 1 & 53](https://sam.gov/opp/b2c8f63a5b5b476fb1aee7dddbbaef67/view)Veterans Affairs, Department ofService-Disabled Veteran-Owned Small Business2026-11-09Combined Synopsis/Solicitation[30 RS Mission Planning Software Tool (MPST)](https://sam.gov/opp/73d918da3ba340a28a2d7e5d23c270b1/view)Dept. of DefenseSmall Business Set Aside - Total2026-11-06Sources Sought[C1DA--Renovate Specialty Clinics on 2nd](https://sam.gov/opp/cc0fd029e4f94dd28f101314a39d38cd/view)Veterans Affairs, Department ofService-Disabled Veteran-Owned Small Business2026-11-06Presolicitation[B533--VANIHCS SPS Water Testing (VA-27-00000760)](https://sam.gov/opp/557503071f3d4719a8196424d78b2b7b/view)Veterans Affairs, Department ofService-Disabled Veteran-Owned Small Business

Platform test run, build 0.1.1, checked 2026-11-10: NAICS 5415/5413, last 7 days, small-business set-asides; 38 notices, 5 shown. Contact fields omitted here.
[Open on Apify Store](https://apify.com/pandadad0214/sam-gov-opportunities)

### SPF, DKIM & DMARC Checker
DomainGradeScoreDMARC policySPF ends withMail providerapify.comA100reject-all (fail)Google Workspacegithub.comB87quarantine~all (softfail)Microsoft 365harvard.eduB87quarantine~all (softfail)Proofpointmayoclinic.orgC65none-all (fail)Self-hosted / otherasu.eduB80none~all (softfail)Self-hosted / other

Platform test run, build 0.1.1, checked 2026-11-02; 11 inputs, 5 shown.
[Open on Apify Store](https://apify.com/pandadad0214/email-domain-security-checker)

### Bulk Domain WHOIS & Expiry Checker (RDAP)
DomainRegisteredRegistrarCreatedExpiresnytimes.comyesMarkMonitor Inc.1994-01-182027-01-19bbc.co.ukyesBritish Broadcasting Corporation1994-12-132034-12-13apify.comyesAmazon Registrar, Inc.2009-06-022035-06-02t.coyesCSC Corporate Domains, Inc.2010-04-262027-04-25zzqx-panda-unregistered-2026.comno (available)———

Platform test run, build 0.1.1, checked 2026-11-05; 12 domains, 5 shown.
[Open on Apify Store](https://apify.com/pandadad0214/bulk-domain-whois-expiry)

## Everything else

### MCP servers

Four focused public-data servers, the umbrella package, and Quiet File Team MCP — on GitHub, PyPI, Glama, and the Official MCP Registry where listed.
[Browse servers](mcp.html) [Quiet File Team MCP](quiet-file-team-mcp/)

### Apify tools

Public-data Actors for research, federal funding, leads, and site safety. Each card links the Store page and the matching Agensi skill when one exists.
[Browse Actors](apify.html) [Apify Store](https://apify.com/pandadad0214)

### Apps & repos

Steel Panda, Watchdog Panda, Manual Remake, Quiet File Team, Hidden AI Instructions Watch, and the 3D H.Q.
[Browse apps](apps.html) [Quiet File Team](quiet-file-team/)

### Services

Human-checked citation, research, and public-data work on Fiverr and Upwork.
[Hire us](services.html)

### Writing & launch

Notes on dev.to, news on X, and Panda Federation Tools on Product Hunt (launched November 2026).
[dev.to](https://dev.to/pandadad0214) [Follow on X: @PandaFedHQ](https://x.com/PandaFedHQ) [Product Hunt](https://www.producthunt.com/products/panda-federation-tools)

## A live 3D headquarters

Panda Federation H.Q. is a Three.js office where each bot on a team can show a real-time status chip. It is open source and hosted as a public demo.
[Open H.Q.](https://panda-federation-hq.pandafederation.workers.dev) [GitHub](https://github.com/pandadad0214/panda-federation-hq) [More apps](apps.html)

## Free and paid editions stay linked

When a tool has a free sample or kit and a paid edition, both are named on the tool’s card, with the exact place to switch. Apify list rates are on the card and on [pricing.md](pricing.md); the Store page is authoritative. Agensi package prices stay on the Agensi listing.
