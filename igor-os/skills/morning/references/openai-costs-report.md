# OpenAI / Codex Costs and Limits Report

Use when Igor asks to add Codex/OpenAI credit, cost, limit, or remaining-budget visibility to morning briefs or Telegram cron jobs.

## First decision: costs vs Codex limits

There are two different telemetry classes that sound similar:

1. **OpenAI organization costs / spend** — dollars spent via the OpenAI API billing system.
2. **ChatGPT/Codex usage remaining** — the UI percentages Igor sees in Codex/ChatGPT, e.g. `5h 61%` and `Weekly 70%` with reset times.

Do not answer a Codex-limits request with the organization costs endpoint. If Igor shows or asks about "Usage remaining", "5h", "Weekly", or reset times, use the Codex account-usage path below.

## Key facts for OpenAI costs

- `GET https://api.openai.com/v1/organization/costs` reports organization spend/costs, not Codex UI usage remaining.
- Estimated remaining budget requires a configured budget: `remaining = OPENAI_MONTHLY_BUDGET_USD - month_to_date_spend`.
- Requires an OpenAI Admin API key or API key with organization costs permissions.
- Never ask Igor to paste the key into Telegram. Use a local env file.

## Codex UI limits / usage remaining

Use this when Igor asks for the limits shown in the Codex UI (`Usage remaining`, `5h`, `Weekly`, reset time/date).

Hermes already has the implementation in:

```text
/home/igor1/hermes-agent/agent/account_usage.py
```

Core call:

```python
from agent.account_usage import fetch_account_usage, render_account_usage_lines
snapshot = fetch_account_usage("openai-codex", base_url="https://chatgpt.com/backend-api/codex")
print("\n".join(render_account_usage_lines(snapshot)))
```

The underlying Codex/ChatGPT account endpoint is resolved to a `wham/usage` path for `https://chatgpt.com/backend-api/codex`. It returns rate-limit windows such as:

```text
Session: 61% remaining (39% used) • resets ...
Weekly: 70% remaining (30% used) • resets ...
```

Skill script:

```bash
python /home/igor1/hermes-agent/igor-os/skills/morning/scripts/codex_limits_report.py
```

A local convenience copy may also exist at:

```bash
~/.hermes/scripts/codex_limits_report.py
```

If unavailable, the usual fix is Codex OAuth setup/refresh via `hermes auth` for `openai-codex`; do not switch to OpenAI Admin costs API as a workaround.

### Codex OAuth diagnostics / re-auth workflow

Use this when `/usage` or `scripts/codex_limits_report.py` fails to show Codex limits.

1. Check what Hermes thinks is configured:

```bash
hermes auth status openai-codex
hermes auth list
```

2. Probe the exact usage path and surface the underlying error without printing tokens:

```bash
cd /home/igor1/hermes-agent
python - <<'PY'
from agent import account_usage
try:
    snap = account_usage._fetch_codex_account_usage()
    print('\n'.join(account_usage.render_account_usage_lines(snap)) if snap else 'NO_SNAPSHOT')
except Exception as e:
    print(type(e).__name__, str(e))
PY
```

3. If credentials are missing/expired/invalid, start Codex OAuth again. Prefer `--no-browser` in Telegram/remote sessions so Igor receives a device URL and code:

```bash
hermes auth add openai-codex --type oauth --no-browser
```

Send Igor only the verification URL and short device code. Never print or request OAuth tokens.

4. After Igor completes browser sign-in, rerun:

```bash
python /home/igor1/hermes-agent/igor-os/skills/morning/scripts/codex_limits_report.py
# or, from Telegram, /usage
```

Gotcha: `hermes auth status openai-codex` / `hermes auth list` can confirm a pooled OAuth credential, but the Codex account-usage code still needs a usable Codex OAuth token shape for `agent.account_usage`. If the high-level status says logged in while usage remains unavailable, trust the direct probe above and re-auth rather than falling back to organization costs.

## Existing local OpenAI costs script

Path:

```bash
~/.hermes/scripts/openai_costs_report.py
```

It reads:

```text
OPENAI_ADMIN_KEY or OPENAI_API_KEY
OPENAI_MONTHLY_BUDGET_USD
OPENAI_COST_LOOKBACK_DAYS
```

from environment and from:

```bash
~/.hermes/secrets/openai_costs.env
```

Template created at:

```bash
~/.hermes/secrets/openai_costs.env.example
```

Setup:

```bash
mkdir -p ~/.hermes/secrets
chmod 700 ~/.hermes/secrets
cp ~/.hermes/secrets/openai_costs.env.example ~/.hermes/secrets/openai_costs.env
chmod 600 ~/.hermes/secrets/openai_costs.env
nano ~/.hermes/secrets/openai_costs.env
```

Expected output shape:

```text
Codex / OpenAI costs — YYYY-MM-DD
Month-to-date spend: $X.XX
Last 30 days spend: $Y.YY
Configured monthly budget: $Z.ZZ
Estimated remaining: $R.RR (P% used)
Status: OK / watch it / over configured budget
```

## Integration options

Preferred default for both costs and Codex limits: separate Telegram cron in the morning, not inside the main `/morning` brief, unless Igor explicitly wants it embedded.

If embedding in `/morning`, keep it to one compact line under an optional `Usage / budget` block:

```text
Codex: 5h 61% left, weekly 70% left.
```

## Gotchas

- Do not confuse Codex UI limits with OpenAI API spend.
- Do not confuse usage/costs with credit balance.
- If Igor asks for "remaining credits" but shows `5h` / `Weekly`, treat it as Codex limits, not billing.
- If the costs API returns permission errors, the fix is usually an Admin API key with organization costs permissions, not a script rewrite.
- If Codex limits are unavailable, the fix is usually Codex OAuth credentials via `hermes auth`, not an OpenAI Admin API key.
- Redact all secrets in logs and summaries.
