---
name: extract
description: Igor OS memory pre-processor for walls of text (transcripts, meeting notes, brain dumps, voice note transcriptions). Extracts compact, durable memory candidates before they hit long-term storage. Use for /extract or when Igor sends large blocks of text to be remembered.
metadata:
  hermes:
    category: igor-os
  version: "1.1.0"
---

# Extract — Memory Pre-Processor

## When To Use

Trigger when Igor:
- Sends a wall of text explicitly asking to "remember this" or "save this"
- Sends a long voice note / transcript with factual content
- Says `/extract` followed by a block of text
- Pastes meeting notes, call summaries, or brain dumps
- Provides context about people, projects, or decisions

Do NOT trigger on:
- Short factual statements that fit directly in the `memory` tool
- Casual conversation or opinions
- Emotional venting (filtered by policy)

## Procedure

### Step 0: Size check

If the input text is > 2000 characters, use `delegate_task` to process it:
- Subagent receives the full wall of text + these extraction instructions
- Returns ONLY structured candidates (following Steps 1-5 below)
- No tools are needed for the extraction subagent — tell it not to call tools
- Main agent presents results and asks for confirmation per Step 5
- This keeps walls of text out of main context, saving tokens

If ≤ 2000 characters, process directly in the main agent.

Subagent goal template (for >2000 char inputs):
```
Extract durable memory candidates from this text. Follow these rules:
[Steps 1-4 from this skill]

Return ONLY a JSON array of candidates: [{category, fact, confidence, sensitivity}]
No conversational text, no explanations. If nothing durable found, return [].
```

### Step 1: Parse the wall

Read the entire text. Identify what kind of content it is:
- Meeting/call transcript
- Brain dump / stream of consciousness
- Structured notes
- Mixed (voice transcription with noise)

### Step 2: Extract by category

Pull out ONLY durable facts. Be ruthless — discard conversational filler, small talk, repetition.

Categories to extract:

**People & Roles**
- Name, title, company, relationship to Igor
- Contact info (flag as sensitive)
- Key context: "Vitalik — Cloudflare advocate", "Živko — CRO at CloudFresh"

**Decisions & Outcomes**
- What was decided, by whom, when
- Reversible or irreversible?

**Action Items**
- Who does what by when
- Status if known

**Patterns & Insights**
- Repeated observations across sessions
- "Igor noticed that…", "Trend: partners in CEE prefer…"

**Corrections & Preferences**
- Igor correcting a previous assumption
- New style/communication preference

**Project State**
- Current phase, blockers, next milestone
- Key contacts, trial status

### Step 3: Filter by memory policy

Reject:
- Secrets, API keys, passwords
- Raw emotional content (unless Igor explicitly asks to save a lesson)
- Company confidential data not explicitly approved
- PII beyond what's already known

Flag as "ask first":
- Sensitive work context (partners, deals)
- Personal details about others
- Financial figures

### Step 4: Format candidates

For each candidate, produce a compact single-line memory entry:

```
CATEGORY: Compact fact (max ~200 chars)
Confidence: HIGH/MEDIUM/LOW
Sensitivity: low/medium/high — auto-save or ask?
```

Confidence guide:
- HIGH: stated explicitly, no ambiguity
- MEDIUM: implied or needs confirmation
- LOW: inferred, likely needs Igor to verify

### Step 5: Present and confirm

Show all candidates grouped by confidence:

```markdown
# Extract Results — [source description]

## Auto-save (HIGH confidence, low sensitivity)
- [Category]: Fact
- ...

## Ask first (MEDIUM-HIGH confidence, medium+ sensitivity)
- [Category]: Fact — REASON TO ASK
- ...

## Skipped (LOW confidence or policy rejection)
- Fact — reason skipped
- ...

## Summary
- Total extracted: N
- Auto-save: M
- Need confirmation: K
- Skipped: J

Save auto-save candidates now?
```

## Output Constraints

- Each memory candidate: max 200 characters
- Never include raw conversation in the output
- Prefer "X is Y" over "Igor said X is Y"
- Merge duplicates before presenting
- If nothing durable found, say so — don't fabricate

## Pitfalls

- Voice transcription errors: cross-reference names against existing memory. "Vitaly" might be "Vitalik." Flag ambiguous names.
- Transcripts often contain mixed voices: only attribute facts when the speaker is clearly identifiable.
- Don't save the extract skill's own output format to memory — save only the final approved entries with `memory(action="add", target=...)`.
- Walls > 2000 chars: use delegate_task. Walls ≤ 2000 chars: process in main agent.
