# Igor OS Midday Heartbeat (14:30 CEST)

## Cron Configuration

- **Name:** Igor OS Midday Heartbeat
- **Job ID:** f50ce49f0509
- **Schedule:** `30 12 * * *` (12:30 UTC → 14:30 CEST)
- **Deliver:** telegram:1321905
- **Model:** inherits default (deepseek-v4-flash)

## Purpose

Proactive mental health pulse check that Igor does NOT have to initiate. Unlike morning/evening captures (task-oriented), the heartbeat is pure state-checking:

- No session search
- No task analysis
- No todo/action items
- 3-4 lines max
- Direct, warm, grounding tone
- One tiny physical suggestion (water/breathe/stretch)
- No questions about work

## Trigger Pattern

The heartbeat runs daily at 14:30 CEST (Igor's preference — originally 13:00, moved to 14:30). It fires regardless of whether Igor is already chatting with the agent. If Igor is mid-conversation when the heartbeat arrives, he may ignore it or reply briefly — that's fine.

## Interaction with Evening Capture

The evening capture (18:00 CEST) should:
1. Check if the heartbeat ran today
2. If Igor responded with his state in the heartbeat, reference it: "в heartbeat ты говорил что [state] — как сейчас?"
3. If Igor didn't respond to the heartbeat, don't re-pulse — go straight to facts
4. Never duplicate the pulse check; build on it

## Background

Created 19 May 2026 after Igor's sick day where shame spiral about Claude limits → PMЖ anxiety → feeling "волшебно" after a good call showed the value of proactive check-ins. Experiment first ran as a one-shot at 17:45 CEST, then promoted to daily at 14:30 CEST.
