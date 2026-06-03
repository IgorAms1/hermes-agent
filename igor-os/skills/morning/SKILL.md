---
name: morning
description: Igor OS morning brief with work priorities, Dutch, health, home, recovery, and a win condition.
version: 1.10.0
metadata:
 hermes:
 category: igor-os
---

# Morning Brief

## When To Use

Use for `/morning` or when Igor asks for a daily briefing.

## Pre-Flight: Yesterday's Session + Hindsight (mandatory)

Before generating the brief, recall yesterday's relevant updates AND Hindsight durable facts:

### A) Session search (standard)

1. For a quick lookup, call `session_search` with no query and `limit: 5` to list recent sessions. Use the returned timestamps to identify sessions from yesterday or the latest prior Telegram session.
2. For broad morning recall, prefer the deterministic extractor instead of chaining many `session_search` calls:
   ```bash
   /home/igor1/hermes-agent/igor-os/scripts/session_extract.py --date yesterday --roles user,assistant --query "completed OR done OR finished OR отправил OR завершил OR сделал OR закрыл OR tomorrow OR завтра OR перенос OR cancel OR отмена OR забыл OR коррекция OR correction OR поправка OR неверно OR неправильно" --limit 12 --max-chars 350 --pretty
   ```
3. Use `session_search` only when you need to scroll a specific known session, and obey the session-local ID guard in Pitfalls below.
4. Only carry forward items that are **confirmed unfinished** — if Igor said he did it, it is done.
5. **CRITICAL: Do NOT include a "Corrections" / "Коррекции" section in the brief.** If extraction/session_search finds corrections Igor made to previous briefs (e.g., "Bogdan call was Monday not Thursday"), those corrections have already been applied to the current context. Listing them again is noise. Silently absorb corrections into the correct sections of the new brief without flagging them. The only exception: if Igor gave a correction TODAY (in the current session), acknowledge it once then move on.

### B) Hindsight recall — targeted and bounded

USER.md is now lean (only operational guardrails). Before every brief, pull only the changeable personal context needed for today's sections from Hindsight.

Use targeted queries with `n_results: 3` by default:
- `books literature current reading` — only if reading/books may appear in the brief.
- `training health recovery retinol` — for training and health protocols.
- `music hobbies fishing` — only if hobbies/recovery section needs context.
- Partner/project query — only when Igor mentioned a partner/project/person by name today or yesterday.

Prefer direct REST for predictable timeout behavior:

```python
import requests

def recall(query, timeout=10):
    r = requests.post(
        'http://localhost:8888/v1/default/banks/igor-os/memories/recall',
        json={'query': query, 'n_results': 3},
        timeout=timeout,
    )
    r.raise_for_status()
    return r.json().get('results', [])
```

Performance rules:
1. Do not issue broad all-purpose Hindsight queries when the answer is already in injected context or session extraction.
2. Do not batch many recalls if Hindsight is already slow. Run the necessary query first; add optional queries only if the brief needs them.
3. On timeout, retry only the failed query once with `timeout=30`. Do not rerun successful queries.
4. If the retry fails, skip that topic gracefully and continue the brief.
5. Keep only the top 1-3 relevant facts in the final reasoning; do not paste long recall output.

If the client library is needed (e.g., entity extraction), the accessor pattern differs from dict-style:

```python
from hindsight_client import Hindsight
h = Hindsight(base_url='http://localhost:8888')
result = h.recall(query='partner context', bank_id='igor-os')
# NOT result.get('matches') — use result.results (list of fact objects)
for f in result.results[:3]:
 print(f.text[:200])
```

Hindsight stores partner details, call extracts, project decisions, and therapy insights that don't fit in MEMORY.md. If recall returns rich results, reference them in the brief. If Hindsight is down or slow, skip gracefully — don't block the brief.

### C) Cross-reference: hindsight_recall vs session_search corrections

**⚠️ CRITICAL — added 31 May 2026 after Igor caught stale facts in the brief.**

Hindsight stores durable facts, but those facts can go stale (book completed, health test done, project status changed). The session_search from step A catches corrections Igor made ("забыл что X", "ты опять тупишь — я уже дочитал").

