---
name: evening
description: Igor OS evening capture for daily logs, patterns, follow-ups, memory candidates, and tomorrow's task.
version: 1.0.0
metadata:
  hermes:
    category: igor-os
---

# Evening Capture

## When To Use

Use for `/evening` or daily shutdown logging.

## NEVER SILENT

This is non-negotiable. **You must always deliver a response.** Even if Igor hasn't answered the capture questions yet, send the questions. Even if there's "nothing new," send a brief summary of what was already known and ask if anything changed. Never respond with [SILENT] or skip delivery. The evening cron is the last checkpoint of the day — if you go silent, task completions and corrections are lost.

## Pre-Capture Search (mandatory)

Before asking any questions, first scan the current visible Telegram conversation for updates Igor already mentioned. Then use `session_search` for prior sessions or same-day sessions that may have reset:

1. Call `session_search` with `query: "completed OR done OR finished OR отправил OR завершил OR сделал OR закрыл"`, `role_filter: "user,assistant"`, and `limit: 5`.
2. Call `session_search` with `query: "tomorrow OR завтра OR перенос OR cancel OR отмена"`, `role_filter: "user,assistant"`, and `limit: 5`.
3. Use returned timestamps and summaries to keep only today's relevant updates.
4. If summaries are too compressed OR keyword searches return only older sessions (same-day indexing lag), fall back to direct session file extraction: use `execute_code` to list `$HERMES_HOME/sessions/` (usually `~/.hermes/sessions/`) for today's date prefix, then `read_file` to pull content from each matching JSONL file. Extract user messages with the pattern in `references/session-jsonl-parsing.md`. This is more reliable than delegate_task, which can time out at 600s.

Voice transcriptions are often buried in user messages that summaries compress.

## Pitfalls

- **Cron delivery target must be specific.** If setting up the evening cron, `deliver` must be `telegram:<chat_id>` (e.g., `telegram:1321905`), not bare `telegram`. Bare platform name causes silent delivery failure with `no delivery target resolved for deliver=telegram`. Combined with the NEVER SILENT rule above, this is a hard requirement for the cron to actually reach Igor.
- **Voice transcription errors are common.** Cross-reference transcribed names against known context in memory.
- **`session_search` may miss same-day sessions.** The FTS index may not have ingested today's sessions yet when the evening cron fires. If keyword searches return only older sessions, fall back to direct file listing: list `$HERMES_HOME/sessions/` (usually `~/.hermes/sessions/`) for today's date prefix (`YYYYMMDD*`), then use `execute_code` + `read_file` to extract user messages from those JSONL files. See `references/session-jsonl-parsing.md` for the reliable extraction pattern.
- **`delegate_task` can time out on session extraction.** The 600s timeout makes delegate_task unreliable for crawling session files. Prefer the direct `execute_code` + `read_file` + regex approach documented in `references/session-jsonl-parsing.md` instead of step 4's fallback to delegate_task.

## Optional Philosophical Reflection

When Igor asks for existentialist/philosophical reminders, or when a day needs a values-based reflection, add one short optional `🌙 Вечерний вопрос` block. It must support closure, not rumination: 1 gentle question + 1 fact/lesson/next-step closure. Do not use it daily by default; 2–3 times/week is enough. Avoid heavy death/absurdity/guilt framing on low-mood or anxious days.

Reference prompt bank: `references/existentialist-evening-prompts.md`.

## Existential Reflection MVP

Igor approved a 2-week MVP for adding existentialist prompts to morning/evening briefings.

For evening capture, include an existential reflection question **about 2 times per week**, not necessarily every day. If the day sounds emotionally heavy, use a soft grounding/closure question instead.

Purpose: honest reflection, closing loops, and extracting one lesson without rumination or self-punishment.

Rules:
- Keep it to maximum 2 lines.
- Ask one question only. Do not add a lecture.
- Always bias toward closure: one fact, one lesson, one next step, or one thing to release.
- Avoid making the evening into a tribunal. Responsibility is useful; self-prosecution is not.
- Avoid heavy death/absurdity prompts unless Igor explicitly asks for that tone.

Good evening patterns:
- `🌙 Вечерний вопрос: где сегодня был один момент выбора, а не автопилота?`
  `✅ Закрытие: назови один факт без оценки.`
- `🌙 Вечерний вопрос: что сегодня было маленьким, но настоящим?`
  `✅ Закрытие: оставь это как достаточно хорошее.`
- `🌙 Вечерний вопрос: где сегодня ты уменьшил хаос хотя бы немного?`
  `✅ Закрытие: один факт, один урок, один следующий шаг.`
- `🌙 Вечерний вопрос: что можно отпустить до завтра?`
  `✅ Закрытие: не превращай вечер в трибунал — просто закрой одну петлю.`

Grounding substitute for low mood / anxiety:
- `🌙 Вечерний вопрос: что сегодня помогло хотя бы на 5%?`
  `✅ Закрытие: достаточно одного факта, без оценки всей жизни.`

Full prompt library lives at:
`/home/igor1/hermes-agent/research/2026-05-17-existentialist-briefing-prompts/report.md`

## Procedure

Acknowledge what Igor already reported during the day, then ask only the remaining questions:

- What mattered today?
- What did you avoid?
- What did you learn?
- Any work, partner, or interview notes to remember?
- Any Dutch words or phrases from today?
- Any health, training, fishing, MTB, BJJ, microscopy, or relationship notes?

When Igor answers, summarize into:

```text
Daily log
-

Patterns
-

Follow-ups
-

Durable memory candidates
-

Suggested task for tomorrow
-
```

Follow `context/memory-policy.md`. Ask before storing sensitive or work-related memory.
