# Account Notes — Partner Call Follow-Up Storage

## Problem

After extracting a partner call transcript, the default action is to dump every identified follow-up into Igor's daily todo. This creates overwhelm, CRM-dread, and eventually the whole account context gets lost because each item was a tiny todo that got cancelled.

## Solution

Store extracted partner/account context as **account notes** in `igor-os/accounts/<account-slug>.md`, not in daily todo.

## When to use

- Igor says "не выдавай мне все эти задачи каждый день" or similar sentiment after a partner call extract.
- The extracted items are medium-term (next call, next week, end of quarter) rather than "do today".
- The items are prep/context for the *next* call, not actions Igor must execute *right now*.

## When NOT to use

- The item is a real, concrete action for today (e.g., "send this email right after the call", "update CRM now").
- Igor explicitly asks to add something to his todo list.

## Procedure

1. After extracting a partner call, group extracted items:
   - **Today actions** (max 1-2) — add to daily todo.
   - **Next-call prep** — store in account note.
   - **Background / FYI** — store in account note, tagged as background.

2. Account note structure:
   ```markdown
   # <Partner name> — account notes
   Last updated: YYYY-MM-DD
   
   ## Pipeline / opportunities
   - topic — status — prep reminder
   
   ## Product / process guidance covered
   - fact or instruction
   
   ## Portal feedback to collect / escalate
   - item
   
   ## Partner enablement / training status
   - item
   
   ## How to use this note
   When Igor says he has a call: ask type of call, surface 3-5 relevant topics,
   split into: must raise / optional / background.
   ```

3. Surface rules:
   - On next call mention, ask what kind of call (pipeline, enablement, portal feedback, QBR, quick sync).
   - Show 3-5 topics max, split by priority.
   - Do not dump everything.
   - Convert an item to daily todo only when Igor explicitly asks.

## Example

See `igor-os/accounts/logicworks.md` for a worked example.

## Pitfalls

- Easy to revert to "just add to todo" out of habit. The account note replaces the todo for partner-specific items.
- Account notes can accumulate stale topics. If a topic is >2 months old and Igor never raised it, it's probably dead — don't auto-surface.
- One account note per partner, not per call session. Update the same file.