---
name: evening
description: Igor OS evening capture for daily logs, patterns, follow-ups, memory candidates, and tomorrow's task.
version: 1.5.0
metadata:
  hermes:
    category: igor-os
---

# Evening Capture

## When To Use

Use for `/evening` or daily shutdown logging.

## NEVER SILENT

This is non-negotiable. **You must always deliver a response.** Even if Igor hasn't answered the capture questions yet, send the questions. Even if there's "nothing new," send a brief summary of what was already known and ask if anything changed. Never respond with [SILENT] or skip delivery. The evening cron is the last checkpoint of the day — if you go silent, task completions and corrections are lost.

## Heartbeat Awareness

Before the formal evening capture, check if today's midday heartbeat (14:30 CEST cron) already ran and delivered a pulse check.

- If heartbeat ran and Igor responded with his state, **reference it**: "в heartbeat ты говорил что [state] — как сейчас?"
- If heartbeat ran and he didn't respond, **skip the pulse re-check** — the evening capture is for facts, not a second pulse probe
- If heartbeat failed to deliver (shouldn't happen, but check), do a brief pulse-first opening before tasks

The heartbeat's job is state-checking. The evening capture's job is fact-capturing. Don't duplicate the pulse; build on it.

## Pre-Capture Search (mandatory)

Before asking any questions, first scan the current visible Telegram conversation for updates Igor already mentioned. Then use `session_search` for prior sessions or same-day sessions that may have reset:

### ⚠️ Source Primacy Rule

**Never treat your prior cron summaries as ground truth.** The evening capture from yesterday, the heartbeat pulse, the morning brief — these are your *interpretations*, not evidence. If a fact matters (who reminded whom, what was completed vs planned), verify it against the raw user messages in the session files.

**Accuracy beats latency for `/evening` factual recall.** The evening capture is allowed to spend extra time scanning today's raw sessions. Hindsight is durable background context, not the source of truth for what happened today.

**Mandatory first step for any multi-day or cross-reference context:** Run `python3 ~/.hermes/scripts/session_week_summary.py --days=3` to see Igor's actual messages with timestamps. Then cross-check your own summaries against this raw view.

### Standard recall steps

1. If Igor mentioned any partner, project, or person by name during the day (CloudFresh, Semaphore, Techsvit, Traco, Cloudflare, Jamf, Basalt, Denis, Katya, etc.), run a Hindsight recall for durable context:

   Use `execute_code` to query Hindsight. **Prefer direct REST API** (more reliable than the client library):
   ```python
   import requests, json
   r = requests.post('http://localhost:8888/v1/default/banks/igor-os/memories/recall',
       json={'query': 'relevant topic', 'budget': 'low', 'max_tokens': 1200}, timeout=10)
   facts = r.json().get('results', [])[:3]
   for f in facts:
       print(f['text'][:200])
   ```

   If the client library is needed (e.g., entity extraction), the accessor pattern differs from dict-style:
   ```python
   from hindsight_client import Hindsight
   h = Hindsight(base_url='http://localhost:8888')
   result = h.recall(query='topic', bank_id='igor-os')
   # NOT result.get('matches') — use result.results (list of fact objects)
   for f in result.results:
       print(f.text[:200])
   ```

   Reference returned facts in the Daily Log or Follow-ups section. Skip gracefully if the API is unavailable.

   **Performance rule:** keep Hindsight recall targeted. Do not use `n_results`; the current REST API ignores it. Use `budget: "low"` + `max_tokens: 1200`, trim `results[:3]` client-side, query only the named partner/project/person, and avoid broad catch-all recalls. If a recall times out at 10s, retry only that failed query once with `timeout=30`; do not rerun successful queries. If retry fails, skip that context and continue the evening capture.

2. For same-day factual extraction, prefer the deterministic helper over multiple `session_search` calls. Start with a wide signal query:
   ```bash
   /home/igor1/hermes-agent/igor-os/scripts/session_extract.py --date today --roles user,assistant --query "completed OR done OR finished OR отправил OR завершил OR сделал OR закрыл OR tomorrow OR завтра OR перенос OR cancel OR отмена" --limit 40 --session-limit 12 --max-chars 500 --pretty
   ```
3. If the wide query seems sparse, Igor sent many voice notes, or the day was complex, run a second pass without `--query` and inspect raw messages:
   ```bash
   /home/igor1/hermes-agent/igor-os/scripts/session_extract.py --date today --roles user,assistant --limit 80 --session-limit 12 --max-chars 350 --pretty
   ```
4. Use returned raw messages to keep only today's relevant updates.
5. Use `session_search` only for a narrow follow-up query or to scroll a known valid session. Do not reuse `around_message_id` from another session.
6. If helper output is empty, then fall back to `session_search` with small limits; do not use `delegate_task` for session crawling because it can time out.

Voice transcriptions are often buried in user messages that summaries compress.

## Optional Heartbeat Pulse Check (experimental)

When configured as a separate cron (not the main evening capture), the heartbeat is a **proactive state check** — not a task review. It runs between the last work event and the evening capture (e.g., 17:45 CEST).

Purpose: check mental pulse, offer a state check pulse; offer grounding; don't ask for task updates.

Rules:
- Keep to 3-4 lines max
- No task updates, no session search, no analysis
- If Igor reported anxiety/shame/stress during the day: one grounding line using his own language
- One tiny physical suggestion (tea/water/stretch/breathe)
- Like a friend checking in — direct, warm, zero therapeutic tone
- Do not ask him to do anything except rest

Example:
```
🍃 Пульс-чек

Как ты после звонка?

Тяжёлый день — ты болеешь, переживал, но сделал больше чем мог.
Та паника про лимиты — это стыд, не реальность.

Чай с лимоном и 15 минут тишины — главный план на остаток дня.
```

## Pitfalls

- **Tone: zero sycophancy.** Игорь прямо сказал: никакого подхалимажа. Не называть «брат», не хвалить его выбор, не восторгаться. Сухая констатация фактов. Юмор — да, приторность — нет.
- **Date anchoring**: before the evening capture, call `TZ=Europe/Amsterdam date` and cross-reference all events Igor mentioned during the day against actual dates. Do not rely on «сегодня/вчера» from conversation position — Igor notices date errors immediately.
- **Cron overlap hazard**: if two evening cron jobs are scheduled close together (e.g., 18:00 and 20:00), the first may still be processing when the second fires. Detect this by checking if a prior evening-cron session file exists for today and is still actively being written to. Practical heuristic: compare file mtime against current time. If mtime < 5 minutes old, the prior run may still be active — do NOT restart from scratch. Instead, wait (poll mtime every 60s, max 5 min) for it to finish, then check if a capture was delivered. If no delivery found or the prior run was interrupted (incomplete data), COMPLETE the capture rather than restarting a duplicate crawl. Prefer a single daily evening cron over multiple overlapping ones.
- **Cron vs interactive mode**: the skill's Procedure section (step 2) asks questions to Igor. When running as a nightly cron (no user present), skip the questions — compile the summary from today's data directly. Only ask questions on manual `/evening` invocations where Igor is actually there to answer.
- **Cron delivery target must be specific. If setting up the evening cron, `deliver` must be `telegram:<chat_id>` (e.g., `telegram:1321905`), not bare `telegram`. Bare platform name causes silent delivery failure with `no delivery target resolved for deliver=telegram`. Combined with the NEVER SILENT rule above, this is a hard requirement for the cron to actually reach Igor.
- **Voice transcription errors are common.** Cross-reference transcribed names against known context in memory.
- **Multi-day voice-note split:** If Igor sends one voice note that mixes events from different dates, do not flatten it into one «today» log. Ask or infer exact dates, then rewrite the log under separate date headers. If Igor corrects the split («Гаага была 10 июня, щука сегодня»), immediately update the capture with the corrected dates and do not keep the old merged version.
- **`session_search` may miss same-day sessions.** The FTS index may not have ingested today's sessions yet when the evening cron fires. Prefer `/home/igor1/hermes-agent/igor-os/scripts/session_extract.py --date today ...`; it reads `.json`/`.jsonl` session files directly, filters internal skill prompts, and emits compact JSON. Use `session_search` only as a narrow fallback.
- **But `session_extract --date today` can also return zero sessions.** Do not interpret `sessions_scanned: []` as “nothing happened.” Fall back to `session_search` with the actual Amsterdam date plus broad update terms, then scroll the matched current-day session around raw user messages. If the search result is huge/persisted, read or parse the persisted output to extract `user` messages and nearby assistant confirmations; avoid relying on assistant summaries alone.
- **`delegate_task` can time out on session extraction.** The 600s timeout makes delegate_task unreliable for crawling session files. Prefer `igor-os/scripts/session_extract.py` or the lower-level patterns in `references/session-jsonl-parsing.md`.
- **Performance: parallelize independent calls.** When calling `session_search` for multiple queries, batch them in parallel (not sequential). Prefer `execute_code` for 3+ operations. Don't `session_search` if the answer is already in context — trust context first.
- **Memory architecture:** partner/project details → files at `~/.hermes/context/` or `igor-os/context/`. Memory gets only compact pointers. See `references/memory-architecture.md` in the morning skill.
- **Retention hygiene after Igor's 2026-06-23 correction:** do not turn the evening crawl into automatic storage. Ordinary same-day facts ("two calls drained me", "sent a BJJ pause message", "answered Adfinis but decisions remain") belong in the evening report/session history unless Igor asks to retain them or they clearly form a reusable durable pattern. Hindsight is for durable context, not a dump of every daily update. Hermes memory is only for compact operational guardrails; never store daily logs there.
- **Don't hallucinate completions.** Не отмечать задачу как сделанную, пока Igor не подтвердил выполнение. «Написал» ≠ «отправил». «Надо купить» ≠ «купил». «Черновик готов» ≠ «сообщение ушло». «Отправил сообщение в gym о паузе» ≠ «абонемент отменён» до ответа/подтверждения. Отсутствие исправления ≠ подтверждение. Если нет явного «сделал/готов/отправил/подтвердили» — не ставь галку.
- **Hindsight client library API divergence.** `hindsight_client` v0.6.1 returns `RecallResponse` objects (attribute access: `result.results`, `result.results[0].text`), NOT dicts. The `.get('matches')` pattern fails silently. For reliability, use the direct REST API at `/v1/default/banks/{bank_id}/memories/recall` — it returns standard JSON with a `results` array.

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

## Small Wins — обязательный блок

Igor сам сказал: «когда ты перечисляешь мои маленькие победы мне становится лучше». Делать системно каждый вечер, а не по настроению.

### Pattern-recognition wins

Count real-time recognition of a repeating state as a win, even if the state itself was unpleasant or unresolved. Especially important pattern class: **office/workday state appearing outside work**.

Capture it explicitly when Igor says he noticed:
- “это тот же офисный паттерн”;
- “я не хочу здесь находиться, но держу лицо”;
- low resource + suppressed impulses + politeness/social obligation;
- tics returning as a signal;
- loss of agency / someone else taking over decisions.

Format as a concrete win, not a therapy lecture:
`- 🧭 поймал паттерн в моменте: офисное состояние включилось в [context], тики = сигнал низкого ресурса + сдержанных импульсов.`

Do not over-solve immediately. First log the detection. If giving a next step, keep it tiny: exit plan, water/air break, or permission to stop pretending for 2 minutes.

Принцип: scanning the day for wins, not waiting to be told. Если Igor не упомянул что-то, но оно было в его сообщениях — засчитай.

### Что искать (автоматически, из дневной переписки)
### Что искать (автоматически, из дневной переписки)

- **Утренняя рутина:** медитация (~20 мин), Julia Reppel, Liberated Mind, шахматы (streak)
- **Семафор/Jamf работа:** отправленные письма, звонки, транскрипты, анализ, даже «просто ответил» — это win
- **Тело:** поел, выпил воду, поспал днём, вышел на улицу, отдохнул — это wins, не «ничего»
- **Recovery substitutes:** если Igor заменил думскроллинг на лежать с маской/наушниками, цельный альбом, тишину, игру, прогулку или другой восстановительный кокон — считать это win. Формулировать как «🎧 музыка в темноте вместо думскроллинга» / «🎮 захотел играть = ресурс вернулся» без морализации.
- **Resource markers:** возвращение желания играть, читать, слушать музыку, кататься или смотреть кино — не “лень”, а полезный маркер ресурса. Логировать как наблюдение о состоянии нервной системы, не превращать в задачу.
- **Биохимическая осознанность (special win):** Если Igor заметил, что падение энергии/настроения было вызвано не психологией, а тем что давно не ел — и поел — это win уровня «система работает». Особенно ценно для дней без Dex, где реальная энергия ниже и падения сахара более вероятны. Маркировать как «🍒 заметил падение сахара — поел».
- **Эмоциональная регуляция:** заметил триггер, не сорвался, пошёл полежать = win
- **Быт:** комбуча, тумбочки, картонки, корм для котов — реальные победы, засчитывать

### Формат

Оформлять в конце evening capture, до Daily Log:

```text
Маленькие победы
- 🧘 медитация 20 мин
- 📖 «Promise at Dawn» — глава 2
- 📬 письмо Basalt + ход разговора
- 🎯 транскрибнул демку Дениса, вопросы готовы
- 🍵 поел, поспал, выжил
```

Без оценки («мог бы больше», «это мелочь»). Просто факты. Мозг пиздит — факты не пиздят.

## Procedure

1. **Pulse-first**: If no heartbeat ran today, open with a one-line state check ("как день прошёл в целом?") before diving into tasks. If heartbeat ran, reference it.
2. Acknowledge what Igor already reported during the day, then ask only the remaining questions:

- What mattered today?
- What did you avoid?
- What did you learn?
- Any work, partner, or interview notes to remember?
- Any Dutch words or phrases from today?
- Any health, training, fishing, MTB, BJJ, microscopy, or relationship notes?

3. **Bias-analysis (optional, light layer)**: After Igor answers the questions, add one pattern-check question if the day had any emotional charge (shame, avoidance, overextension, self-criticism):

- «А было сегодня место, где ты себя наебывал?»
- Или: «Какой паттерн из знакомых сегодня повторился?»
- Или: «Один момент, где твой мозг сказал «я плохой» / «ничего не выйдет» / «потом» — и это было неправда?»

Keep this **one line max**, never a lecture. If Igor engages, note the pattern in `Biases/patterns` section below. If he doesn't, drop it. No follow-up therapy.

When Igor answers, summarize into:

```text
Маленькие победы
- 🧘 медитация 20 мин
- 📖 чтение: глава
- 📬 работа: письма/звонки
- 🎯 проект: прогресс
- 🍵 тело: поел/поспал/отдых
- 🐌 быт: улитки/комбуча/тумбочки

Daily log
-

Patterns / Biases
-

Follow-ups
-

Durable memory candidates

**Policy: durable facts → Hindsight, not Hermes memory.** Hermes memory is only for operational guardrails needed every turn. See memory auto-grooming cron (Sundays 06:00) for automated cleanup.

When identifying durable memory candidates from the day:
- Work/deal intel (calls, deals, partners) → hindsight_retain() with descriptive tags
- Therapy insights, personal reframes → hindsight_retain() with therapy tag
- Project decisions, strategy shifts → hindsight_retain() with project tag
- Corrections, lessons learned → hindsight_retain() with lesson tag

Do NOT store these in Hermes memory via memory(). Hermes memory stays lean (~25-30% capacity) for style rules, system guardrails, and key people identifiers.

Ask before storing sensitive or work-related content if Igor hasn't explicitly shared it for retention.

Suggested task for tomorrow
**Weekend rule:** If tomorrow is Saturday, Sunday, or a known NL holiday, do NOT suggest work items. Let the weekend be weekend. Work items resume on the nearest workday.
```

Follow `context/memory-policy.md`. Ask before storing sensitive or work-related memory.
