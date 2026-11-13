# MCP Servers · Panda Federation

Source: https://pandafederation.com/mcp.html

MCPPyPI 0.2.0Official Registry

### Panda Research Tools

MCP server: 8 research-integrity tools — fake/retracted citation checks, OpenAlex, PubMed, experts.

Install

```
uvx panda-research-tools
```
MCP client config

```
{"mcpServers":{"panda-research-tools":{"command":"uvx","args":["panda-research-tools"],"env":{"APIFY_TOKEN":"YOUR_APIFY_TOKEN"}}}}
```

Ask your agent

- “Check these 12 references for fake, miscited or retracted papers and tell me which to replace.”
- “Find recent PubMed studies on intermittent fasting and build an evidence table I can open in Excel.”
[GitHub](https://github.com/pandadad0214/panda-research-tools) [PyPI 0.2.0](https://pypi.org/project/panda-research-tools/) [MCP Registry](https://registry.modelcontextprotocol.io/v0/servers?search=io.github.pandadad0214/panda-research-tools) [Glama](https://glama.ai/mcp/servers/pandadad0214/panda-research-tools) [MCP Repository](https://mcprepository.com/pandadad0214/panda-research-tools)MCPPyPI 0.2.0Official Registry

### Panda Public Funding Tools

MCP server: 10 public funding tools — grants, contracts, SBIR/STTR, SEC financials, recalls.

Install

```
uvx panda-public-funding-tools
```
MCP client config

```
{"mcpServers":{"panda-public-funding-tools":{"command":"uvx","args":["panda-public-funding-tools"],"env":{"APIFY_TOKEN":"YOUR_APIFY_TOKEN"}}}}
```

Ask your agent

- “Find open SAM.gov bids for NAICS 541511 with a small-business set-aside.”
- “List open Grants.gov opportunities about rural broadband and their close dates.”
[GitHub](https://github.com/pandadad0214/panda-public-funding-tools) [PyPI 0.2.0](https://pypi.org/project/panda-public-funding-tools/) [MCP Registry](https://registry.modelcontextprotocol.io/v0/servers?search=io.github.pandadad0214/panda-public-funding-tools) [Glama](https://glama.ai/mcp/servers/pandadad0214/panda-public-funding-tools) [MCP Repository](https://mcprepository.com/pandadad0214/panda-public-funding-tools) [cursor.directory](https://cursor.directory/plugins/panda-public-funding-tools)MCPPyPI 0.2.0Official Registry

### Panda Leads Tools

MCP server: 15 public lead tools — local businesses, NPI, hiring signals, new businesses, permits.

Install

```
uvx panda-leads-tools
```
MCP client config

```
{"mcpServers":{"panda-leads-tools":{"command":"uvx","args":["panda-leads-tools"],"env":{"APIFY_TOKEN":"YOUR_APIFY_TOKEN"}}}}
```

Ask your agent

- “Find cardiologists in Phoenix, Arizona from the official NPI Registry.”
- “Pull new Florida LLC and corporation filings from the last few days.”
[GitHub](https://github.com/pandadad0214/panda-leads-tools) [PyPI 0.2.0](https://pypi.org/project/panda-leads-tools/) [MCP Registry](https://registry.modelcontextprotocol.io/v0/servers?search=io.github.pandadad0214/panda-leads-tools) [Glama](https://glama.ai/mcp/servers/pandadad0214/panda-leads-tools) [MCP Repository](https://mcprepository.com/pandadad0214/panda-leads-tools)MCPPyPI 0.2.0Official Registry

### Panda Web Security Tools

MCP server: 7 site and email safety tools — SPF/DKIM/DMARC, AI/SEO audit, prompt-injection scan.

Install

```
uvx panda-web-security-tools
```
MCP client config

```
{"mcpServers":{"panda-web-security-tools":{"command":"uvx","args":["panda-web-security-tools"],"env":{"APIFY_TOKEN":"YOUR_APIFY_TOKEN"}}}}
```

Ask your agent

- “Check SPF, DKIM and DMARC for these 10 domains and list the fixes.”
- “Which of these domains expire in the next 90 days, and who is the registrar?”
[GitHub](https://github.com/pandadad0214/panda-web-security-tools) [PyPI 0.2.0](https://pypi.org/project/panda-web-security-tools/) [MCP Registry](https://registry.modelcontextprotocol.io/v0/servers?search=io.github.pandadad0214/panda-web-security-tools) [Glama](https://glama.ai/mcp/servers/pandadad0214/panda-web-security-tools) [MCP Repository](https://mcprepository.com/pandadad0214/panda-web-security-tools)MCPPyPI 1.8.0

### Panda Federation Tools (umbrella)

Give Claude, Cursor or any MCP client 40 public-data tools on Apify: research, federal funding, leads, web security.

Install

```
uvx panda-federation-tools
```
MCP client config

```
{"mcpServers":{"panda-federation-tools":{"command":"uvx","args":["panda-federation-tools"],"env":{"APIFY_TOKEN":"YOUR_APIFY_TOKEN"}}}}
```

Ask your agent

- “Which Panda tool should I use to find federal contract recompetes?”
- “Search the full tool list for anything about product recalls.”
[GitHub](https://github.com/pandadad0214/panda-federation-tools) [Docs](https://pandadad0214.github.io/panda-federation-tools/) [PyPI 1.8.0](https://pypi.org/project/panda-federation-tools/) [Glama](https://glama.ai/mcp/servers/pandadad0214/panda-federation-tools) [MCP Repository](https://mcprepository.com/pandadad0214/panda-federation-tools)

The four focused domain servers and Quiet File Team MCP are on the Official MCP Registry. This umbrella package is installed from PyPI or GitHub.
MCPPyPI 0.1.3Official Registry

### Quiet File Team MCP

Six free offline MCP tools that explain, configure and check a Quiet File Team (bots sharing files).

Install

```
uvx quiet-file-team-mcp
```
MCP client config

```
{"mcpServers":{"quiet-file-team":{"command":"uvx","args":["quiet-file-team-mcp"]}}}
```

Ask your agent

- “Draft a team.conf for three bots named lead, builder and helper in America/Phoenix.”
- “Explain how the NO WORK early exit works before I set up my routines.”
[Product page](quiet-file-team-mcp/) [Free Bash core](quiet-file-team/) [GitHub](https://github.com/pandadad0214/quiet-file-team-mcp) [PyPI](https://pypi.org/project/quiet-file-team-mcp/) [MCP Registry](https://registry.modelcontextprotocol.io/v0/servers?search=io.github.pandadad0214/quiet-file-team-mcp) [Glama](https://glama.ai/mcp/servers/pandadad0214/quiet-file-team-mcp) [MCP Repository](https://mcprepository.com/pandadad0214/quiet-file-team-mcp) [DevHunt](https://devhunt.org/tool/quiet-file-team-mcp)
