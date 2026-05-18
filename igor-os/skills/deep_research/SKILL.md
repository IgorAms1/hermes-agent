---
name: deep_research
description: Igor OS deep research mode for clarified, multi-threaded source research with parallel delegation, synthesis, a short Telegram summary, and a saved local Markdown report.
version: 1.0.0
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

Use 2-3 parallel threads by default because `delegation.max_concurrent_children` is commonly 3. If more coverage is needed, run a second wave after the first results return.

## Delegation

Use `delegate_task` in batch mode with `tasks` for independent research threads. Each task must be self-contained and must request sources.

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

Key findings
- Finding - source URL - confidence high/medium/low

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

## Sources

- <URL> - <why it matters>

## Appendix: Research Threads
```

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

## Safety And Privacy

- Never store secrets, raw `.env`, private keys, or credentials in the report.
- For work-sensitive topics, sanitize customer names or mark the report as local/private.
- For medical, legal, financial, immigration/visa, or high-stakes current information, use current web sources and label uncertainty clearly.
- For visa/immigration/admin procedures, separate: (1) official legal/formal requirements, (2) application-center practice/checklists, and (3) practical recommendations. Prefer government/official portals first, then VFS/application-center pages for local process details. Always warn that checklists, fees, appointment availability, and routing can change.
- Keep Telegram concise; put long details in the report.
