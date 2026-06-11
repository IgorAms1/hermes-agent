---
name: performance
description: "Read-only Hermes performance status for Telegram: latency clues, slow/error tool calls, memory sizes, Hindsight health, cache/compression config, and practical tuning suggestions."
version: 1.0.1
metadata:
  hermes:
    category: igor-os
---

# Performance Status

## When To Use

Use when Igor asks why Hermes is slow, stuck, looping, timing out, using too much memory, failing `session_search`, failing `execute_code`, or whether memory/cache/Hindsight settings look healthy.

Example triggers:
- `/performance`
- `performance status`
- `why is Hermes slow?`
- `почему Hermes тупит?`
- `check latency / tool errors`
- `memory status`

## Safety Rules

- Read-only only. Do not edit config, restart services, prune memory, rotate credentials, or run destructive commands.
- Never print secrets, raw `.env`, OAuth tokens, SSH keys, or full raw journal dumps.
- Prefer counts, durations, file sizes, config values, and redacted excerpts.
- Summarize private conversation/tool output instead of quoting it.
- If a diagnostic command can emit private data, filter it to errors/timing/status lines and redact before showing Igor.

## Default Response Shape

Keep Telegram output compact:

```text
Performance status: OK / attention / degraded
Service: active, uptime <duration>, memory <RSS/peak if available>
Config: compression=<on/off>, prompt_cache=<ttl>, context=<engine>
Memory: MEMORY.md <used>/<limit>, USER.md <used>/<limit>, Hindsight <up/down>
Last 24h:
- slow tools: ...
- tool errors: ...
- session_search errors: ...
- execute_code errors: ...
Likely cause: ...
Next: one concrete safe step
```

Use `OK` only when service is active and recent logs show no repeated slow/error pattern. Use `attention` for isolated errors or expected slow calls. Use `degraded` for repeated timeouts, restart loops, or persistent tool failures.

## Commands

### Service And Resource Snapshot

```bash
systemctl --user status hermes-gateway.service --no-pager | sed -n '1,45p'
ps -p $(systemctl --user show hermes-gateway.service -p MainPID --value) -o pid,etime,%cpu,%mem,rss,cmd --no-headers 2>/dev/null || true
```

### Config Snapshot

```bash
cd ~/hermes-agent
./venv/bin/python - <<'PY'
from pathlib import Path
import json, yaml
cfg = yaml.safe_load(Path.home().joinpath('.hermes/config.yaml').read_text()) or {}
summary = {
    'memory': cfg.get('memory'),
    'compression': cfg.get('compression'),
    'prompt_caching': cfg.get('prompt_caching'),
    'context': cfg.get('context'),
    'tool_output': cfg.get('tool_output'),
    'tool_loop_guardrails': cfg.get('tool_loop_guardrails'),
    'agent': {k: (cfg.get('agent') or {}).get(k) for k in ['max_turns', 'gateway_timeout', 'gateway_notify_interval', 'disabled_toolsets']},
    'toolsets': cfg.get('toolsets'),
}
print(json.dumps(summary, ensure_ascii=False, indent=2))
PY
```

### Memory Size Snapshot

```bash
cd ~/hermes-agent
./venv/bin/python - <<'PY'
from pathlib import Path
import yaml
home = Path.home()
cfg = yaml.safe_load(home.joinpath('.hermes/config.yaml').read_text()) or {}
mem_cfg = cfg.get('memory') or {}
files = [
    ('MEMORY.md', int(mem_cfg.get('memory_char_limit') or 0)),
    ('USER.md', int(mem_cfg.get('user_char_limit') or 0)),
]
for name, limit in files:
    path = home / '.hermes' / 'memories' / name
    size = len(path.read_text(encoding='utf-8')) if path.exists() else 0
    pct = (size / limit * 100) if limit else 0
    print(f'{name}: {size}/{limit} chars ({pct:.0f}%)')
PY
```

### Hindsight Health

```bash
docker ps --format 'table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}' | grep -E '^hindsight|NAMES' || echo 'Hindsight not found as container (may be running as process)'
# Hindsight API root (/) returns 404 -- use /v1/default/banks for health check
curl -fsS http://127.0.0.1:8888/v1/default/banks >/dev/null && echo 'hindsight API: reachable' || echo 'hindsight API: not reachable'
# Also check the UI
curl -fsS -o /dev/null -w 'hindsight UI: HTTP %{http_code}\n' http://127.0.0.1:9999/ 2>/dev/null || echo 'hindsight UI: not reachable'
```

