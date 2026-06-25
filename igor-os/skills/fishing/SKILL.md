---
name: fishing
description: Igor OS Amsterdam fishing log mode for structured session capture, patterns, and next-session tests.
version: 1.0.0
metadata:
  hermes:
    category: igor-os
---

# Fishing Log Mode

## When To Use

Use for `/fishing`, Amsterdam fishing session logs, tackle notes, and pattern finding.

## Capture Fields

Ask only for missing fields that matter:

- Location.
- Date/time.
- Weather/wind.
- Water clarity/current.
- Target species.
- Lures/rigs/weights.
- Retrieve/presentation.
- Bites/catches/follows.
- Snags/lost tackle.
- Sonar observations if any.
- Lessons learned.

## Voice/STT Handling Pitfalls

Fishing voice notes often mix Russian, English brand names, decimals, lure sizes, and local place names. Treat suspicious STT output as provisional instead of immediately hardening it into a fact.

- Common fragile fields: lure size decimals (`3.8"` vs `7.8"`), brand/model names (`Keitech Swing Impact FAT`), weights (`7 g`), local spots (`Левопарк`), and bite-result verbs (`слетели`, `не засеклись`).
- If a transcript contains an unlikely lure size or garbled tackle phrase, repeat back a compact structured draft and ask/allow correction before deriving patterns.
- When the user corrects one field, update the log explicitly and mark the corrected value as authoritative for that session.
- For fishing logs, prefer storing structured corrected facts over raw transcript wording.
- Suggest a short end-of-voice recap for noisy/technical sessions: `место / время / рыба / поклёвки / приманка / вес / что исправить в распознавании`. This is often more effective than trying to make STT perfect.

## Non-Catch Value

Log more than catch count. Quietness, lack of people, feeling safe/usable, renewed taste for fishing, and “this spot feels like mine” are meaningful fishing-session facts. They influence whether a spot is actually repeatable for Igor, not just whether it produced bites.

Also capture **return of fishing drive** and **paths to improvement** as first-class session outcomes. If Igor says he “caught the long-lost passion for fishing” or saw how to improve, log that beside the fish: what technique/presentation he wants to study next (e.g. jig rig, jig, free rig), what changed in confidence, and what next experiment follows. This is useful because the session’s value may be rekindled motivation + a learning direction, not only the zander.

## Output

```text
Structured log
-

Pattern hypotheses
-

Next session recommendation
-

What to test next
-
```

Be empirical. Label hypotheses as hypotheses.
