# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Install in development mode (also installs the `requests` dependency)
pip install -e .

# Run the CLI — the message is read from stdin (there is no -t/--text flag)
echo 'message' | sendtoteams -u <webhook_url>
echo 'message' | sendtoteams -n <target_name>   # resolve URL from TEAMS_WEBHOOK

# Dry run (prints resolved url + JSON payload, sends nothing)
echo 'message' | sendtoteams -u <webhook_url> --dry

# List configured webhook targets
sendtoteams --list
```

There is no test suite, linter, or build step configured in this repo; `--dry` is the primary way to inspect behavior.

## Architecture

Single-module Python CLI package (`teams-webhook`) that sends stdin to a Microsoft Teams webhook (Power Automate workflow, since the legacy Teams incoming-webhook connector is deprecated).

**Entry point**: `sendtoteams` console script → `teams_webhook.send:send` (defined in `setup.cfg`).

**All logic lives in [send.py](src/teams_webhook/send.py).** `send()` resolves a target URL, reads stdin, builds a payload in one of two formats, and POSTs it (or prints it under `--dry`).

### Two output formats

Each target carries a format, chosen by a URL prefix. `parse_url_entry()` strips the prefix and returns `(url, use_message)`:

- **Card** (default, no prefix or `card:`/`c:`) → `build_card_message()` produces an Adaptive Card (version 1.4) inside an `attachments` array. URLs are rewritten to `[url](url)` markdown by `markdown()`, newlines become `  \n`, and the top-level `text` field is also populated (legacy).
- **Message** (`msg:`/`message:`/`m:`) → `build_message_message()` produces a flat `{'text': html}` payload. URLs are rewritten to `<a href>` anchors by `anchorize()` and newlines become `<br>`.

Example: `TEAMS_WEBHOOK='msg:https://...'` or `-u 'card:https://...'`.

### Target configuration (`get_targets`)

`TEAMS_WEBHOOK` (or a `-u` value) is a semicolon-separated list of entries, parsed into a `name → value` dict:

- Plain URL (optionally with a `msg:`/`card:` prefix) → the implicit `default` target.
- `name=url` → a named target.
- `name=othername` → an alias, stored internally as `alias:othername`. `send()` follows the `alias:` chain (looping until it hits a real URL) when resolving `-n`.

`-n` defaults to `default`. `--list` prints the raw stored values (so aliases show as `alias:...`).
