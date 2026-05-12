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

## Inputs

Use the current date, available memory/context, and any priorities Igor provides in the message. If priorities are missing, infer cautiously from recent context and mark assumptions.

## Output

Keep it concise:

```text
Morning Brief - <date>

Work priorities
1.
2.
3.

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
