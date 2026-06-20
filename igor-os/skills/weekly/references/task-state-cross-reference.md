# Weekly Review: Task-State Cross-Reference

Session-derived lesson: when a weekly review includes workstreams that have a live external task system, raw chat logs are not enough for next-week priorities.

## Why

Igor often discusses work items in Telegram as ideas, call notes, reflections, or raw inbox material. Some of those later become active tasks, waiting items, backlog, or completed items in Obsidian. A weekly review should not infer current task status from chat alone when a task-state file exists.

## Current Semaphore pattern

For Semaphore work:

1. Run the mandatory raw recall first:
   `python3 ~/.hermes/scripts/session_week_summary.py --days=7`
2. Search sessions for work/Semaphore evidence.
3. If Semaphore appeared, use the `read-semaphore-tasks` skill or run:
   `~/bin/hermes_read_tasks.sh`
4. In the review, separate:
   - what happened this week from raw logs;
   - what is currently active/waiting/backlog from Obsidian;
   - Hermes's recommendation for next week.
5. Do not promote inbox notes or chat ideas into "active tasks" unless the task file has done so.

## Pitfalls

- Do not carry forward a task just because it appeared in a call note; check whether it is active, waiting, backlog, or completed.
- Do not treat prior morning/evening summaries as source-of-truth for task status.
- Do not mention absent personal-task sections in a work-only summary unless relevant to the weekly review.
- If the read script fails, say task-state could not be verified and base priorities on raw logs with that caveat.