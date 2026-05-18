---
name: morning
description: Igor OS morning brief with work priorities, Dutch, health, home, recovery, and a win condition.
version: 1.0.0
metadata:
  hermes:
    category: igor-os
---

# Morning Brief

## When To Use

Use for `/morning` or when Igor asks for a daily briefing.

## Pre-Flight: Yesterday's Session (mandatory)

Before generating the brief, recall yesterday's relevant updates with tools that exist in Hermes:

1. Call `session_search` with no query and `limit: 5` to list recent sessions. Use the returned timestamps to identify sessions from yesterday or the latest prior Telegram session.
2. Call `session_search` with a broad query such as `completed OR done OR finished OR отправил OR завершил OR сделал OR закрыл OR tomorrow OR завтра OR перенос OR cancel OR отмена`, `role_filter: "user,assistant"`, and `limit: 5`.
3. If summaries are too compressed, use `delegate_task` with `toolsets: ["terminal", "file"]` and context pointing to `$HERMES_HOME/sessions/` plus the relevant session id. Ask it to extract only user-reported completions, priorities for today, and corrections.
4. Only carry forward items that are **confirmed unfinished** — if Igor said he did it, it is done.

Skip this and you will assign him tasks he already closed.

## Inputs

Use the current date, available memory/context, and any priorities Igor provides in the message. If priorities are missing, infer cautiously from recent context and mark assumptions.

**Before outputting work priorities, check memory exclusions.** Scan the memory/user-profile blocks already injected into context for entries with "NOT", "don't assign", "not my", "не моя", or "не назначай". If the injected memory is insufficient and file tools are available, read `$HERMES_HOME/memories/MEMORY.md` and `$HERMES_HOME/memories/USER.md`; otherwise use `session_search` with those terms plus known risky entities such as ASBIS or Salesforce. Filter out tasks Igor explicitly flagged as someone else's responsibility.

## Iterative Build

The morning brief is rarely one-shot. Igor typically sends multiple voice notes adding tasks, times, and corrections. Expect to:
- Receive 3–6 follow-up messages refining the brief
- Provide a "full morning view" on request (consolidated, clean)
- Track task completion throughout the morning with ✅/🔲 status

## Pitfalls

- **Check memory exclusions before generating work priorities.** Memory contains explicit "not my partner / not my task" entries. Never infer action items for things Igor has flagged as someone else's responsibility. If Igor asks to remove an excluded entity from the visible brief, keep filtering it silently and do **not** mention the exclusion by name in future morning outputs unless he brings it up.
- **Voice transcription errors are common.** Cross-reference transcribed names against known context in memory (e.g., "Jump Sales Academy" → Jamf Sales Academy, "bottles" → bowls). If a transcribed word doesn't match any known entity but sounds similar to one, use the known entity.
- **Don't infer tasks from previous session context that Igor hasn't confirmed.** Only carry forward items Igor explicitly mentions or that are clearly unfinished from yesterday.
- **Cron delivery target must be specific.** If setting up the morning cron, `deliver` must be `telegram:<chat_id>` (e.g., `telegram:1321905`), not bare `telegram`. Bare platform name causes silent delivery failure with `no delivery target resolved for deliver=telegram`.
- **Memory near capacity.** When memory usage exceeds ~85%, offer Igor a structured prune: present all entries tagged as remove/compact/keep, get approval, batch execute. To expand limits instead: `hermes config set memory.memory_char_limit <N>` and `hermes config set memory.user_char_limit <N>`. Full pruning methodology in `references/memory-management.md`.

## Optional Philosophical Focus

When Igor asks for existentialist/philosophical reminders, or when a values-to-action nudge would help, add a short optional `🧭 Фокус` block. It must be practical, not decorative: 1 compact thought + 1 concrete action/choice for 10–25 minutes. Do not use it daily by default; 2–4 times/week is enough. Avoid heavy doom, guilt, or “total responsibility” framing, especially on low-mood/anxious days. Use grounding prompts instead.

Reference prompt bank: `references/existentialist-briefing-prompts.md`.

## Optional Usage / Budget Telemetry

When Igor asks to include Codex/OpenAI credit, cost, limits, or remaining-budget reporting in the morning flow, use `references/openai-costs-report.md`. Important distinction: Codex UI limits/remaining percentages are **not** the OpenAI organization costs API. For ChatGPT/Codex 5h/weekly remaining limits, use the Hermes account-usage path or `scripts/codex_limits_report.py`. Default preference: a separate morning Telegram cron instead of bloating the main `/morning` brief, unless Igor explicitly wants it embedded. Keep any embedded usage/cost line compact.

## Existential Focus MVP

Igor approved a 2-week MVP for adding existentialist prompts to morning/evening briefings.

For morning briefings, include this block **about 3 times per week**, not necessarily every day. If unsure whether to include it today, include it unless the brief is already overloaded.

Purpose: translate existentialist ideas into agency and action, not decorative philosophy.

Rules:
- Keep it to maximum 2 lines.
- Always include a behavioral tail: one concrete 10-25 minute step, chosen task, or reduced-friction action.
- Tone: direct, light, non-moralizing. No doom, no guilt, no grand metaphysics before coffee.
- Avoid heavy prompts when sleep/mood looks bad, anxiety is high, or the day needs stabilization. Use a grounding prompt instead.
- Do not use philosopher names unless useful; the prompt should work even without attribution.

Good morning patterns:
- `🧭 Фокус: Смысл сегодня не нужно найти целиком — его можно немного сделать.`
  `➡️ Практический перевод: выбери один 15-минутный шаг в сторону важного.`
- `🧭 Фокус: Свобода сегодня — это выбрать следующий шаг, а не идеальную жизнь.`
  `➡️ Практический перевод: какой шаг уменьшит хаос?`
- `🧭 Фокус: Время ограничено — поэтому не всё заслуживает твоего внимания.`
  `➡️ Практический перевод: что сегодня можно не делать?`
- `🧭 Фокус: Неидеальное действие часто честнее идеального плана.`
  `➡️ Практический перевод: сделай черновую версию на 10 минут.`

Grounding substitute for low mood / anxiety:
- `🧭 Фокус: Сегодня не нужно доказывать смысл жизни. Нужно бережно пройти следующий метр.`
  `➡️ Практический перевод: вода, еда, душ, сообщение человеку или один простой шаг.`

Full prompt library lives at:
`/home/igor1/hermes-agent/research/2026-05-17-existentialist-briefing-prompts/report.md`

## Output

Keep it concise:

```text
Morning Brief - <date>

Work priorities
1.
2.
3.

Personal tasks
- (non-work errands, household, reading, hobbies — Igor always has these)

Dutch micro-task
-

Health/training note
-

Relationship/home note
-

Hobby/recovery suggestion
-

Today's win condition
-
```

## Tone

Direct, practical, and plain. No motivational filler.