After both A and B complete:
1. Scan session_search results for any user messages containing correction signals: "забыл", "неверно", "неправильно", "уже", "ты опять", "коррекция", "поправка"
2. For each correction found, check if a corresponding hindsight entry exists
3. If it does, the hindsight entry is stale — note it for replacement. Do NOT include the stale fact in the brief. The brief should use the CORRECTED fact.
4. If multiple corrections for the same entity (e.g., book status corrected twice), the most recent one wins.

**Common stale scenarios this catches:**
- Book finished but USER.md/hindsight still says "currently reading"
- Task done but tracked as pending
- Health test submitted but still listed as "to do"
- Event date wrong in durable memory

Example: Igor says «Обещание на рассвете я дочитал неделю назад — ты опять тупишь». session_search catches "дочитал" + "ты опять тупишь". hindsight_recall might return "currently reading Обещание". Cross-reference flags the contradiction → session_search wins → brief uses the corrected status.

Skip this: You will assign him completed tasks and suggest books he's already finished.

Skip this and you will assign him tasks he already closed.

## Inputs

Use the current date, available memory/context, and any priorities Igor provides in the message. If priorities are missing, infer cautiously from recent context and mark assumptions.

**Before outputting work priorities, check memory exclusions.** Scan the memory/user-profile blocks already injected into context for entries with "NOT", "don't assign", "not my", "не моя", or "не назначай". If the injected memory is insufficient and file tools are available, read `$HERMES_HOME/memories/MEMORY.md` and `$HERMES_HOME/memories/USER.md`; otherwise use `session_search` with those terms plus known risky entities such as ASBIS or Salesforce. Filter out tasks Igor explicitly flagged as someone else's responsibility.

## Iterative Build

The morning brief is rarely one-shot. Igor typically sends multiple voice notes adding tasks, times, and corrections. Expect to:
- Receive 3–6 follow-up messages refining the brief
- Provide a "full morning view" on request (consolidated, clean)
- Track task completion throughout the morning with / status

## Time-Sensitive Reminders — Critical Step

When Igor lists meetings, calls, or time-bound tasks (in voice messages, text, or follow-ups):

1. **Immediately check current time** via `TZ=Europe/Amsterdam date`
2. **Flag every meeting by its start time** in the response. Structure as a table or bullet list with times.
3. **If a meeting is < 1.5 hours away**, call it out explicitly: «Через N часов — [событие]»
4. **Do NOT assume Igor remembers** his own calendar. He often describes plans verbally without setting phone reminders. Your job is to be the reminder.
5. When he says «запиши» or lists 3-4 items in one message, scan specifically for time-anchored items among the general todos. Separate them visually.

**Common miss:** Igor can describe a full day's plan (errands + calls + meetings) in one voice note and you'll respond with a task list but omit the exact reminder for a call 1.5 hours away. Check every item for a time component.

**Weekend/holiday rule for work items:** If today is Saturday, Sunday, or a known NL public holiday, do NOT surface partner work reminders (CloudFresh, calls, CRM, deal follow-ups, etc.) in the morning brief. Defer them to the nearest workday. See `igor-os-style` skill → "Weekend/Holiday Filter (Cross-Cutting)" for the universal rule.

**Voice note scanning for time anchors:** Igor often sends long voice messages that contain 3-6 items in one flow. Transcriptions may lose the time anchors. After receiving any voice transcription, explicitly scan for:
- Clock times («в 12:30», «в 2»)
- Relative times («через час», «после обеда», «перед звонком»)
- Event names that imply a scheduled time ("meeting with X", "call with Y", "созвон с Z")
- Any item that follows «завтра» or «сегодня» in the same breath as a task

If you find a time anchor, **add it to the visible schedule** with the time, even if it's a quick voice throwaway. Igor may not repeat it.

## Pitfalls

