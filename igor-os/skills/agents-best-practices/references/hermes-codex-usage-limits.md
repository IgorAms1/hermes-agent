# Hermes Codex Usage Limits

## When this matters

Use this note when Igor asks for Codex/ChatGPT remaining limits, weekly quota, five-hour/session quota, `/usage` output, or Telegram cron reports for Codex availability.

## Key distinction

OpenAI organization costs are not Codex usage limits.

- `GET https://api.openai.com/v1/organization/costs` reports API spend/costs.
- ChatGPT/Codex remaining quota comes from the ChatGPT Codex backend usage endpoint used by Hermes account usage.

In Hermes, the relevant path is implemented in:

```text
/home/igor1/hermes-agent/agent/account_usage.py
```

The Codex usage URL resolver maps the configured Codex backend:

```text
https://chatgpt.com/backend-api/codex
```

to:

```text
https://chatgpt.com/backend-api/wham/usage
```

## Expected report shape

```text
Codex usage remaining
Provider: openai-codex (Plus)
Session: 38% remaining (62% used) • resets in 37m (2026-05-18 12:22 CEST)
Weekly: 66% remaining (34% used) • resets in 5d 23h (2026-05-24 11:01 CEST)
```

## Auth workflow

Re-authenticate Codex with:

```bash
hermes auth add openai-codex --type oauth --no-browser
```

Then open the printed device URL and enter the printed code. Do not ask Igor to paste tokens into Telegram.

Check credentials:

```bash
hermes auth status openai-codex
hermes auth list
```

If multiple stale Codex credentials exist, remove the stale one by index, id, or label:

```bash
hermes auth remove openai-codex 1
```

## Credential-store pitfall

Hermes has had two Codex auth shapes:

1. legacy provider state: `providers.openai-codex.tokens`;
2. current credential pool: `credential_pool.openai-codex[]`.

`hermes auth add openai-codex` writes to the credential pool. If a usage reporter only calls the legacy `resolve_codex_runtime_credentials()` / `_read_codex_tokens()` path, it can say "No Codex credentials stored" even though `hermes auth status openai-codex` says logged in.

Fix pattern for account usage fetchers:

1. Try the normal runtime resolver.
2. If that fails, fall back to `agent.credential_pool.load_pool("openai-codex")`.
3. Select the highest-priority / newest pooled OAuth entry.
4. Use its `access_token` as the Bearer token and `base_url` as the Codex backend.

## Local timezone

System time may be UTC. User-facing Telegram reports for Igor should show Europe/Amsterdam time. For standalone scripts, set:

```python
os.environ.setdefault("TZ", "Europe/Amsterdam")
time.tzset()
```

before rendering reset times.

## Verification

Run:

```bash
/home/igor1/.hermes/scripts/codex_limits_report.py
```

or use Telegram `/usage` after the gateway reloads/uses the patched account usage code.
