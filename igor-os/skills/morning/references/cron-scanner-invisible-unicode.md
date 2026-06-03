# Cron Scanner — Invisible Unicode False Positives

## The Problem

Hermes cron jobs run through a security scanner in `cron/scheduler.py` that blocks prompts containing invisible unicode characters. The scanner checks the **assembled prompt** (user prompt + loaded skill content) — not just the cron job's prompt text.

## Scanner Source

`cron/scheduler.py` → `_build_job_prompt()` → `_scan_assembled_cron_prompt()` → `tools/cronjob_tools.py::_scan_cron_prompt()`

## Blocked Characters (`_CRON_INVISIBLE_CHARS`)

Defined in `tools/cronjob_tools.py`, line 68:

```python
_CRON_INVISIBLE_CHARS = {
    '\u200b',  # ZERO WIDTH SPACE
    '\u200c',  # ZERO WIDTH NON-JOINER
    '\u200d',  # ZERO WIDTH JOINER  ← THIS ONE
    '\u2060',  # WORD JOINER
    '\ufeff',  # ZERO WIDTH NO-BREAK SPACE (BOM)
    '\u202a',  # LEFT-TO-RIGHT EMBEDDING
    '\u202b',  # RIGHT-TO-LEFT EMBEDDING
    '\u202c',  # POP DIRECTIONAL FORMATTING
    '\u202d',  # LEFT-TO-RIGHT OVERRIDE
    '\u202e',  # RIGHT-TO-LEFT OVERRIDE
}
```

## Why It Blocks Legitimate Content

Many **compound emoji** use U+200D (Zero Width Joiner) to combine multiple codepoints into a single glyph:

| Intended | What you type | ZWJ present? |
|---|---|---|
| 🧘 | `U+1F9D8` | No |
| meditation+female | `U+1F9D8 U+200D U+2640 U+FE0F` | **Yes** |
| women+girls+family | `U+1F469 U+200D U+1F469 U+200D U+1F467 U+200D U+1F466` | **Yes** |
| 👪 | `U+1F46A` | No |

The scanner iterates over every character in the assembled prompt. If any character's codepoint is in `_CRON_INVISIBLE_CHARS`, it blocks immediately — regardless of context.

## Detection

```bash
grep -Pn $\'\\u200d\' <file>   # detect U+200D
grep -Pn $\'\\u200b\' <file>   # detect U+200B
grep -Pn $\'\\ufeff\' <file>   # detect BOM
```

## Fix

Replace ZWJ-based compound emoji with simple single-codepoint alternatives:

| ZWJ variant | Replace with |
|---|---|
| compound meditation → `🧘` | Lotus person (unisex) |
| compound family → `👪` | Simple family |
| compound laptop → `💻` | Laptop only |
| compound runner → `🏃` | Runner (unisex) |

After editing, verify zero matches before testing with `cronjob(action='run')`.

## Other Cron Skills Affected

Any skill loaded by a cron job is subject to this scan at runtime. The check happens in `cron/scheduler.py::_build_job_prompt()` ~ line 996, not at create/update time. This means:

- `cronjob(action='create', ...)` only scans the user prompt (line 335)
- `cronjob(action='update', ...)` only scans the updated prompt text (line 457)
- **Runtime** scans the assembled prompt (skill content + prompt) in `_build_job_prompt()` (line 996)

So a skill can pass create/update validation but still be blocked at runtime due to ZWJ in its SKILL.md.
