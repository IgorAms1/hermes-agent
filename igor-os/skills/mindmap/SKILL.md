---
name: mindmap
description: Igor OS visual synthesis mode for turning research, notes, plans, decisions, or processes into Telegram-ready PNG mind maps and block diagrams.
version: 1.0.0
metadata:
  hermes:
    category: igor-os
---

# Mindmap Mode

## When To Use

Use for `/mindmap` or when Igor asks for a mind map, process map, visual summary, block diagram, sequence of steps, decision tree, visual breakdown, "карту", "схему", or "разбей на блоки".

This skill is often used after `/deep_research`: take the report or the latest research result, compress it into 5-9 visual blocks, render a PNG, and send the image to Telegram.

## Output Contract

Produce one primary output:

1. A PNG image saved locally and sent to Telegram as `MEDIA:/absolute/path/to/mindmap.png`.

Optionally include one short Telegram caption with the image path and what layout was chosen. Do not send a long explanation unless Igor asks.

## Source Selection

Use the best available source:

- If Igor provides text, use that text.
- If Igor gives a file path, read that file.
- If Igor says "из этого", "из последнего ресерча", "по отчету", or similar, use the most recent relevant `$HERMES_HOME/research/**/report.md`.
- If there are multiple plausible reports, choose the newest by modified time and mention that briefly.
- If the source is ambiguous enough to change the diagram, ask one compact question.

Never include secrets, raw `.env`, credentials, or private keys in a visual artifact.

## Choose The Layout

Choose automatically unless Igor requests a specific type:

- `flow`: sequential process, plan, workflow, protocol, onboarding, habit system, step-by-step explanation.
- `mindmap`: concepts, clusters, strategy, research findings, pros/cons, ecosystem, mental model.

If unsure, use `flow` for action/process topics and `mindmap` for conceptual/research topics.

## Content Rules

- Match Igor's language. If the source/request is Russian, all node titles and captions should be Russian.
- Keep each node compact: short title plus 1-3 bullets or one concise sentence.
- Use 5-9 nodes by default. More than 12 nodes makes the image hard to read on Telegram.
- Preserve important product names, source names, and technical terms.
- Prefer useful compression over completeness. The full report can keep the details; the image should make the structure visible.

## Render Workflow

Create a directory:

```text
$HERMES_HOME/mindmaps/YYYY-MM-DD-<topic-slug>/
```

Write a UTF-8 JSON spec:

```json
{
  "title": "Короткий заголовок",
  "subtitle": "Что показывает схема",
  "layout": "flow",
  "palette": "ocean",
  "nodes": [
    {
      "title": "1. Первый блок",
      "body": "Короткое объяснение.",
      "items": ["Один важный пункт", "Еще один пункт"]
    }
  ],
  "footer": "Опционально: источник или дата"
}
```

Render it with:

```bash
/home/igor1/hermes-agent/venv/bin/python /home/igor1/hermes-agent/igor-os/scripts/render_mindmap.py /absolute/path/to/mindmap.json /absolute/path/to/mindmap.png
```

Validate before sending:

```bash
/home/igor1/hermes-agent/venv/bin/python - <<'PY'
from pathlib import Path
from PIL import Image
p = Path("/absolute/path/to/mindmap.png")
assert p.exists() and p.stat().st_size > 10_000
with Image.open(p) as img:
    assert img.format == "PNG"
    assert img.width >= 1200 and img.height >= 700
print("OK")
PY
```

Send to Telegram:

```text
send_message(action="send", target="telegram", message="MEDIA:/absolute/path/to/mindmap.png")
```

If image sending fails, send it as a document:

```text
send_message(action="send", target="telegram", message="[[as_document]] MEDIA:/absolute/path/to/mindmap.png")
```

## Good Defaults

- `palette: "ocean"` for general work/research.
- `palette: "forest"` for health, training, routines, personal systems.
- `palette: "warm"` for decisions, risks, buying choices, tradeoffs.
- `layout: "flow"` for sequential blocks.
- `layout: "mindmap"` for clustered concepts.

## Telegram Caption

Keep it short:

```text
Собрал схему: <тема>
Формат: <flow/mindmap>
Файл: /absolute/path/to/mindmap.png
```