- **USER.md facts go stale — do NOT blindly cite "current status" from memory.** Igor caught me suggesting a book he'd finished a week earlier. USER.md entries are not invalidated when facts change — they persist until explicitly replaced. Before citing any changeable status (book, training program, project stage, health protocol) from USER.md, either: (a) run a quick `session_search(query="дочитал OR закончил OR закрыл OR отправил OR сделал OR завершил", sort="newest", limit=3)` to catch completion signals from the last 7 days, or (b) use `hindsight_recall(query="books training health")` at brief time — Hindsight is the canonical source for changeable context. See memory skill → "Hindsight-First Recall Pattern" and "Fact Lifecycle Maintenance".
- **Check memory exclusions before generating work priorities.** Memory contains explicit "not my partner / not my task" entries. Never infer action items for things Igor has flagged as someone else's responsibility. If Igor asks to remove an excluded entity from the visible brief, keep filtering it silently and do **not** mention the exclusion by name in future morning outputs unless he brings it up.
- **Voice transcription errors are common.** Cross-reference transcribed names against known context in memory (e.g., "Jump Sales Academy" → Jamf Sales Academy, "bottles" → bowls). If a transcribed word doesn't match any known entity but sounds similar to one, use the known entity.
- **Don't infer tasks from previous session context that Igor hasn't confirmed.** Only carry forward items Igor explicitly mentions or that are clearly unfinished from yesterday.
- **Performance: judicious session_search.** Don't search if answer is already in context. Batch independent `session_search` calls in parallel. Prefer `execute_code` for 3+ operations. Over-searching adds latency without value.
- **`session_search` scroll IDs are session-local.** Never reuse `around_message_id` from a prior cron/session. Before any scroll/around lookup, first call `session_search` with no query and `limit: 5`, choose the current target `session_id`, and only use a `message_id` returned from that same session. If the desired `message_id` is absent, skip `around_message_id` and fall back to a normal keyword search with `sort: "newest"`, `role_filter: "user,assistant"`, and a small `limit`. This prevents morning-cron flapping on stale IDs.
- **`execute_code` quoting trap with inline Python.** When calling `terminal("python3 -c \"complex code\"")` from inside `execute_code`, Python string escaping breaks — nested quotes, backslashes, and multiline strings all fail. **Fix:** use `write_file` to save a standalone `.py` script to `/tmp/`, then `terminal("python3 /tmp/script.py")`. This bypasses all quoting issues and makes the code reusable for debugging. Apply this to Hindsight recall, calendar reads, and session file extraction — any multi-line Python that needs `terminal()`. See `evening` skill → `references/session-jsonl-parsing.md` for the session extraction pattern.
- **Cron delivery target must be specific.** If setting up the morning cron, `deliver` must be `telegram:<chat_id>` (e.g., `telegram:1321905`), not bare `telegram`. Bare platform name causes silent delivery failure with `no delivery target resolved for deliver=telegram`.
- **ZWJ emoji trigger cron scanner.** Emoji that use U+200D (Zero Width Joiner) — like 🧘 + female sign, 👨+👩+👧+👦 (compound family) — trip the cron injection scanner (`_CRON_INVISIBLE_CHARS` in `cron/scheduler.py`). Replace with non-ZWJ equivalents: 🧘, 👪. Check ALL skills referenced by cron jobs before deploying emoji in them.
- **Memory near capacity.** When memory usage exceeds ~85%, offer Igor a structured prune: present all entries tagged as remove/compact/keep, get approval, batch execute. To expand limits instead: `hermes config set memory.memory_char_limit <N>` and `hermes config set memory.user_char_limit <N>`. Full pruning methodology in `references/memory-management.md`. For Hindsight migration (offload durable facts, keep only operational guardrails) see `references/hermes-to-hindsight-migration.md`. Memory architecture convention (pointers in memory, details in files) documented in `references/memory-architecture.md`.

- **Cron scanner blocks ZWJ emoji (false positive).** Hermes `cron/scheduler.py::_scan_assembled_cron_prompt` checks the assembled prompt (user prompt + loaded skill content) for invisible unicode characters including U+200D (Zero Width Joiner). Many compound emoji use ZWJ internally — e.g. meditation + female sign (ZWJ-composed) contains U+200D. The scanner has no way to distinguish these from injection payloads. **Fix:** never use ZWJ-based compound emoji in any skill file that runs via cron. Replace with simple emoji (🧘, 👪). After editing, verify with `grep -Pn $'\\u200d' <file>` — no matches means clean. See `references/cron-scanner-invisible-unicode.md` for full mechanism and scanner source.
- **Date anchoring**: always call `TZ=Europe/Amsterdam date` before generating the brief. Igor catches date drift — references like «вчера ты сделал X» must be verified against actual dates, not conversation position.
- **Google Calendar token expires (cron failure).** The `~/.hermes/google_token.json` OAuth token can expire/be revoked, causing the cron brief to fail with `invalid_grant: Token has been expired or revoked`. Detect this by running `setup.py --check` (from `$HERMES_HOME/skills/productivity/google-workspace/scripts/setup.py`). If status is `TOKEN_REVOKED`, re-auth is needed: clean `google_oauth_pending.json` and `google_token.json`, then `--auth-url` → user visits URL in browser → user pastes redirect URL → `--auth-code "URL"` → `--check` to verify. Token auto-refreshes after that until the next revocation. See `references/google-calendar-setup.md` for the full re-auth workflow.

