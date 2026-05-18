# Account Notes Pattern

Use this when Igor shares partner/account call extracts that are useful for future call prep but should not become daily todos.

## Trigger

- Igor says extracted follow-ups should not appear every day.
- Partner call notes contain useful future topics, open questions, or relationship context.
- The next useful moment is "when I have a call with this partner", not "today".

## Storage

Create or update:

```text
/home/igor1/hermes-agent/igor-os/accounts/<account-slug>.md
```

Suggested structure:

```markdown
# <Account> — account notes

Purpose: keep <Account>-specific topics out of Igor's daily todo list. Surface these notes when Igor says he has a call/QBR/follow-up with <Account>.

Last updated: YYYY-MM-DD

## Current call-prep topics

### Pipeline / opportunities
- **Opportunity name**
  - Status / signal.
  - Prep reminder.

### Process / enablement
- Topic.

### Open questions
- Question.

## How to use this note

When Igor says he has a <Account> call:
1. Do not dump every item as a todo list.
2. Ask call type only if it materially changes prep.
3. Surface 3-5 most relevant topics.
4. Split into must raise today / optional if time / background only.
5. Keep daily todo clean unless Igor explicitly asks to convert an item into an action.
```

## Todo hygiene

If you already added account-specific items to the daily todo list and Igor corrects you:

1. Move the content into the account note.
2. Mark the todos cancelled with a short "MOVED TO <Account> account notes" label.
3. Confirm the new retrieval behavior.

## Pitfall

Do not turn CRM/account context into Telegram-dread. Account notes are retrieval context for call prep, not a daily task tax.
