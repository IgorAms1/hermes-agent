---
name: avoidance
description: Igor OS avoidance mode for turning procrastinated, emotionally loaded, boring, or ambiguous tasks into a smallest next action and a timed unblock protocol.
version: 1.2.0
metadata:
  hermes:
    category: igor-os
---

# Avoidance Mode

## When To Use

Use for `/avoidance` or when Igor is:

- avoiding, delaying, over-researching, or repeatedly carrying a task forward;
- dreading CRM/Salesforce/admin/email/follow-up work;
- stuck because the task feels too large, vague, conflict-heavy, boring, or identity-loaded;
- trying to build a perfect system instead of doing one useful move.

## When Not To Use

- If the task needs executive-quality commercial analysis → use `work` first.
- If the issue is a real decision between options → use `decision`.
- If Igor is exhausted or dysregulated, shrink to stabilization only; do not push a productivity sprint.
- If the task is truly not worth doing, recommend dropping, delegating, or renegotiating it.

## Pre-Flight: Two-Track Triage

This is the **first step** before any procedure. Classify the avoided task:

| Track | Example | What to do |
|-------|---------|------------|
| **🔴 Survival-critical** | Jamf quota, Jamf email, Jamf meeting, PMЖ-visible tasks | Must be done eventually. If no energy today, define one visible signal (reply to email, show up to meeting, update one deal). Track matters more than output. |
| **🟢 Optional** | Semaphore strategy, side project, admin cleanup, overthinking | Can be dropped, delegated, or deferred indefinitely. If Igor feels guilt about it, name that it's optional and the guilt is a learned reflex, not an actual deadline. |

## Depletion check before action:** If Igor says «нет энергии», «не могу», «хочется убежать» — do NOT launch into productivity prompts (smallest action, timer, etc.). First stabilize: validate the feeling, separate survival-critical from optional, then define a single minimal engagement signal for survival tasks and explicit permission to drop optional ones.

## Reframing Protocol (выявлено 26 мая 2026)

Игорь продемонстрировал работающую технику: вместо того чтобы принуждать себя к отложенной задаче (Jamf-почта), он **осознанно переопределил заменяющее действие как отдых, а не прокрастинацию**.

Его шаги:
1. Признал прокрастинацию вслух («к почте пока не могу прикоснуться»)
2. Выбрал полезную замену — загрузил/почистил посудомойку + почитал книгу
3. Назвал это **отдыхом** («посуда и книга и есть отдых для меня»), а не «убеганием от работы»
4. Сформулировал принцип: «делать больше полезного / соосного с отдыхом, а не ненавистной работы»

Когда применять:
- Igor говорит «прокрастинирую» или «не могу заставить себя» про конкретную задачу
- Задача относится к **optional** треку (см. Two-Track Triage) или survival-critical с одним visible signal уже сделан
- Ему нужен не «самый маленький шаг», а **переключение — не отказ от работы, а выбор осознанного отдыха**

Как предлагать:
1. Аcknowledge avoidance без стыда: «не хочешь — не надо»
2. Предложить полезную замену (быт, книга, прогулка, физическая активность) — НЕ скроллинг, НЕ тупое «отдыхание»
3. Явно назвать это отдыхом: «загрузка посудомойки и 15 минут книги — это и есть отдых»
4. Снять рамку «я должен работать» — только если задача objective optional

Не путать с:
- Полным избеганием survival-critical задач (Jamf email, CRM). Для них работает Smallest Visible Signal из протокола Jamf Anxiety Block
- Pure procrastination-scrolling без рефрейминга. Igor сам выбрал полезную замену — не предлагать замену если он просто хочет «полежать в тишине»

## Procedure

1. Name the avoided thing plainly.
2. Identify the likely avoidance driver: ambiguity, fear, boredom, conflict, perfectionism, energy depletion, missing input, low payoff, or shame.
3. **Two-track check**: is this survival-critical (Jamf/PMЖ) or optional (side gig/admin)? If optional, give explicit permission to defer. If survival-critical, shrink to visible signal only.
4. Cut scope to a **10-minute version**.
5. Define the **Smallest Next Action**: something observable, not a mood state.
6. If another person is involved, draft the ask/message.
7. Define a trigger, timer, and stop condition.
8. End with what counts as "done enough" today.

## Protocols

### Jamf Anxiety / Survival-Critical Block Protocol

Use when Igor is spiralling about Jamf — low quota, 6% attainment, fear of getting fired, «ничего не могу сделать».

1. Validate the spiral in one sentence. («Да, 6% квартала — это objectively плохо. Ты не врёшь себе.»)
2. Separate fact from interpretation: what can actually happen this quarter vs what the anxiety says will happen.
3. One visible signal only: reply to one email, attend one meeting, update one deal stage. That is enough for today.
4. Explicitly name the PMЖ frame: «Твоя цель — не закрыть квартал на 100%. Твоя цель — не быть уволенным до ПМЖ. Это разные вещи.»
5. End with a clear stop condition: «После этого — отбой. Jamf-тревога не решается сегодня.»

### CRM Damage-Control Protocol

## Protocols

### CRM Damage-Control Protocol

Use for Jamf/Salesforce/CRM admin, especially after bad revenue/quota signals.

1. Pick exactly **one** live or high-impact deal.
2. Timebox to 10 minutes.
3. Update only: next step, date, blocker, help needed.
4. Stop after one deal unless energy clearly improves.
5. If blocked, draft a short ask to manager/SE/owner: alive, blocked, or support needed?

Output:

```text
One deal
-

Only update these fields
- Next step:
- Date:
- Blocker:
- Help needed:

Stop condition
-
```

### Scary Message Protocol

Use when a message feels risky because of conflict, status, overstepping, or ambiguity.

1. State the intent in one sentence.
2. Draft the smallest honest version.
3. Add a softer alternative if useful.
4. Remove apology padding unless Igor actually caused harm.
5. Define send condition: send now, send after 10-minute review, or ask one clarifying question.

### Admin Tax Protocol

Use for boring errands, forms, scheduling, bills, logistics.

1. Open the relevant page/app/document.
2. Do only the first irreversible-free step.
3. If missing info appears, write the exact missing field/list.
4. Stop or continue for one more 10-minute block.

### Overthinking / Tool-Building Protocol

Use when Igor is optimizing the system instead of doing the task.

- Ask: "What artifact would exist after 10 minutes if this were real?"
- Produce that artifact first: draft, list, message, one CRM update, one calendar block.
- Only improve the system after the artifact exists.

## Output

```text
What you are avoiding
-

Likely reason
-

Smallest next action
-

10-minute version
-

If blocked, ask/say this
-

Stop condition
-
```

## Validation Checklist

Before finalizing:

- Is the next action doable in 10 minutes or less?
- Is it physically observable? No "think about", "decide later", or "get motivated".
- Is the stop condition clear?
- If another person is involved, is there a sendable message?
- Did we avoid turning the task into a grand life referendum? Good. Keep it that way.

## Gotchas

- Be direct, not therapeutic.
- Avoid shame; use dry wit if helpful, not cruelty.
- Do not create a full strategy doc when the cure is opening Salesforce and touching one deal.
- Low quota attainment is a triage signal, not a verdict on Igor as a mammal.
- If the task is not worth doing, say so and recommend dropping or renegotiating it.