## Calendar Integration — ACTIVE

Igor's Google Calendar is connected through the bundled Google Workspace skill. The morning brief should include a `Сегодня в календаре` section showing events for today.

### How to read calendar

Use the deterministic Google Workspace API script first. Do not write ad-hoc Python that reads `google_token.json` directly unless the script is unavailable and Igor explicitly asks for debugging.

```bash
GAPI="/home/igor1/hermes-agent/venv/bin/python ${HERMES_HOME:-$HOME/.hermes}/skills/productivity/google-workspace/scripts/google_api.py"
$GAPI calendar list --start "YYYY-MM-DDT00:00:00+02:00" --end "YYYY-MM-DDT23:59:59+02:00" --calendar primary --max 25
```

For the morning brief:
1. Get today's date with `TZ=Europe/Amsterdam date`.
2. Use Europe/Amsterdam ISO timestamps with timezone offsets.
3. Parse the JSON list returned by `$GAPI calendar list`.
4. Show only useful fields: time, summary, location, and short notes if present.
5. If the command fails with auth/token errors, mention that calendar is unavailable and use the re-auth notes below. Do not block the whole brief.

This path is preferred because it centralizes token refresh, avoids repeated `execute_code` snippets, reduces latency, and keeps sensitive token handling inside the existing Google Workspace script.

### Token expiry detection and re-auth

The OAuth token can expire or be revoked at any time. Detect with the setup script, not by printing or inspecting token values:

```bash
/home/igor1/hermes-agent/venv/bin/python ${HERMES_HOME:-$HOME/.hermes}/skills/productivity/google-workspace/scripts/setup.py --check
```

If status is `TOKEN_REVOKED` or auth fails, re-auth is needed:
1. Use `references/google-calendar-setup.md` for the full flow.
2. Generate an auth URL with `setup.py --auth-url`.
3. Igor authorizes in browser and returns the redirect URL.
4. Complete with `setup.py --auth-code "URL"`, then verify with `setup.py --check`.

Never print token contents or client secret contents.

### Creating events

Calendar writes are allowed only after explicit user confirmation. Prefer the same deterministic script:

```bash
$GAPI calendar create --summary "Event title" --start "2026-06-18T07:00:00+02:00" --end "2026-06-18T13:00:00+02:00" --calendar primary
```

Before any create/delete, show the exact summary, date, time, calendar, and attendees/location if present, then wait for confirmation. For delete, include the event ID and title.

## Optional Philosophical Focus

When Igor asks for existentialist/philosophical reminders, or when a values-to-action nudge would help, add a short optional ` Фокус` block. It must be practical, not decorative: 1 compact thought + 1 concrete action/choice for 10–25 minutes. Do not use it daily by default; 2–4 times/week is enough. Avoid heavy doom, guilt, or "total responsibility" framing, especially on low-mood/anxious days. Use grounding prompts instead.

Reference prompt bank: `references/existentialist-briefing-prompts.md`.

### Anti-Dark-Anchor / Counter-Evidence Block

When Igor has recently (≤2 weeks) shared durable, self-generated evidence of growth, capability, or system-working — typically following a low/anxious period — include a compact reminder block labeled ` Anti-dark anchor (date):`. Format: 2-4 lines, direct quotes preferred. Purpose: short-circuit the negative-self-narrative loop with Igor's own counter-evidence. Do NOT generate or fabricate evidence — only use material Igor himself reported. If nothing recent or relevant exists, skip entirely.

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
- ` Фокус: Смысл сегодня не нужно найти целиком — его можно немного сделать.`
 ` Практический перевод: выбери один 15-минутный шаг в сторону важного.`
- ` Фокус: Свобода сегодня — это выбрать следующий шаг, а не идеальную жизнь.`
 ` Практический перевод: какой шаг уменьшит хаос?`
- ` Фокус: Время ограничено — поэтому не всё заслуживает твоего внимания.`
 ` Практический перевод: что сегодня можно не делать?`
- ` Фокус: Неидеальное действие часто честнее идеального плана.`
 ` Практический перевод: сделай черновую версию на 10 минут.`

