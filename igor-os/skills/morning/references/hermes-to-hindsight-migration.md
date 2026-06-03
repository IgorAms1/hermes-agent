# Hermes Memory → Hindsight Migration

## When To Use

When Hermes memory (`MEMORY.md` + `USER.md`) hits >85% capacity and durable context needs to be offloaded to Hindsight (vectorize-io) for long-term storage.

## Process

### Step 1: Audit both stores

Read both memory files to see what's there:

```bash
cat ~/.hermes/memories/MEMORY.md
cat ~/.hermes/memories/USER.md
```

Also check what's already in Hindsight via `hindsight_recall` to avoid duplicates.

### Step 2: Categorize entries

**GOES TO HINDSIGHT** (durable context, not needed every turn):
- Project details (Semaphore team/positioning/pricing, partner handling rules)
- Therapy reframes and personal insights (rest/permission reframe, shame-paralysis)
- Historical context (Cloudflare interview impact, Чай death)
- Energy patterns (Semaphore gives energy, Jamf drains)
- Technical lessons (Docker port security, ritalin hyperfocus pattern)
- Future interests (MCP, Hermes token optimization)
- User preferences that are situational, not operational

**STAYS IN HERMES** (operational guardrails, needed every turn):
- Style/communication preferences (tone, zero sycophancy, format rules)
- SYSTEM TIME / date anchoring rules
- Known bugs (first letters truncation)
- Key people identifiers (Vitalik, Vera, Jack, Welat, Sveta, Oleg)
- Infrastructure quick-references (Whoogle port, Hindsight localhost)
- Active project scope (compact pointer to Hindsight)
- Memory policy itself

### Step 3: Bulk export to Hindsight

Group related facts and store each group as one `hindsight_retain` call with tags:

```python
hindsight_retain(content="...", context="category label", tags=["tag1","tag2"])
```

Batch parallel calls to speed up the process.

### Step 4: Clean Hermes memory

Use `memory(action='replace', old_text, new_text)` to compress bulky entries.
Use `memory(action='remove', old_text)` to delete entries now in Hindsight.

Target: under 50% capacity to leave room for new operational context.

### Step 5: Verify

Check final memory usage percentage in the system prompt header.
