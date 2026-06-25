# Stuck Turn / Telegram Hang Triage

Use when Igor reports that Hermes/agent "завис", "hung", or mentions a long delay duration.

## Key lesson

Do not first interpret this as a semantic complaint about the answer. Treat it as a runtime incident until logs say otherwise.

## Minimal read-only diagnostic

1. Check current Amsterdam time if the response will reference time.
2. Check service snapshot:

```bash
systemctl --user status hermes-gateway.service --no-pager | sed -n '1,45p'
ps -p $(systemctl --user show hermes-gateway.service -p MainPID --value) -o pid,etime,%cpu,%mem,rss,cmd --no-headers 2>/dev/null || true
```

3. Check the relevant journal window, filtered/redacted:

```bash
journalctl --user -u hermes-gateway.service --since '<window start>' --until '<window end>' --no-pager \
  | grep -Ei 'Cancelled task|did not exit|Tool .* returned error|timeout|timed out|Unclosed client session|Traceback|model|openai|codex|telegram|gateway' \
  | sed -E 's#(Bearer )[A-Za-z0-9._~+/-]+#\1[REDACTED]#g; s#(TOKEN|SECRET|KEY|PASSWORD|PASS|AUTH|CREDENTIAL|CLIENT)[A-Za-z0-9_]*[=:][^[:space:]]+#\1=[REDACTED]#Ig' \
  | tail -200
```

4. Count recent symptoms if needed:

```bash
journalctl --user -u hermes-gateway.service --since '24 hours ago' --no-pager \
  | grep -E 'Cancelled task|Unclosed client session|Tool .* returned error|timeout|timed out' \
  | sort | uniq -c | tail -80
```

## Signals and meaning

- `Cancelled task ... did not exit within 5s; unblocking dispatch` = an old Telegram agent task did not terminate cleanly; a new message forced dispatch forward.
- Repeated `Unclosed client session` = likely aiohttp/session cleanup leak around subprocess/tool/model calls; mention as a runtime smell, not proof of root cause.
- Skill collision errors (`Skill name collision`, ambiguous skill) = contributing workflow friction, not usually enough alone to explain a 100+ minute hang.
- Normal RSS/CPU and active service = not OOM/CPU starvation.
- Hindsight API reachable and no session_search errors = don't blame memory/search.
- `gateway_timeout` value matters: if set high, the gateway may allow long stuck tasks before timing out.

## Response shape

```text
Performance status: degraded/attention
What happened: [runtime hang / cancelled task / no evidence of service crash]
Evidence:
- [timestamp + log signal]
- [service state]
- [error counts]
Likely cause: [agent task stuck after tool/model chain; contributing factors]
Not likely: [memory pressure / Hindsight / session_search / CPU]
Next safe step: [one read-only or explicitly-confirmed action]
```

## Pitfall

If Igor asks "почему тебя увело куда-то?" after a long silence, don't assume he means topical drift. Ask logs first or run performance diagnostics immediately. Otherwise the answer becomes a therapy note about agent reasoning while the actual problem was a 112-minute stuck turn. Very elegant. Completely wrong layer.
