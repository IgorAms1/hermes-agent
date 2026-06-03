---
name: deep_research
description: Igor OS deep research mode for clarified, multi-threaded source research with parallel delegation, synthesis, a short Telegram summary, and a saved local Markdown report.
version: 1.3.0
metadata:
  hermes:
    category: igor-os
---

# Deep Research Mode

## When To Use

Use for `/deep_research` or when Igor asks for deep research, investigation, market scan, vendor comparison, technical research, source-backed synthesis, or a decision memo that needs multiple sources.

Do not use for quick factual answers, simple web lookup, or opinion-only brainstorming. Use `/research` for a plan only; use `/deep_research` when Hermes should actually run the research and produce a saved report.

## Core Contract

Deep research must produce two outputs:

1. A short Telegram-friendly summary with the decision-relevant answer.
2. A full local Markdown report saved under `$HERMES_HOME/research/YYYY-MM-DD-<topic-slug>/report.md`.

If Igor asks for the file, or if the result is substantial and Telegram is available, send the report as a Markdown document with:

```text
send_message(action="send", target="telegram", message="[[as_document]] MEDIA:/absolute/path/to/report.md")
```

## Language And Encoding

- Match the user's language for all user-visible output. If Igor asks in Russian, write the Telegram summary, report headings, body, recommendations, and appendix summaries in Russian.
- Keep original-language source names, titles, product names, URLs, and technical terms when translating them would reduce clarity.
- Minimize unnecessary English code-switching. Translate generic labels and ordinary phrasing such as `bottom line`, `confidence`, `daily driver`, `backup`, `product facts`, and `practical consensus` when the user's language has a natural equivalent.
- Do not leave English template headings such as `Executive Answer`, `Key Findings`, `Evidence`, `Weak Evidence`, or `Appendix: Research Threads` in a Russian report. Localize the structure itself.
- Save Markdown files as UTF-8 text. After writing `report.md`, read back the first section and scan for obvious encoding/escaping failures before sending:

```text
\\uXXXX escapes, HTML entities, replacement characters (�), mojibake fragments like Ð/Ñ, or literal JSON-escaped newlines.
```

- If any of those artifacts appear, rewrite the file before sending it to Telegram. Do not send a corrupted report.

## Clarify First

If the request is ambiguous, ask up to 3 compact questions before researching:

- What decision or output should this research support?
- Scope: geography, time horizon, products/companies/sources to include or exclude?
- Depth: quick scan, standard deep research, or exhaustive?

If Igor gives enough context, do not stall. State reasonable assumptions and proceed.

## Research Plan

Before delegating, create a short plan.

Reference notes available:
- `references/netherlands-visa-invitation-russian-parents.md` — official-first research notes for Igor inviting Russian parents to the Netherlands on a short-stay Schengen visa.

Before delegating, create a short plan:

```text
Research question
-

Assumptions
-

Threads
1.
2.
3.

Success criteria
-
```

### Plan Confirmation Gate

Если Igor явно просит спланировать исследование («спланируй», «сделай с планированием», «напиши план сначала», «покажи план») — покажи ему план в Telegram **до** запуска delegate_task и жди подтверждения.

Если Igor просто просит «сделай дип ресерч на тему X» / «исследуй Y» / «сбацай ресерч» — не показывай план, запускай исследование сразу.

Используй 2-3 параллельных threads по умолчанию. Если нужно больше покрытия — запусти вторую волну после первых результатов.

## Delegation

**Внимание: контекст — ограниченный ресурс.** Local pipeline с Crawl4AI может вернуть 15-20KB+ сырого контента, что съедает бюджет ответа. Используй осознанно.

**Для быстрой ориентации** (без delegation):
Запусти `python3 ~/.hermes/scripts/search_pipeline.py --query "..." --limit 3 --no-content`
Это даст только заголовки и сниппеты — достаточно чтобы понять, есть ли контент.

**Когда delegation неизбежен** (глубокое исследование, параллельные треки):
Не трать контекст на pipeline. Сразу переходи к делегированию — delegate_task суб-агенты сами выполнят веб-поиск, и их результаты не загрязняют твой контекст.

**Исключение:** используй pipeline с `--no-content` перед delegation только чтобы:
- Валидировать поисковые запросы (найдут ли вообще что-то?)
- Поймать правильные термины на голландском/русском

Используй `delegate_task` если:
- Нужна параллельная обработка разных аспектов вопроса
- Нужны специфические источники (академические, локальные)
- Pipeline с --no-content показал, что контент есть

Default thread pattern:

```json
{
  "tasks": [
    {
      "goal": "Research thread 1: ...",
      "context": "Question, scope, required source types, output schema.",
      "toolsets": ["web"]
    },
    {
      "goal": "Research thread 2: ...",
      "context": "Question, scope, required source types, output schema.",
      "toolsets": ["web"]
    }
  ]
}
```

If a thread needs local file work, use `toolsets: ["web", "terminal", "file"]`. Do not use `delegate_task` for tiny research tasks where one web search is enough.

