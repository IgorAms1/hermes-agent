# Personal AI operating layer patterns

Use this reference when auditing or designing a private personal agent like Hermes / Igor OS: messaging-first UI, memory, routines, tools, research, and life/work workflows.

## Core conclusion

Do not optimize first for “more autonomy.” Optimize for a bounded personal operating layer:

1. Capture with minimal friction.
2. Clarify into next actions, references, decisions, logs, or research questions.
3. Act safely via typed tools and approval gates.
4. Review, learn, and evaluate usefulness.

For Igor OS specifically, the loop that is proving useful is:

```text
Morning plan → situation capture → small wins → evening reflection → weekly synthesis → adjusted next cycle
```

This works because it creates visible evidence of movement: small wins stop disappearing, days stop feeling like they evaporated, and weekly review turns scattered actions into a trajectory. This is more useful than abstract motivation.

The agent should be a trusted execution scaffold, not a clever oracle or elegant procrastination machine.

## Recommended architecture

```text
Messaging input
→ intent/router
→ policy/permission check
→ relevant skill + memory retrieval
→ workflow graph / durable job state
→ typed tool calls
→ verification
→ memory write candidate
→ response/notification
→ trace/eval log
```

Key design choices:

- Messaging app is the remote control, not the secure data substrate.
- Local/private memory is the source of truth for sensitive personal context.
- Skills/playbooks hold procedural memory; durable memory stores facts/preferences.
- Workflows should be explicit, inspectable, and resumable.
- Observability is part of the product, not an admin afterthought.

## What “good” looks like

- Mode-based UX: morning, evening, work, research, mindmap, avoidance/admin rescue, relationship, training, weekly review.
- Sparse durable memory with source, timestamp, confidence, sensitivity, and status.
- Local research/mindmap artifacts instead of losing outputs in chat.
- Approval gates for external, destructive, costly, emotional, legal, financial, health, or work-stakeholder actions.
- Weekly usefulness review: did the agent reduce friction or create polished avoidance?

## Common failure modes

- Treating Telegram/chat as the privacy boundary.
- Building one giant autonomous loop instead of bounded workflows.
- Saving too much automatic memory without review/delete controls.
- Letting scheduled jobs become prompt-cron without state, retries, last output, and failures.
- Overusing multi-agent theatre before a single-agent workflow fails measurable evals.
- Measuring activity volume instead of task completion, trust, and reduced cognitive load.

## Autonomy matrix

No approval usually needed:

- Summarize notes.
- Draft private content.
- Search/read non-sensitive local context when relevant.
- Log workouts/interactions.
- Produce research reports/mindmaps.
- Suggest next actions.

Approval required:

- Send messages.
- Publish/share documents.
- Modify shared/external systems.
- Delete files, logs, notes, or memories.
- Create calendar commitments involving others.
- Spend money.
- Submit forms or contact institutions.
- Store highly sensitive memory permanently.

Double approval recommended:

- Relationship messages with emotional stakes.
- Financial/legal/admin submissions.
- Irreversible deletion.
- Public posts.
- Work communications to senior stakeholders, partners, or customers.
- Sharing private logs with anyone.

## Control-plane features to add early

- `/status`: active jobs, routines, open loops.
- `/jobs`: schedule, last run, next run, failures, last output.
- `/memory`: categories, recent changes, stale candidates.
- `/forget`: delete/archive memory by query or id.
- `/approve`: pending actions.
- `/sources`: sources used in last research/answer.
- “What memory did you use?”: cited memory snippets or “none.”

## Memory states

Use explicit lifecycle states:

- `candidate`: proposed by model, not accepted.
- `active`: durable and normally usable.
- `stale`: likely outdated; verify before using.
- `archived`: retained locally but not injected by default.
- `deleted`: removed or tombstoned depending on audit requirements.

## Weekly evaluation prompts

Rate 1–5:

- Helped me focus.
- Reduced cognitive load.
- Helped me act, not just think.
- Respected privacy boundaries.
- Interrupted appropriately.
- Made the system simpler.
- Helped with avoided tasks.

Count:

- Important tasks completed.
- Admin tasks unblocked.
- Research questions answered.
- Suggestions ignored.
- Agent interruptions.
- Approval requests.
- Corrections needed.
- Mistakes/hallucinations.
- Time saved.
- Time wasted.

Kill rule: if a routine creates noise for two consecutive weeks, pause or rewrite it.

## Source anchors

- Anthropic, Building effective agents: workflow-first patterns, routing, evaluator loops.
- LangGraph: durable execution, persistence, human-in-loop workflows.
- OpenAI tools/function calling/evals: typed tools and evaluation.
- MemGPT / Letta: explicit memory hierarchy for stateful agents.
- OpenAI memory controls: saved memory vs chat history, view/delete controls.
- OWASP LLM Top 10: prompt injection, sensitive disclosure, excessive agency.
- Google PAIR + Microsoft Human-AI Interaction Guidelines: user control, correction, transparency.
