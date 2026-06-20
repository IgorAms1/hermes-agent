---
name: weekly
description: Igor OS weekly review across work, Dutch, health, relationship, hobbies, patterns, priorities, stop, double down, and next-week constraints.
version: 1.3.0
metadata:
  hermes:
    category: igor-os
---

# Weekly Review

## When To Use

Use for `/weekly`, Sunday/Monday planning, or when Igor asks to synthesize the last week and choose next-week priorities.

## When Not To Use

- Daily planning → use `morning`.
- Single avoided task → use `avoidance`.
- Work-only strategy → use `work`.
- Emotional raw dump that needs extraction first → use `extract`, then summarize.

## Pre-Flight: Recent Week Recall — Source Primacy Rule ⚠️

**Never use your own prior cron summaries (evening captures, morning briefs, prior weekly reviews) as the primary source for what happened.** Your summaries are interpretations — they contain errors (wrong attributions, missed details, inverted facts). The raw session files are the ground truth.

**Mandatory first step:** Run `python3 ~/.hermes/scripts/session_week_summary.py --days=7` to extract user messages by day from JSONL session files. This gives you Igor's actual words with timestamps, not your summary of them.

**Then** cross-reference key claims (who reminded whom, who called whom, what was done vs planned) against the raw user messages. If your prior summary says X but the user message says Y, trust the user message. Only after raw extraction, consult your prior cron summaries as a secondary hint.

**Why this rule exists:** Igor caught me inverting the direction of a reminder (Basalt call — he reminded me, not vice versa) and glossing over Pn/Vt because I only skimmed my brief summaries instead of reading the packed session files.

### Additional recall steps

After the source primacy check, search for additional material:

1. Call `session_search` with a broad query like:
   `weekly OR week OR done OR completed OR сделал OR завершил OR тренировка OR Dutch OR work OR Semaphore OR Jamf OR Nastya OR relationship OR MTB OR BJJ`
   with `role_filter: "user,assistant"`, `limit: 5`.
2. If Igor asks to recover a missed `/weekly`, treat it as a backfill: search the target date range explicitly, use the session_week_summary.py script as primary source, include cron/session summaries only as secondary hints.
3. Carry forward only confirmed unfinished items. If Igor said something was done, it is done.
4. **Scan for daily streaks explicitly** — search for mentions of meditation (20 min), chess (streak count + days), mobility/Julia Reppel, reading (Liberated Mind, Promise at Dawn). These are high-signal wins Igor expects to see in the review. If they happened every day, say «каждый день» — not just «было». Check each day of the week individually — don't assume if Monday had meditation that Tuesday automatically did.
5. **Scan for ideas and insights explicitly** — Igor often shares innovations, integrations, re-framings, and realizations during the week (e.g., Claude+DOMO integration idea, Garmin data MVP, LinkedIn cleanup, anti-temny-yakor, Cloudflare re-framing as growth). These are not task completions and will not match «сделал/завершил/отправил». Search for terms like: `идея OR мысль OR инсайт OR понял OR осознал OR integration OR MVP OR build OR built OR Claude OR Garmin OR insight OR reframe`. If you do not find them via keywords, scan user messages manually — Igor drops major insights in voice transcriptions that keyword search may miss.
6. **Cross-reference evening little wins** — evening captures often record small wins (a fixed thing, a repaired item, a conversation, a moment with Nastya, a household task). Search for things like: `победа OR win OR сделал OR починил OR убрал OR купил OR приготовил OR записал OR отправил OR помыл OR загрузил`. These are easy to miss and important to Igor.
7. **Second-pass fallback:** If after the first pass the review feels thin (fewer than ~15 items across all categories), do a second pass manually reading user messages from the week's sessions. The first pass often misses voice-transcribed material, small household wins, and insights that don't match keyword patterns.
8. Scan memory exclusions before assigning work tasks: do not add ASBIS or Salesforce lead visibility unless Igor explicitly brought them up.
9. **Cross-reference current task-state before setting next-week work priorities.** If Semaphore, Obsidian, active tasks, P0s, GTM, partner calls, or deal work appeared in the week, load/use `read-semaphore-tasks` (or run `~/bin/hermes_read_tasks.sh`) after raw recall. Use the task file to distinguish active/waiting/backlog/completed items. Do not carry forward work priorities only from chat memory or old summaries when the Obsidian task-state is available.
10. **Scheduled delivery discipline:** if `/weekly` runs as a cron job with auto-delivery, produce the review as the final response only. Do not call `send_message`. Use `[SILENT]` only when raw logs genuinely show nothing new; a thin week is still a report, not silence.