Each research thread should return:

```text
Thread answer
-

Key findings (each with source quality)
- Finding - source URL - [PRIMARY/SECONDARY/COMMENTARY] - confidence high/medium/low

Source quality:
  PRIMARY = official doc, academic paper, government site, original research
  SECONDARY = book, reputable analysis, review article, synthesis
  COMMENTARY = blog, podcast, forum post, opinion, news article

Contradictions / uncertainty
-

Best sources
- URL - why it matters

What to verify next
-
```

## Synthesis

After delegation, synthesize across threads:

- Deduplicate sources and findings.
- Separate strong evidence, weak evidence, speculation, and anecdote.
- Call out contradictions instead of smoothing them over.
- State confidence and what would change the conclusion.
- Prefer primary/official sources for current, legal, medical, financial, technical, or business-critical claims.
- Do not fabricate citations. If a claim has no source, label it unsourced or omit it.

## Second Wave Deepening

**Это ключевой механизм для глубины.** Первый проход (2-3 трека) даёт ширину. Второй проход даёт глубину.

После synthesis оцени:

- Какие находки самые важные, но поверхностные? (1-2 штуки)
- Какие источники заслуживают отдельного глубокого погружения?
- Где confidence низкий, а тема важна для ответа?

Если есть хотя бы один кандидат — запусти вторую волну delegate_task с фокусом на него. Пример:

```json
{
  "tasks": [
    {
      "goal": "Deep dive into [specific finding/source]: ...",
      "context": "First pass found X but needs verification. Find primary sources, academic papers, or official documents.",
      "toolsets": ["web"]
    }
  ]
}
```

После второй волны — финальный synthesis с учётом новых данных.

### Alternative: Pipeline instead of delegate_task for narrow follow-up

Когда пользователь уточняет запрос после основного отчёта («расскажи подробнее про X», «добавь про Y», «а что с Z?»):

- Если вопрос **узкий** (конкретные кейсы, имена, документы) — не запускай delegate_task. Subagent потратит контекст на планирование, а сделает то же, что ты — несколько поисковых запросов.
- Используй `search_pipeline.py --no-content` для быстрой ориентации, потом `--max-content` на 1-2 лучших результата. Это быстрее, дешевле и даёт тот же результат.

Delegate_task оправдан для follow-up только если:
- Нужно параллельно исследовать 2+ независимых аспекта
- Нужен анализ на другом языке (например, нидерландские источники)
- Тема достаточно глубокая для полноценного второго захода

### Pipeline fallback for thin delegate results

Delegate_task может вернуть **только план и никаких находок** — subagent описал что будет делать, но не успел/не смог дать конкретные URL, цитаты, или числа. Такое бывает при тайм-аутах или когда тема сложная для автоматического поиска.

**Не запускай повторную делегацию в надежде, что второй раз выйдет плотнее.** Вместо этого:

1. Извлеки ключевые слова/сущности из плана, который subagent вернул
2. Запусти 2-3 self-directed запроса через `search_pipeline.py` с `--max-content 2000-3000` на лучших кандидатах из выдачи
3. Если нужно больше — увеличь `--limit 5` или добавь ещё один запрос

Это даёт тот же объём данных, не тратя контекст на повторную делегацию.

### Recency follow-up pattern

Когда после основного ресерча пользователь просит «самые последние», «актуальные», «2025-2026» уточнения:

- Не запускай новый delegate_task на тот же запрос с фильтром по дате. Subagent может сделать то же самое дольше.
- Вместо: выполни `search_pipeline.py --query "..." --limit 3-5 --max-content 3000` с ключевыми словами, суженными на конкретные кейсы/имена/годы.
- Если источники оказались качественными (BBC, отчёты парламентов, Hybrid CoE, академические PDF) — это PRIMARY/SECONDARY. Если низкокачественными (форумы, непонятные блоги) — COMMENTARY с низкой уверенностью.

Признаки, что recency follow-up нужен:
- Пользователь сказал «сейчас», «последние», «влияние на текущую ситуацию»
- Основной ресерч охватывает историю, а пользователь хочет current events
- Обнаружился разрыв между последней датой в отчёте и сегодня

**Признак, что вторая волна не нужна:**
- Тема узкая, первый проход дал исчерпывающие primary sources
- Уверенность высокая по всем ключевым claims
- Igor просил быстрый ответ, не exhaustive

**Признак, что вторая волна обязательна:**
- Обнаружились противоречия между источниками
- Ключевой claim опирается на один secondary/commentary источник
- Тема большая и Igor явно просит «покопайся поглубже»

## Local Report

Create a directory:

```text
$HERMES_HOME/research/YYYY-MM-DD-<topic-slug>/
```

Save:

```text
brief.md       # initial question, assumptions, plan
thread-1.md    # optional, if useful
thread-2.md
thread-3.md
report.md      # final report
```

Use this `report.md` structure, localized to Igor's request language:

