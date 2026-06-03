# Memory Architecture Convention

Established May 19, 2026 as the standard for Igor OS.

## Principle

Memory (injected every turn) holds only what's needed daily: style, health, key people, exclusions, compact pointers. Detailed partner/project data lives in files, loaded lazily by the agent when context triggers it.

## Pattern

**Memory entry (compact pointer):**
```
CloudFresh (top-3 CEE partner): CRO Živko (Bulgaria). Marketer: Alexandra. Call extract at ~/.hermes/context/cloudfresh-call-2026-05-19.md — load on CloudFresh mentions.
```

**File (lazy load):**
`~/.hermes/context/cloudfresh-call-2026-05-19.md` — full call extract, action items, contacts.

## File locations

- `~/.hermes/context/` — partner files, call extracts
- `igor-os/context/` — Semaphore discovery, project-level docs

## Agent behavior

When Igor mentions an entity (CloudFresh, Traco, Semaphore), the agent:
1. Checks memory for a file pointer
2. Loads the file via read_file or skill_view
3. Uses file content for the current task

When storing new information:
1. Save to file first (write_file)
2. Update memory pointer (compact, one line)
3. If memory near capacity, offer prune before auto-saving

## Memory budget

Target: under 50% usage. At 85%+ offer structured prune.
Entries should be declarative facts, not instructions or stale metadata.
