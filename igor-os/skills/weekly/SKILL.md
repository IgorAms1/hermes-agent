---
name: weekly
description: Igor OS weekly review across work, Dutch, health, relationship, hobbies, patterns, priorities, stop, double down, and next-week constraints.
version: 1.1.0
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

## Pre-Flight: Recent Week Recall

Before producing a weekly review, gather evidence:

1. Call `session_search` with no query and `limit: 5` to inspect recent sessions.
2. Call `session_search` with a broad query like:
   `weekly OR week OR done OR completed OR сделал OR завершил OR тренировка OR Dutch OR work OR Semaphore OR Jamf OR Nastya OR relationship OR MTB OR BJJ`
   with `role_filter: "user,assistant"`, `limit: 5`.
3. If Igor asks to recover a missed `/weekly`, treat it as a backfill: search the target date range explicitly, include cron/session summaries if available, and state briefly why the review was missed only if evidence shows it.
4. Carry forward only confirmed unfinished items. If Igor said something was done, it is done.
5. Scan memory exclusions before assigning work tasks: do not add ASBIS or Salesforce lead visibility unless Igor explicitly brought them up.

Reference: `references/backfill-missed-weekly.md` contains the recovery pattern for a missed weekly review.

## Procedure

1. Define the date range.
2. Extract evidence by area: work, Dutch, health/training, relationship/home, hobbies/recovery, systems.
3. Separate events from patterns.
4. Identify wins, avoided problems, unresolved loops, and energy drains.
5. Pick top 3-5 priorities for next week.
6. Choose one thing to stop and one thing to double down on.
7. End with a practical first Monday move.

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

## Validation Checklist

Before finalizing:

- Are priorities based on recent evidence, not hallucinated continuity?
- Did we avoid reassigning completed items?
- Did we exclude work items Igor marked as someone else's responsibility?
- Are there no more than 5 next-week priorities?
- Is there one concrete first move, not a vague intention?

## Gotchas

- Do not turn the weekly review into a life audit tribunal.
- Do not overfit one bad day into a weekly identity narrative.
- Keep it concise enough for Telegram; save long synthesis to a Markdown report only if Igor asks.
- If data is thin, say so and ask Igor for missing bullets instead of inventing a cinematic arc.