### Recent Tool Latency And Errors

Use 24h by default. Increase only if Igor asks.

```bash
journalctl --user -u hermes-gateway.service --since '24 hours ago' --no-pager \
  | grep -Ei 'Tool .* returned error|tool .* completed \(|completed in|timed out|timeout|session_search|execute_code|compression|cache|memory|Hindsight|Failed with result|Traceback' \
  | sed -E 's#(Bearer )[A-Za-z0-9._~+/-]+#\1[REDACTED]#g; s#(TOKEN|SECRET|KEY|PASSWORD|PASS|AUTH|CREDENTIAL|CLIENT)[A-Za-z0-9_]*[=:][^[:space:]]+#\1=[REDACTED]#Ig' \
  | tail -120
```

### Quick Error Counts

```bash
journalctl --user -u hermes-gateway.service --since '24 hours ago' --no-pager \
  | ./venv/bin/python - <<'PY'
import re, sys
counts = {}
slow = []
for line in sys.stdin:
    if 'Tool ' in line and ' returned error ' in line:
        m = re.search(r'Tool ([A-Za-z0-9_]+) returned error \(([0-9.]+)s\)', line)
        if m:
            tool, sec = m.group(1), float(m.group(2))
            counts[f'{tool}:errors'] = counts.get(f'{tool}:errors', 0) + 1
            if sec >= 5:
                slow.append((tool, sec))
    if 'timed out' in line or 'timeout' in line.lower():
        counts['timeouts'] = counts.get('timeouts', 0) + 1
    if 'session_search' in line and ('error' in line.lower() or 'not in session_id' in line):
        counts['session_search_errors'] = counts.get('session_search_errors', 0) + 1
    if 'execute_code' in line and 'error' in line.lower():
        counts['execute_code_errors'] = counts.get('execute_code_errors', 0) + 1
for k in sorted(counts):
    print(f'{k}: {counts[k]}')
if slow:
    print('slow_error_tools:', ', '.join(f'{tool} {sec:.1f}s' for tool, sec in slow[-10:]))
PY
```

If the Python pipeline returns empty because shell pipeline stdin handling is awkward, fall back to the Recent Tool Latency And Errors command and summarize manually.

## Interpretation Rules

- `session_search` errors like `around_message_id ... not in session_id` usually mean a workflow is passing stale or invalid message IDs. Fix the skill/workflow before tuning infrastructure.
- `execute_code` errors importing unavailable `hermes_tools` functions mean the task should use normal tools or a dedicated tool wrapper, not ad hoc code.
- Calendar reads through `execute_code` are functional but slower and noisier than a deterministic calendar wrapper/tool.
- Memory files above 80% need pruning/offloading to Hindsight; below 80% is not urgent.
- Hindsight reachable but poor recall means data/model/query issue, not service outage.
- Hindsight timeouts should be handled by narrowing queries first: use API-supported `budget`/`max_tokens`, trim `results[:3]` client-side, named partner/project queries only, retry only failed queries once at 30s, then skip gracefully. Do not tune infrastructure before query shape is fixed.
- Repeated timeouts or high RSS after restart indicate real degradation; recommend rollback or a focused debug pass.
- `tool_loop_guardrails.hard_stop_enabled: false` means Hermes warns about loops but does not stop them. Do not recommend enabling hard-stop until a loop pattern is understood.

## Performance Lessons To Apply

Use the map rule:

- Repeated instructions/procedure -> Skill.
- Deterministic API/file/token work -> Tool or script wrapper.
- Slow recurring Python snippets -> dedicated wrapper/tool.
- Repeated tool failure -> test + skill correction.
- Latency suspicion -> measure first, then tune.

Common recommendations:

- If Google Calendar is often used, create a deterministic calendar read wrapper instead of writing Python snippets each time.
- If `session_search` keeps failing with invalid IDs, update the calling skill to list sessions first and only use valid message IDs.
- If memory is near capacity, compact/offload durable details into Hindsight and keep only pointers/operational facts in `MEMORY.md` and `USER.md`.
- If tool outputs are too large, narrow reads/searches instead of raising global output limits.
