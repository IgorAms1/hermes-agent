# Memory Management

## Current Architecture (May 2026)

- **Backend**: Mnemosyne v2.8.0 — local SQLite + FTS5 + sqlite-vec. Zero-cloud, sub-millisecond.
- **Storage**: `~/.hermes/mnemosyne/data/mnemosyne.db`
- **Pre-processor**: `/extract` skill — structured extraction from walls of text. Uses delegate_task for inputs >2000 chars to keep main context lean.
- **Maintenance**: `/cleanup` skill — audits memory, cron jobs, skills, and context files for staleness.
- **Tool**: `mnemosyne_remember` for direct writes. Old `memory` tool still available but secondary.

## Checking Status

```bash
hermes memory status           # Provider: mnemosyne (after restart)
hermes mnemosyne stats         # Working + episodic memory counts
```

Memory usage percentage shown in system prompt header (e.g., `[19% — 1,978/10,000 chars]`). Flag when >85%.

## Limit Configuration

```bash
# In ~/.hermes/config.yaml under memory: block
memory.memory_char_limit: 10000   # general memory
memory.user_char_limit: 5000      # user profile
memory.provider: mnemosyne        # set by mnemosyne installer
```

Igor chose these limits deliberately. Do not suggest changes unless he raises it first.

## Pruning Workflow

Use `/cleanup` skill — it audits all 9 entries and categorizes into:
- Remove (stale), Compact (too verbose), Keep (boundaries, active projects, stable preferences)

Old file-based memory (`~/.hermes/memories/MEMORY.md` + `USER.md`) preserved as backup — not active when Mnemosyne is provider.

## Migration Reference

Migration script: `migrate_to_mnemosyne.py` (run in hermes-agent venv).
Import path: `from mnemosyne.core.memory import Mnemosyne, init_db`
Method: `store.remember(content, source, importance, scope, trust_tier)`

## What NOT to Prune

- Boundaries and "NOT my" rules
- Active partner/contact info
- Stable preferences (style, tone, communication rules)
- System rules (timezone conversion)
- Training schedules (compacted is fine)
