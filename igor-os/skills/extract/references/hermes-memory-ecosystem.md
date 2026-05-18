# Hermes Memory Ecosystem — Community Research (May 2026)

Sourced from [r/hermesagent](https://www.reddit.com/r/hermesagent/comments/1tdzucm/any_solutions_for_hermes_memory/), 50+ comments.

## Built-in Hermes Memory Plugins

Hermes Agent ships with 8 memory plugins:

| Plugin | Type | Notes |
|---|---|---|
| honcho | LLM-enhanced | Collects aggressively — some users left because it stored too much |
| hindsight | LLM-enhanced | Popular, Web GUI, semantic connections. Token heavy (1 user: 5M tokens in hours). Needs cheap model |
| supermemory | LLM-enhanced | Similar tier |
| holographic | Basic | Very basic, lightweight |
| openviking | Mid-tier | — |
| mem0 | API-based | Free API key, good integration |
| retaindb | — | — |
| byterover | — | — |

**Current Igor OS:** None active — using Hermes built-in recall surfaces: FTS5-backed `session_search`, injected memory blocks, memory files, and the `memory` tool for approved durable writes.

## Community Favorites (Not in Built-in List)

| Tool | Why | Setup |
|---|---|---|
| **Mnemosyne** | Purpose-built for Hermes, local, no LLM required, vector embeddings | Separate install, has Discord community |
| **LCM** | Cross-session context, used with Mnemosyne | Companion plugin |
| **Hindsight** | Best balance of "not too simple, not overcomplicated" per multiple users | Built-in, just needs cheap model |
| **Obsidian Vault** | Full human control, bootstraps from last 2 entries on session start | obsidian skill exists in Hermes (disabled on Telegram) |

## Critical Patterns

### 1. Capture Frequency
Power users adjust how often memory captures — "every 10th message" instead of every message dramatically reduces token cost without meaningful loss.

### 2. Language Mismatch
German working memory was compressed to English by LLM → vector search broke. The embedding model and the query language must match the stored language. **Relevant for Igor:** Russian/English/Dutch mix.

### 3. Cheap Model Strategy
External memory plugins make additional API calls on every user message. Community consensus: use a dirt-cheap cloud model (gemini-flash, minimax subscription) or run local to keep costs manageable.

### 4. Structure Over Volume
One power user described: `memory.md` vs `fact_base` with strict uniqueness, and prompting to check `fact_base` on every turn. The structure matters more than the storage backend.

### 5. Tool Schema Bloat
Hermes Agent allows only ONE external memory provider at a time. Adding a plugin also adds its tool schemas to every model call — a hidden context cost.

## Decision Framework for Igor OS

```
Current state: built-in memory + /extract pre-processor
                 ↓
Is memory retrieval failing? (can't find known facts)
  NO → Stay. /extract handles quality.
  YES → Is the problem language mismatch?
         YES → Try storing in query language first (extract pitfall)
         NO → Is the problem semantic relevance?
               YES → Add vector search (mem0 or Mnemosyne)
               NO → Is context too large?
                     YES → Add auto-compaction tuning
                     NO → Consider Obsidian for human review
```

## Key Takeaway

The `/extract` pre-processor approach (filter before storage) is what power users converged on — they just do it manually or via prompt tuning. Igor OS's `/extract` skill formalizes this.
