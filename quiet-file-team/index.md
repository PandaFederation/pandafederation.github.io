# Quiet File Team · Panda Federation

Source: https://pandafederation.com/quiet-file-team/

## What it is

Quiet File Team lets several AI bots share one computer through plain files, so idle routines stop on `NO WORK` instead of spending tokens. It is a free, MIT-licensed Bash kit (pair notes, an append-only task queue, a board and an early-exit check) with no server, chat bus or LLM inside.

It runs on one shared Linux machine. It is not a hosted service, not a replacement for the owner’s chat, and not a way for bots to talk behind the owner’s back.
[GitHub repo](https://github.com/pandadad0214/quiet-file-team)[Free MCP companion](../quiet-file-team-mcp/)[Latest release (v0.1.0)](https://github.com/pandadad0214/quiet-file-team/releases/tag/v0.1.0)

## Who it is for

Use it when two or more bots or scheduled routines share one machine and you want idle runs to exit early and handoffs to live in files.

Do not use it when bots run on different machines without a shared local disk, you need authentication or encryption, or you need real-time chat.

## How it works

Each bot’s chat is for the owner. A shared computer plus files is the bus; there are no background listeners or hidden chat channels. Every routine starts with `has-work.sh <id>`. Exactly `NO WORK` means stop: no chat, no status, no board line. Otherwise pick up only the listed work.
**Pair files**`pairs/<a-b>.md` hold short, directed handoffs. Notes over 2000 characters get an overflow file under `pairs/long/`.**Task queue**`tasks.log` is append-only. The latest event for a task is its state: `open`, `claimed`, `done`, `blocked`, `needs-owner`, `decided` or `cancelled`.**Board**`board.md` is an append-only summary, updated via `post.sh`. It is not a transcript.**Early exit**Start every routine with `has-work.sh` and stop when it prints exactly `NO WORK`. It always exits 0, so check the output.

Scripts serialize mutations using `flock`. All writes stay on the local disk: no network, no scheduler, no model calls. Requirements are Linux, Bash 4+, GNU coreutils, awk, sed, tar and util-linux `flock`.

Ids label records; they do not prove identity. This is not authentication, access control or encrypted storage. Never put private data in this bus.

## Install and quick start

Copy the kit into a shared local folder. Keep its scripts and `team.conf` together. No package registry is required.

```
curl -fsSL https://github.com/pandadad0214/quiet-file-team/archive/refs/tags/v0.1.0.tar.gz | tar xz && mv quiet-file-team-0.1.0 team
export TEAM_DIR="$PWD/team"
bash "$TEAM_DIR/has-work.sh" helper # a fresh kit prints: NO WORK
```

Or clone the repo: `git clone https://github.com/pandadad0214/quiet-file-team.git team`.

- Name your bots in `team/team.conf` (`TEAM_IDS="lead builder helper"`) and set `TEAM_TZ` (default `UTC`).
- Start every routine with `bash "$TEAM_DIR/has-work.sh" <id>` and stop the routine when it prints exactly `NO WORK`.
- Give each bot the core rules in the repo and paste the early-exit block into each routine. Then run the practice exercise once in a fresh folder.

A short practice run on an untouched demo log:

```
export TEAM_DIR="$PWD/team"
bash "$TEAM_DIR/task.sh" new lead helper "Sort a sample inbox"
bash "$TEAM_DIR/task.sh" claim T0001 helper
bash "$TEAM_DIR/task.sh" set T0001 done helper "Sample inbox sorted"
bash "$TEAM_DIR/post.sh" helper done "Demo checklist updated"
bash "$TEAM_DIR/pair.sh" lead builder "Review the demo checklist"
bash "$TEAM_DIR/has-work.sh" helper
# NO WORK
```

Use the task id printed by `new` if the folder already contains tasks. Do not run the demo against a production data folder. Full commands and trust limits are in the [GitHub README](https://github.com/pandadad0214/quiet-file-team#how-to-use-this).

## Commands
**has-work.sh <id>**Print pending `TASKS:` / `HANDOFFS:` or exactly `NO WORK`.**task.sh**`new`, `claim`, `set`, `list`, `owner`, `stale`, `show`.**pair.sh**Append a directed pair note; `read [count]` reads recent lines.**post.sh**Append `done`, `needs-owner`, `handoff: <id>`, `fyi` or `resolved`.**backup.sh**Optional local snapshot of board, task log and pairs. No upload.

## Switch editions

The free core on this page is enough to run a team. A free MCP companion explains and checks a layout. A paid setup kit is also live if you want a guided install or a pre-configured ZIP.

- **Free Bash core** — this page. Install with the curl or git clone command above. Source is on [GitHub](https://github.com/pandadad0214/quiet-file-team).
- **Free MCP companion** — six offline guidance tools (explain the method, draft config and early-exit text, validate a supplied layout, draft a practice workflow, batch owner questions). It never reads your files or calls the network. Keep this folder, then add the companion to your MCP client: `uvx quiet-file-team-mcp`. Product page: [Quiet File Team MCP](../quiet-file-team-mcp/).
- **Setup kit generator** — paid Apify Actor, charged per successfully generated kit; the list rate is on the Apify Tools card and on [pricing.md](../pricing.md); the Store page is authoritative. On the Actor page fill Roster (`TEAM_IDS`, e.g. `lead builder helper`), IANA time zone (`TEAM_TZ`) and Coordinator (`lead`), set the maximum run charge to at least the price shown on the Store page, then Start. Download `OUTPUT.zip` from the run’s key-value store and unpack it into a new folder; move live tasks over by hand. [Open Apify Store](https://apify.com/pandadad0214/quiet-file-team-setup)
- **Quiet File Team Setup Kit** — paid Agensi skill, one-time price on the live listing. Keep this folder, load the skill in your agent, apply the rule packs you want, practice in a new folder and finish the acceptance checklist. Do not replace operational logs with examples. [Open Agensi](https://agensi.io/skills/quiet-file-team-setup-kit)
- **Paid → free** — keep your scripts, drop the optional kit rules and continue with the free README on this page. For a clean copy, clone the GitHub repository separately, back up current data and re-enter active tasks deliberately; never merge `.seen` cursors blindly.

## FAQ

### Is this a hosted service?

No. It is a local Bash kit on one shared Linux machine. There is no server, chat bus or LLM inside, and it makes no network or model calls.

### How do idle routines stop spending tokens?

Start every routine with `has-work.sh <id>`. When it prints exactly `NO WORK`, the routine should stop: no chat, no status, no board line. These are operating practices, not a measured savings promise.

### What does a bot need besides the scripts?

Give each bot the core rules from the repo and paste the early-exit block into each routine, replacing the id and path. Ensure the routine really stops on exactly `NO WORK`.

### Can I put secrets or personal data in the files?

No. The bus is plain files on one trusted machine, with no encryption or access control. Text is checked for long digit strings and email-shaped content as a rough guardrail, not a secret detector. Never put private data in this bus.

### Does the free MCP install the scripts for me?

No. [Quiet File Team MCP](../quiet-file-team-mcp/) explains, configures and checks a team from supplied inputs. Install the Bash core from this page or GitHub, then add the MCP companion if you want setup guidance.

## Links
[GitHub repo](https://github.com/pandadad0214/quiet-file-team)[Quiet File Team MCP](../quiet-file-team-mcp/)[Apify setup kit (price on the Store page)](https://apify.com/pandadad0214/quiet-file-team-setup)[Agensi setup kit (price on Agensi)](https://agensi.io/skills/quiet-file-team-setup-kit)[All apps & repos](../apps.html)[Follow on X: @PandaFedHQ](https://x.com/PandaFedHQ)

Built by Panda Federation · MIT License · Product page for Quiet File Team.
