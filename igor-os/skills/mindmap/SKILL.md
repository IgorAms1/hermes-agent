---
name: mindmap
description: Igor OS visual synthesis mode for turning research, notes, plans, decisions, or processes into Telegram-ready PNG mind maps and block diagrams.
version: 1.1.0
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

Write a UTF-8 JSON spec with these fields:

| Field | Type | Description |
|-------|------|-------------|
| `title` | string | Chart title (shown in header + center hub for mindmap layout) |
| `subtitle` | string | Optional subtitle |
| `layout` | string | `"flow"` or `"mindmap"` |
| `palette` | string | `"ocean"`, `"forest"`, or `"warm"` |
| `nodes` | array | Array of node objects (max 12) |
| `footer` | string | Optional source/date footer |

Each node object:

| Field | Type | Description |
|-------|------|-------------|
| `title` | string | Bold heading for the card |
| `body` | string | Optional summary sentence shown before bullets |
| `items` | array of strings | Bullet points (each starts with •) |

Full example:

```json
{
  "title": "Тема исследования",
  "subtitle": "Ключевые выводы и структура",
  "layout": "mindmap",
  "palette": "ocean",
  "nodes": [
    {
      "title": "Блок 1",
      "body": "Короткое пояснение.",
      "items": [
        "Первый факт или вывод",
        "Второй факт или вывод"
      ]
    }
  ],
  "footer": "Источник: ... | Навигатор, 18.05.2026"
}
```

Render it with the script:

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

Send to Telegram — **один вызов**, не два:

```text
send_message(action="send", target="telegram", message="Собрал схему: <тема>\nФормат: <layout>\nMEDIA:/absolute/path/to/mindmap.png")
```

Текст до `MEDIA:` становится caption'ом к изображению. **Не отправляй текст и картинку отдельными сообщениями** — это создаёт спам в чате. Если нужно отправить только картинку без caption — используй `message="MEDIA:/path"`.

If image sending fails, send it as a document:

```text
send_message(action="send", target="telegram", message="[[as_document]] MEDIA:/absolute/path/to/mindmap.png")
send_message(action="send", target="telegram", message="[[as_document]] MEDIA:/absolute/path/to/mindmap.png")

## Tone: zero sycophancy

Same as deep_research skill — no «отлично», «прекрасно», «брат», «ого», cheerleading. Dry delivery: «Собрал схему: тема.». No fluff around the image.

## Good Defaults

- `palette: "ocean"` for general work/research.
- `palette: "forest"` for health, training, routines, personal systems.
- `palette: "warm"` for decisions, risks, buying choices, tradeoffs.
- `layout: "flow"` for sequential blocks.
- `layout: "mindmap"` for clustered concepts.
- Canvas width: `1600` for flow, `2000` for mindmap (these are defaults — override via spec `width` field if needed).



## Pitfalls

- **Hub text**: The center hub in mindmap layout shows the `title` from the JSON spec. Make the title descriptive enough to work both as the chart heading AND the central hub label (e.g. "Дельфины" not "Исследование"). Avoid single-char hub labels like "?".
- **Connector lines**: Mindmap layout draws diagonal lines from the center hub to each card. These are intentional connector lines, not rendering artifacts. If asked to "fix the lines", they are feature lines — make them thinner (width=3) and use the palette line colour so they look clean.
- **Card count**: Max 12 nodes. Mindmap layout uses a 2-column grid. With 7 nodes, the last card in the right column will have empty space below it — that's normal for unbalanced counts. With 9+ nodes the layout fills more evenly.
- **Font sizes on Telegram**: The renderer uses 64px title, 36px card title, 28px body on a 2000px canvas. This is optimised for Telegram image preview (tap-to-zoom). Smaller sizes look cramped in chat.
- **Card overflow**: If card text is very long, body text will wrap. The card height adjusts automatically but keep bullets to 1-3 per card. If body+items exceeds ~8 lines total, split into more nodes.
- **Vision analysis of output**: The renderer output can be viewed via `vision_analyze` to debug layout issues — but only if the vision auxiliary model supports image input. As of May 2026, the vision auxiliary is set to `google/gemini-3.1-flash-lite` (via OpenRouter) which supports vision. If you get a 404 "No endpoints found that support image input", the vision model doesn't support images — switch to a vision-capable model.
- **Double delivery**: Не отправляй caption и MEDIA двумя вызовами send_message. Один вызов с `message="caption\nMEDIA:/path"` отправляет и текст, и картинку как одно сообщение. Два вызова = два сообщения в чате, пользователь видит спам.
