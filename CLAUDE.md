# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Install in development mode
pip install -e .

# Install dependencies only
pip install requests

# Run the CLI
sendtoteams -u <webhook_url> -t 'message'
echo 'message' | sendtoteams -u <webhook_url>

# Dry run (prints JSON without sending)
echo 'message' | sendtoteams -u <webhook_url> --dry

# List configured webhook targets
sendtoteams --list
```

## Architecture

This is a single-module Python CLI package (`teams-webhook`) that sends messages to Microsoft Teams via Power Automate workflow webhooks (the Teams incoming webhook connector is deprecated).

**Entry point**: `sendtoteams` console script → `teams_webhook.send:send`

**Core flow in [send.py](src/teams_webhook/send.py)**:
1. `get_targets(url_string)` — parses a semicolon-separated URL config string from the `TEAMS_WEBHOOK` env var into a dict of named targets. Supports aliases (`alias=target_name`) and an implicit `default` target for bare URLs.
2. `markdown(text)` — converts raw HTTP/HTTPS URLs in text into Adaptive Card markdown link syntax.
3. `send()` — CLI entrypoint: resolves the target URL (from `-u` flag or named target via `-n`), reads message from stdin, wraps it in a Teams Adaptive Card JSON payload, and POSTs it to the webhook.

**Message format**: Sends an Adaptive Card (version 1.4) inside a `attachments` array. The `text` field at the top level is also populated (legacy field). Newlines are converted to `  \n` for markdown compatibility.

**Webhook URL configuration**: Set `TEAMS_WEBHOOK` env var with semicolon-separated entries:
- Plain URL → becomes the `default` target
- `name=url` → named target
- `alias=name` → alias pointing to another target name