```markdown
# <Research title>

Date: <YYYY-MM-DD>
Question: <one sentence>

## Executive Answer

## Recommendation / Decision Implication

## Key Findings

## Evidence

### Strong Evidence

### Weak Evidence

### Speculation / Anecdote

## Contradictions And Unknowns

## Sources (Annotated)

### Key Sources
- <URL> — [PRIMARY/SECONDARY/COMMENTARY] — <1-2 sentences: what was taken, why it matters>
- ...

**Маркировка источника:**
- **PRIMARY** — первоисточник: научная статья, официальный документ, government portal, API-спецификация, интервью, сырые данные
- **SECONDARY** — вторичный: книга, аналитика, лонгрид, курс лекций, качественная журналистика
- **COMMENTARY** — комментарий: блог, подкаст, форум, opinion piece, tweet, вики (хороша для ориентации, но не как evidence)

### Supplementary
- <URL> — ...

### Unused But Relevant
- <URL> — not used, but <why may be useful>
```

## Appendix: Research Threads

(Omit if the report is self-contained.)

## Pitfalls

- **Subagent file claims are self-reported, not verifiable.** Subagents run in isolated workspaces — any file they claim to have written (thread reports, source tables, etc.) exists in THEIR context, not YOUR filesystem. Do not reference paths from subagent summaries unless you verify they exist on disk first. If a subagent claims «создан файл /path/to/report.md», treat it as a lie until you stat the path. The only file that reliably exists is the one YOU write in synthesis.
- **Single-pass shallowness.** First pass gives breadth but can miss depth. If the topic is large or Igor explicitly asks to «покопайся поглубже», a second wave of delegation is mandatory, not optional.
- **Over-reliance on secondary sources.** Wikipedia, analysis, blogs are good for orientation but claims need primary sources for confidence. Lower confidence if a key claim relies on commentary.
- **Missing contradictions.** Don't smooth over contradictions between sources — surface them. A contradiction is often more valuable than consensus.
- **Fabricated citations.** No «according to research / experts say» without a URL. If no source, label it unverified.
- **Missing dates.** For current topics (laws, products, geopolitics) include publication/currency date. Information can become stale.
- **Output truncation.** The report or Telegram summary can be silently truncated (⚠️ Response truncated due to output length limit) if it exceeds the model's output budget. This wastes the entire research effort. **Mitigation:** after delegation finishes and before writing the Telegram response, save the full report to `report.md` first. Keep the Telegram summary under ~3000 chars — key findings only. If the summary itself would be truncated, fall back to a one-paragraph bottom line plus «Полный отчет приложен / локально в report.md». Never let a full report be delivered inline where it can be cut mid-sentence.

For Russian requests, use Russian labels, for example:

```markdown
# <Название исследования>

Дата: <YYYY-MM-DD>
Вопрос: <одно предложение>

## Короткий вывод

## Практическое решение

## Ключевые выводы

## Доказательная база

### Сильные основания

### Более слабые основания

### Гипотезы и практический опыт

## Противоречия и неизвестные

## Источники

## Приложение: исследовательские потоки
```

## Telegram Output

Keep the Telegram response short and in the same language as the request.

Do not copy the English label names below into a non-English answer. Localize
the Telegram summary labels too.

Neutral structure:

```text
Deep research: <topic>

Bottom line
-

Why
1.
2.
3.

Confidence
-

Full report
- /absolute/path/to/report.md
```

For Russian requests, use Russian labels:

```text
Исследование: <тема>

Вывод
-

Почему
1.
2.
3.

Уверенность
-

Полный отчет приложен.
Локально: /absolute/path/to/report.md
```

If the file was sent, say it in the user's language, for example `Полный отчет приложен.` for Russian. If file sending fails, include the local path and the error in one line, again in the user's language.

## Tone: zero sycophancy (mandatory)

Игорь прямо сказал: никакого подхалимажа. Телеграм-сводка должна быть сухой, фактологической, без:

- «Отличная работа», «прекрасный результат» — не надо
- «Как тебе такое?», «вот это поворот», «ого!» — нет
- Называть его «брат», «дружище», «дорогой» — категорически нет
- Восторженных эпитетов про его вопросы или идеи

Допустимо:
- Сухая констатация: «Есть. Отчёт сохранён.»
- Прямые выводы без смягчения
- Юмор и сарказм — да, но без приторности
- Признание ошибок — прямо, без извинений

## Safety And Privacy

- Never store secrets, raw `.env`, private keys, or credentials in the report.
- For work-sensitive topics, sanitize customer names or mark the report as local/private.
- For medical, legal, financial, immigration/visa, or high-stakes current information, use current web sources and label uncertainty clearly.
- For visa/immigration/admin procedures, separate: (1) official legal/formal requirements, (2) application-center practice/checklists, and (3) practical recommendations. Prefer government/official portals first, then VFS/application-center pages for local process details. Always warn that checklists, fees, appointment availability, and routing can change.
- Keep Telegram concise; put long details in the report.