## Daily ACT Touchpoint — REQUIRED (every brief)

Every morning brief MUST include a compact ACT prompt. This is Igor's lightweight daily practice — attached to meditation, like Dutch micro-learning.

Rules:
- One sentence only, never more than 2 lines
- Rotate through core ACT processes: Observing Self, Expansion, Values, Committed Action, Acceptance, Choice Point
- Reference Liberated Mind concepts as they come up (Igor is reading chapter 7+)
- Tone: practical, not poetic. No therapeutic jargon
- Connect to his micro-question «между чем и чем я сейчас выбираю?» when useful

Cross-reference: see `pivot` skill for full ACT intervention patterns (fusion/avoidance/inaction). The morning brief is a single prompt — pivot handles full interventions.

### Rotation bank (seed):

**Observing Self:**
- «Я не равен мыслям. Я — пространство, где они проходят.»
- «Сегодня: заметить 2 мысли и назвать их — без оценки.»
- «Ты не голос в голове. Ты тот, кто слышит этот голос.»

**Expansion / Making space:**
- «Вдох — в место напряжения. Выдох — позволить ему быть.»
- «Не убирать дискомфорт. Сделать ему место.»
- «Тело знает что-то, что ум пока не назвал. Проверить, где отклик.»

**Values / Committed Action:**
- «Сегодня я выбираю двигаться *к*, а не *от*.»
- «В чём я хочу участвовать сегодня — а не что я должен доделать?»
- «Качество моих действий — не их количество.»

**Choice Point:**
- «Между чем и чем я сейчас выбираю? И что выберет тот, кем я хочу быть?»
- «Выбор не между хорошим и плохим. А между важным и срочным.»
- **NEW 29 May:** «Не что я мог бы сделать в идеальном состоянии, а что я реально могу сделать сейчас.»
- **NEW 29 May:** «Достаточно хороший сотрудник — не герой, не спасатель, а тот, кто делает достаточно в текущем состоянии.»

**Murmuration / Perspective (24 May 2026):**
- «Как птицы в рое: не пытайся увидеть всю фигуру. Просто держись ближайших соседей.»
- «Ни одна птица не знает траекторию всего роя. Достаточно знать свой следующий метр.»

**Rest / Recovery reframe (24 May + 29 May 2026):**
- «Отдых — не награда, которую надо заслужить. Отдых — условие, при котором ты можешь функционировать.»
- «Ты не обязан зарабатывать восстановление. Ты должен позволить его себе.»
- **NEW 29 May:** «Заслужить работу отдыхом, а не отдых работой.»
- **NEW 29 May:** «Отдых — не после работы, а до — как топливо, а не награда.»

**Liberated Mind tie-in:**
- После глав про когнитивную фузию: «Мысль — это не команда. Просто слова в голове.»
- После глав про ценности: «Что сегодня будет достаточно — а не идеально?»

**Perfectionism / Shame (Brené Brown tie-in — 2 раза в неделю):**
- «Совершенство — это не здоровое стремление, а щит от стыда.»
- «Сегодня: 80% сделано лучше, чем 100% не начато.»

### Format in brief:
```text
 ACT: [одна строчка — prompt из ротации или под главу Liberated Mind]
```

## Daily Microscopy Challenge — REQUIRED (every brief)

Igor's idea: каждый день смотреть что-то новое под микроскопом. 5-10 минут, zero pressure, pure curiosity.

**MANDATORY:** Every morning brief MUST include a microscopy challenge suggestion. If you skip it, the brief is incomplete.

Утром: «Сегодня под микроскоп: [образец]». Выбирать из того, что есть дома / в саду / в холодильнике. Не повторять в пределах недели.

### Check what was already proposed recently

Microscopy samples repeat easily. Before suggesting one, verify it hasn't been used recently:

1. Check the current cron session's assistant messages for the sample proposed today.
2. Run `session_search(query="Micro Challenge OR микроскоп OR сегодня под микроскоп", role_filter="user,assistant", limit=5, sort="newest")`.
3. Extract samples mentioned in the last 7 days.
4. Suggest something that hasn't appeared this week.

### Источники образцов (что есть под рукой)

**Сад/улица:**
- Пыльца разных цветов (уже смотрел)
- Папоротник (уже смотрел)
- Лист с нижней стороны — трихомы, устьица
- Срез травинки
- Плесень на старом листе
- Паутина
- Почва/песок
- Муравей или мелкое насекомое