References:
- `references/backfill-missed-weekly.md` — recovery pattern for a missed weekly review
- `~/.hermes/scripts/session_week_summary.py` — extract user messages by day from raw session files. Run before every multi-day summary.
- `read-semaphore-tasks` skill / `~/bin/hermes_read_tasks.sh` — current Semaphore task-state for next-week work priorities.
- `references/task-state-cross-reference.md` — pattern for combining raw weekly logs with Obsidian task-state without hallucinating task status.

## Procedure

1. Define the date range.
2. Extract evidence by area: work, Dutch, health/training, relationship/home, hobbies/recovery, systems.
3. Separate events from patterns.
4. Identify wins, avoided problems, unresolved loops, and energy drains.
5. **Explicitly check daily streaks** — did meditation, chess, mobility, reading happen every day? Capture the streak count if available.
6. **Explicitly check ideas/insights** — any integration attempts, frameworks coined, re-framings (Cloudflare, anti-dark-anchor, etc.). These are often the most valuable content of the week.
7. Pick top 3-5 priorities for next week.
8. Choose one thing to stop and one thing to double down on.
9. End with a practical first Monday move.

## Output

```text
Weekly Review - <date range>

Biggest wins
-

Avoided problems
-

Work/career progress
-

Dutch progress
-

Health/training status
-

Relationship/home status
-

Hobby/recovery notes
-

Patterns noticed
-

Top 5 priorities for next week
1.
2.
3.
4.
5.

One thing to stop doing
-

One thing to double down on
-

First move next week
-
```

**Format rule for this user:** Err on the side of comprehensive. Igor's stated preference is «давай тогда полный список одним сообщением» — he wants to see everything collected so he can calibrate his own perception of the week. A too-short review upsets him more than a too-long one. Include all categories, all found items, all streaks, all insights. Only omit things he explicitly said were not relevant. The "Telegram-first" rule (short messages) is overridden for weekly reviews.
```

## Validation Checklist

Before finalizing:

- Are priorities based on recent evidence, not hallucinated continuity?
- Did we avoid reassigning completed items?
- Did we exclude work items Igor marked as someone else's responsibility?
- Are there no more than 5 next-week priorities?
- Is there one concrete first move, not a vague intention?
- **Did we include daily streaks?** (meditation every day, chess N-day streak, mobility each morning)
- **Did we include ideas and insights from the week?** (integration attempts, frameworks, re-framings — not just task completions)
- **Are voice-transcribed insights captured?** Igor often drops key innovations in voice messages, not text. If your sources were only text, you may have missed the most valuable material.

## Gotchas

- Do not turn the weekly review into a life audit tribunal.
- Do not overfit one bad day into a weekly identity narrative.
- Keep it concise enough for Telegram; save long synthesis to a Markdown report only if Igor asks.
- If data is thin, say so and ask Igor for missing bullets instead of inventing a cinematic arc.
- **Do not forget daily streaks and ideas.** Igor explicitly noted this as a recurring pain point. Meditation every day, chess streak, mobility, and weekly innovations (integration ideas, frameworks, re-framings) are as important as task completions. Missing them upsets him more than getting a task wrong — because streaks and ideas are identity markers, not todos. Search voice transcriptions manually if keyword search turns up nothing.
