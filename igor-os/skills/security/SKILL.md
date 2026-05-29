---
name: security
description: Read-only Hermes VPS security status for Telegram: service health, recent sensitive-access/tool-risk audit summaries, redacted errors, and safe next steps.
version: 1.0.0
metadata:
  hermes:
    category: igor-os
---

# Security Status

## When To Use

Use when Igor asks for security status, audit logs, sensitive access events, tool risk events, Hermes service health, recent errors, or whether the VPS/agent looks safe after a change.

Example triggers:
- `/security`
- `security status`
- `show security audit`
- `any sensitive_access_audit lines?`
- `is Hermes healthy?`
- `что по безопасности?`

## Safety Rules

- Read-only only. Do not edit files, restart services, rotate credentials, change config, or run destructive commands.
- Never print raw secrets, token values, OAuth files, `.env` contents, SSH keys, raw prompts, or full journal dumps.
- Prefer summaries, counts, categories, service state, and last few redacted lines.
- Redact before showing any log line.
- If output may contain private conversation text, summarize it instead of quoting it.
- If Igor asks for raw logs, warn that raw logs may contain private data and provide a redacted excerpt unless he explicitly confirms raw output.

## Default Response Shape

Keep Telegram output compact:

```text
Security status: OK / attention / critical
Service: active since <time>, PID <pid>
Mode: sensitive_access=<audit|confirm|block>
Last 1h:
- sensitive_access_audit: N events; categories: ...; tools: ...
- tool_risk_audit: N events; critical tools observed: ...
- errors: N; crashes/restarts: N
Recent redacted lines:
1. ...
2. ...
Next: ...
```

Use `OK` only when the service is active and there are no fresh crashes or high-signal errors. Use `attention` when audit events or warnings exist but service is healthy. Use `critical` when the service is inactive, repeatedly restarting, or fresh stack traces/crashes appear.

## Commands

### Service Health

```bash
systemctl --user is-active hermes-gateway.service
systemctl --user status hermes-gateway.service --no-pager | sed -n '1,40p'
```

### Config Mode

```bash
cd ~/hermes-agent
./venv/bin/python - <<'PY'
from hermes_cli.config import load_config
security = load_config().get('security', {}) or {}
print(security.get('sensitive_access', {'mode': 'audit'}))
PY
```

### Recent Security Audit Summary

Use a short window by default (`1 hour ago`). Increase only if Igor asks.

```bash
journalctl --user -u hermes-gateway.service --since '1 hour ago' --no-pager \
  | grep -E 'sensitive_access_audit|tool_risk_audit|ERROR|Traceback|Failed with result|Started hermes-gateway|Stopped hermes-gateway' \
  | sed -E 's#(Bearer )[A-Za-z0-9._~+/-]+#\1[REDACTED]#g; s#(TOKEN|SECRET|KEY|PASSWORD|PASS|AUTH|CREDENTIAL|CLIENT)[A-Za-z0-9_]*[=:][^[:space:]]+#\1=[REDACTED]#Ig' \
  | tail -80
```

### Count Audit Events

```bash
journalctl --user -u hermes-gateway.service --since '1 hour ago' --no-pager \
  | grep -E 'sensitive_access_audit|tool_risk_audit' \
  | sed -E 's#(Bearer )[A-Za-z0-9._~+/-]+#\1[REDACTED]#g; s#(TOKEN|SECRET|KEY|PASSWORD|PASS|AUTH|CREDENTIAL|CLIENT)[A-Za-z0-9_]*[=:][^[:space:]]+#\1=[REDACTED]#Ig' \
  | ./venv/bin/python - <<'PY'
import json, re, sys
counts = {'sensitive_access_audit': 0, 'tool_risk_audit': 0}
categories = set()
tools = set()
critical_tools = set()
for line in sys.stdin:
    if 'sensitive_access_audit' in line:
        counts['sensitive_access_audit'] += 1
    if 'tool_risk_audit' in line:
        counts['tool_risk_audit'] += 1
    m = re.search(r'(sensitive_access_audit|tool_risk_audit) (\{.*\})', line)
    if not m:
        continue
    try:
        event = json.loads(m.group(2))
    except Exception:
        continue
    if event.get('event') == 'sensitive_access_audit':
        for ref in event.get('references', []) or []:
            cat = ref.get('category')
            if cat:
                categories.add(cat)
        tool = (event.get('metadata') or {}).get('tool')
        if tool:
            tools.add(tool)
    elif event.get('event') == 'tool_risk_audit':
        tool = event.get('tool_name')
        if tool:
            tools.add(tool)
        if event.get('risk_level') == 'critical_system' and tool:
            critical_tools.add(tool)
print('sensitive_access_audit=', counts['sensitive_access_audit'])
print('tool_risk_audit=', counts['tool_risk_audit'])
print('categories=', ', '.join(sorted(categories)) or 'none')
print('tools=', ', '.join(sorted(tools)) or 'none')
print('critical_tools=', ', '.join(sorted(critical_tools)) or 'none')
PY
```

If the Python pipeline returns empty because shell pipeline stdin handling is awkward, fall back to the Recent Security Audit Summary command and summarize manually.

## Interpretation Rules

- `sensitive_access_audit` in `audit` mode is not automatically bad. It means Hermes touched or referenced sensitive paths, often legitimately for Google Calendar or diagnostics.
- A `google_oauth_token` event during a Calendar read is expected.
- `ssh_secret`, `hermes_env`, or `hermes_auth` from `terminal` or `execute_code` deserves attention unless Igor explicitly requested diagnostics.
- `tool_risk_audit` for `terminal`, `execute_code`, `write_file`, `patch`, `skill_manage`, or `cronjob` means critical tool usage happened or was attempted; summarize, do not panic.
- Fresh `Failed with result`, `Traceback`, or repeated `ERROR` after a restart means investigate before making more changes.

## Safe Next Steps

If status is `attention`, recommend one concrete next step:
- keep `security.sensitive_access.mode: audit` and observe for 24h;
- review the last audit categories;
- run a read-only smoke test;
- open the PR for review.

If status is `critical`, recommend rollback or pausing further changes before debugging.