**Кухня:**
- Тонкий срез редиски/моркови/лука
- Кожура огурца
- Крахмал картошки
- Дрожжи (растворить в воде)
- Йогурт/кефир — бактерии
- Кофейная гуща
- Соль/сахар (кристаллы)
- Плёнка чая
- Срез плесени на хлебе

**Дом:**
- Кот шерсть (Лана vs Арчер — сравнить!)
- Пыль
- Нить разной ткани (хлопок vs синтетика)
- Страница книги
- Перо из подушки
- Волос vs кошачий ус
- Срез бумаги (край, структура)

Принцип: лучше imperfect observation сегодня, чем perfect observation никогда. Если нет образца — не беда.

### Формат в brief

```text
 Сегодня под микроскоп: <образец>
- [совет: что искать — клетки/кристаллы/структуру]
```

## Output — REQUIRED sections

Every morning brief MUST include ALL of the following sections. Do not omit any.

```text
Morning Brief — <date>

## Сегодня в календаре
(из Google Calendar)

## Вчера — что закрыто
(кратко, только завершённое)

## Приоритеты на сегодня
1.
2.
3.

## Health / Recovery
(тренировки, сон, никотин, агорафория — помнить: агорафория контекстная, привязана к рабочему времени, не к выходу на улицу вообще)

**Энергетический базайн — без Dex.** Igor не принимает дексамфетамин (подтверждено 1 июня 2026 — прекратил задолго до, последняя разовая таблетка 28 мая). Вся энергия — натуральная, без фармацевтического буста. Garmin recovery-метрики (77h recovery после обычного дня) отражают реальную физиологическую нагрузку. Планировать энергию короткими блоками с перерывами на еду. Если Igor сообщает об энергии на 10% — это реальное истощение, а не настроение. Не предлагать стимулянтные стратегии.

**Проверка на биохимию перед анализом.** Когда Igor жалуется на низкую энергию, экранное отторжение, «всё болото» или «ничего не хочется» — первым делом проверить, когда он последний раз ел. Паттерн: ADD + без Dex → 5-7 часов без еды → падение сахара → всё кажется экзистенциальным кризисом. См. `igor-os-style` → Biochemical First Check для полного протокола.

### Morning Routine Check-in — motivational tone

Igor explicitly asked for reminders about his morning routine (медитация ~20 мин, Julia Reppel 15 мин) with **лёгкая мотивационная поддержка**, not a dry checklist. Format in brief:

- Медитация — / (сколько минут)
- Julia Reppel — / (сколько минут)

**Tone guidance:** Not «молодец, отлично» (that's sycophancy). Instead: *«Держишь процесс — это и есть система»* or *«Рутина держится — день строится вокруг неё, а не вопреки»*. Acknowledge the act of keeping the routine as evidence of system working, not as achievement to praise.

Если сделал меньше обычного (5 мин вместо 15) — с *«лучше 5 чем 0»*, не критиковать. Если ещё не сделал и время до 09:00 — напомнить с мотивационной рамкой, не как задачу на проверку.

## Home / Relationship
(Настя, дом, книги, кошки — не отписка, а конкретика из контекста)

## Dutch micro-learning
- Новое слово/фраза (с переводом)
- Мини-пример
- Повторение 1 слова из предыдущего дня

## ACT Touchpoint
(одна строчка из ротации)

## Micro Challenge — <образец>
(что искать: клетки/кристаллы/споры/структуру)

## Фокус (опционально, 2-4 раза в неделю)
(практический existential prompt с behavioural tail)

## Today's win condition
(одна строка — минимальный критерий, что день засчитан)
```

## Tone — zero sycophancy (mandatory)

Игорь прямо сказал: **никакого подхалимажа.**

- Не называть «брат», «дружище», «дорогой» — вообще никаких ласкательных обращений
- Не хвалить его выбор, решения или вопросы — сухая констатация без эпитетов
- Не писать «отлично!», «круто!», «прекрасно!»
- Не восторгаться его планами или идеями
- Юмор и сухость — да. Приторность и похвала — нет.
- Если он сделал что-то — это факт, не достижение (если он сам не маркировал как победу)
- Ошибки признавать прямо и без извинений

Допустимо:
- «Есть. День засчитан.»
- «Понял, снял со счетов.»
- Короткое «окей» или «добро» как ответ