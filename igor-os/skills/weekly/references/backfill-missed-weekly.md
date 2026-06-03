# Backfilling a Missed Weekly Review

Use when Igor says he did not receive `/weekly`, asks to "pull" last week, or requests a historical weekly review.

## Recovery Pattern

1. Determine the intended date range from context. For Monday recovery, default to the previous Monday-Sunday range.
2. Use `session_search` with no query (`limit: 5`) to see recent session IDs and cron sessions.
3. Search explicitly for the date range and known weekly domains:
   - work: `Jamf`, `Semaphore`, partners, calls, CRM
   - personal/home: `Nastya`, cats, errands, birthday, friends
   - health: training, back, kettlebell, mobility, BJJ/MTB
   - learning/hobbies: Dutch, microscopy, kombucha, chess
   - system: memory, skills, Codex, cron
4. **Then search for daily streaks and insights** — these are not task completions and won't match keyword searches. Search for: `медитация OR chess OR streak OR streak OR шахмат OR Julia Reppel OR mobility OR интеграция OR integration OR идея OR insight OR MVP`. Also scan voice transcriptions — Igor's most valuable innovations (Claude+DOMO integration, Garmin analysis, re-framings) often come through voice, not text.
5. Only mark items as pending when the transcript/session summary says they remained pending. If Igor reported completion, do not resurrect it.
6. If evidence shows a delivery failure, mention it in one sentence; do not turn the weekly review into a debugging report.

## Output Adjustment

For backfills, use `Weekly Review — <date range>` and then concise sections. Include:
- biggest wins
- avoided problems
- work/career progress
- Dutch progress
- health/training status
- relationship/home
- hobbies/recovery
- patterns
- top 3-5 priorities for the current week
- one thing to stop
- one thing to double down on
- first move for today/this week

## Pitfalls

- Do not assign stale tasks from automated cron summaries unless they are confirmed unfinished.
- Do not include excluded work areas such as ASBIS or Salesforce lead visibility unless Igor explicitly raises them.
- Do not over-explain the cron/tool failure; Igor asked for the recovered review, not incident management.
