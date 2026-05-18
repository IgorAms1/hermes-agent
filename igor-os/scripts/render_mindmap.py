#!/usr/bin/env python3
"""Render Igor OS mind-map specs to PNG.

The renderer intentionally depends only on Pillow, which is already available
in the Hermes virtualenv. Input is a UTF-8 JSON file with a compact structure:

{
  "title": "Map title",
  "subtitle": "Optional subtitle",
  "layout": "flow" | "mindmap",
  "nodes": [
    {"title": "Step", "body": "Short text", "items": ["bullet"]}
  ],
  "footer": "Optional footer"
}
"""

from __future__ import annotations

import argparse
import json
import sys
import textwrap
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont


PALETTES = {
    "ocean": {
        "bg": "#F6FAFF",
        "ink": "#102033",
        "muted": "#52677A",
        "card": "#FFFFFF",
        "line": "#BFD3EA",
        "accents": ["#2563EB", "#0891B2", "#0F766E", "#7C3AED", "#DB2777"],
    },
    "forest": {
        "bg": "#F7FBF7",
        "ink": "#17251C",
        "muted": "#53665A",
        "card": "#FFFFFF",
        "line": "#C9DEC9",
        "accents": ["#15803D", "#0F766E", "#65A30D", "#2563EB", "#A16207"],
    },
    "warm": {
        "bg": "#FFFAF4",
        "ink": "#2D2118",
        "muted": "#6F5C4B",
        "card": "#FFFFFF",
        "line": "#E9CFAE",
        "accents": ["#C2410C", "#CA8A04", "#BE123C", "#7C3AED", "#047857"],
    },
}


def _font_path(bold: bool = False) -> str | None:
    name = "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"
    candidates = [
        f"/usr/share/fonts/truetype/dejavu/{name}",
        f"/usr/share/fonts/dejavu/{name}",
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf",
    ]
    for font_dir in Path(sys.prefix).glob("lib/python*/site-packages/matplotlib/mpl-data/fonts/ttf"):
        candidates.append(str(font_dir / name))
    for candidate in candidates:
        if candidate and Path(candidate).exists():
            return candidate
    return None


def _font(size: int, *, bold: bool = False) -> ImageFont.ImageFont:
    path = _font_path(bold)
    if path:
        return ImageFont.truetype(path, size=size)
    return ImageFont.load_default()


def _text_width(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont) -> int:
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0]


def _wrap(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont, width: int) -> list[str]:
    lines: list[str] = []
    for raw in str(text or "").splitlines() or [""]:
        raw = raw.strip()
        if not raw:
            lines.append("")
            continue
        words = raw.split()
        current = ""
        for word in words:
            probe = word if not current else f"{current} {word}"
            if _text_width(draw, probe, font) <= width:
                current = probe
                continue
            if current:
                lines.append(current)
            if _text_width(draw, word, font) <= width:
                current = word
            else:
                font_size = int(getattr(font, "size", 24))
                approx_chars = max(8, int(width / max(12, font_size * 0.55)))
                wrapped = textwrap.wrap(word, width=approx_chars, break_long_words=True)
                lines.extend(wrapped[:-1])
                current = wrapped[-1] if wrapped else ""
        if current:
            lines.append(current)
    return lines


def _line_height(font: ImageFont.ImageFont) -> int:
    bbox = font.getbbox("Ag")
    return bbox[3] - bbox[1] + 8


def _draw_wrapped(
    draw: ImageDraw.ImageDraw,
    lines: list[str],
    xy: tuple[int, int],
    font: ImageFont.ImageFont,
    fill: str,
    *,
    line_gap: int = 4,
) -> int:
    x, y = xy
    h = _line_height(font)
    for line in lines:
        if line:
            draw.text((x, y), line, font=font, fill=fill)
        y += h + line_gap
    return y


def _normalize_nodes(spec: dict[str, Any]) -> list[dict[str, Any]]:
    raw_nodes = spec.get("nodes") or spec.get("blocks") or spec.get("steps") or []
    nodes: list[dict[str, Any]] = []
    for idx, raw in enumerate(raw_nodes, 1):
        if isinstance(raw, str):
            nodes.append({"title": f"{idx}. {raw}", "body": ""})
            continue
        if not isinstance(raw, dict):
            continue
        node = dict(raw)
        node.setdefault("title", f"Блок {idx}")
        node.setdefault("body", node.get("summary", ""))
        nodes.append(node)
    return nodes[:12]


def _node_text(node: dict[str, Any]) -> str:
    parts: list[str] = []
    body = str(node.get("body") or node.get("summary") or "").strip()
    if body:
        parts.append(body)
    items = node.get("items") or node.get("bullets") or []
    if isinstance(items, list):
        parts.extend(f"• {str(item).strip()}" for item in items if str(item).strip())
    children = node.get("children") or []
    if isinstance(children, list):
        parts.extend(f"• {str(child).strip()}" for child in children if str(child).strip())
    return "\n".join(parts)


def _measure_card(
    draw: ImageDraw.ImageDraw,
    node: dict[str, Any],
    card_width: int,
    title_font: ImageFont.ImageFont,
    body_font: ImageFont.ImageFont,
) -> tuple[int, list[str], list[str]]:
    inner_width = card_width - 56
    title_lines = _wrap(draw, str(node.get("title", "")), title_font, inner_width)
    body_lines = _wrap(draw, _node_text(node), body_font, inner_width)
    height = 42
    height += len(title_lines) * (_line_height(title_font) + 4)
    if body_lines:
        height += 12 + len(body_lines) * (_line_height(body_font) + 4)
    return max(150, height), title_lines, body_lines


def _draw_card(
    draw: ImageDraw.ImageDraw,
    node: dict[str, Any],
    box: tuple[int, int, int, int],
    *,
    accent: str,
    palette: dict[str, Any],
    index: int | None,
    title_font: ImageFont.ImageFont,
    body_font: ImageFont.ImageFont,
    title_lines: list[str],
    body_lines: list[str],
) -> None:
    x1, y1, x2, y2 = box
    draw.rounded_rectangle((x1, y1, x2, y2), radius=28, fill="#D7E2EF")
    draw.rounded_rectangle((x1, y1 - 4, x2, y2 - 4), radius=28, fill=palette["card"])
    draw.rounded_rectangle((x1, y1 - 4, x1 + 14, y2 - 4), radius=8, fill=accent)
    if index is not None:
        badge = str(index)
        bx, by = x1 + 28, y1 + 24
        draw.ellipse((bx, by, bx + 52, by + 52), fill=accent)
        tw = _text_width(draw, badge, body_font)
        draw.text((bx + 26 - tw / 2, by + 10), badge, font=body_font, fill="#FFFFFF")
        text_x = x1 + 100
    else:
        text_x = x1 + 34
    text_y = y1 + 24
    text_y = _draw_wrapped(draw, title_lines, (text_x, text_y), title_font, palette["ink"], line_gap=3)
    if body_lines:
        text_y += 8
        _draw_wrapped(draw, body_lines, (text_x, text_y), body_font, palette["muted"], line_gap=3)


def _draw_arrow(draw: ImageDraw.ImageDraw, x: int, y1: int, y2: int, color: str) -> None:
    draw.line((x, y1, x, y2 - 16), fill=color, width=6)
    draw.polygon([(x - 16, y2 - 16), (x + 16, y2 - 16), (x, y2 + 8)], fill=color)


def _render_flow(spec: dict[str, Any], output_path: Path, palette: dict[str, Any]) -> None:
    width = int(spec.get("width") or 1600)
    margin = 88
    gap = 44
    title_font = _font(58, bold=True)
    subtitle_font = _font(30)
    card_title_font = _font(34, bold=True)
    body_font = _font(27)
    footer_font = _font(23)

    scratch = Image.new("RGB", (width, 200), palette["bg"])
    draw = ImageDraw.Draw(scratch)
    nodes = _normalize_nodes(spec)
    card_width = width - margin * 2
    measured = [_measure_card(draw, node, card_width, card_title_font, body_font) for node in nodes]

    title_lines = _wrap(draw, spec.get("title", "Mind map"), title_font, width - margin * 2)
    subtitle_lines = _wrap(draw, spec.get("subtitle", ""), subtitle_font, width - margin * 2)
    footer_lines = _wrap(draw, spec.get("footer", ""), footer_font, width - margin * 2)

    height = margin
    height += len(title_lines) * (_line_height(title_font) + 6)
    if subtitle_lines:
        height += 18 + len(subtitle_lines) * (_line_height(subtitle_font) + 4)
    height += 54
    height += sum(item[0] for item in measured) + max(0, len(measured) - 1) * gap
    if footer_lines:
        height += 44 + len(footer_lines) * (_line_height(footer_font) + 4)
    height += margin
    height = max(900, min(height, 12000))

    img = Image.new("RGB", (width, height), palette["bg"])
    draw = ImageDraw.Draw(img)
    y = margin
    y = _draw_wrapped(draw, title_lines, (margin, y), title_font, palette["ink"], line_gap=6)
    if subtitle_lines:
        y += 18
        y = _draw_wrapped(draw, subtitle_lines, (margin, y), subtitle_font, palette["muted"])
    y += 48

    accents = palette["accents"]
    for idx, (node, measure) in enumerate(zip(nodes, measured), 1):
        card_h, title_lines, body_lines = measure
        x1 = margin
        x2 = width - margin
        y1 = y
        y2 = y + card_h
        _draw_card(
            draw,
            node,
            (x1, y1, x2, y2),
            accent=accents[(idx - 1) % len(accents)],
            palette=palette,
            index=idx,
            title_font=card_title_font,
            body_font=body_font,
            title_lines=title_lines,
            body_lines=body_lines,
        )
        if idx < len(nodes):
            _draw_arrow(draw, width // 2, y2 + 10, y2 + gap - 14, palette["line"])
        y += card_h + gap

    if footer_lines:
        y += 16
        _draw_wrapped(draw, footer_lines, (margin, y), footer_font, palette["muted"])

    output_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(output_path, format="PNG", optimize=True)


def _render_mindmap(spec: dict[str, Any], output_path: Path, palette: dict[str, Any]) -> None:
    width = int(spec.get("width") or 1800)
    margin = 84
    gap = 44
    title_font = _font(58, bold=True)
    subtitle_font = _font(30)
    card_title_font = _font(31, bold=True)
    body_font = _font(25)
    footer_font = _font(22)

    scratch = Image.new("RGB", (width, 200), palette["bg"])
    draw = ImageDraw.Draw(scratch)
    nodes = _normalize_nodes(spec)
    card_width = (width - margin * 2 - gap) // 2
    measured = [_measure_card(draw, node, card_width, card_title_font, body_font) for node in nodes]

    title_lines = _wrap(draw, spec.get("title", "Mind map"), title_font, width - margin * 2)
    subtitle_lines = _wrap(draw, spec.get("subtitle", ""), subtitle_font, width - margin * 2)
    footer_lines = _wrap(draw, spec.get("footer", ""), footer_font, width - margin * 2)

    header_h = margin + len(title_lines) * (_line_height(title_font) + 6)
    if subtitle_lines:
        header_h += 18 + len(subtitle_lines) * (_line_height(subtitle_font) + 4)
    header_h += 70

    col_y = [header_h, header_h]
    for i, measure in enumerate(measured):
        col = i % 2
        col_y[col] += measure[0] + gap
    height = max(col_y) + margin
    if footer_lines:
        height += 44 + len(footer_lines) * (_line_height(footer_font) + 4)
    height = max(900, min(height, 12000))

    img = Image.new("RGB", (width, height), palette["bg"])
    draw = ImageDraw.Draw(img)
    y = margin
    y = _draw_wrapped(draw, title_lines, (margin, y), title_font, palette["ink"], line_gap=6)
    if subtitle_lines:
        y += 18
        y = _draw_wrapped(draw, subtitle_lines, (margin, y), subtitle_font, palette["muted"])

    hub_y = y + 34
    draw.rounded_rectangle((margin, hub_y, width - margin, hub_y + 10), radius=5, fill=palette["line"])

    col_y = [header_h, header_h]
    accents = palette["accents"]
    for idx, (node, measure) in enumerate(zip(nodes, measured), 1):
        col = (idx - 1) % 2
        x1 = margin + col * (card_width + gap)
        y1 = col_y[col]
        card_h, title_lines, body_lines = measure
        _draw_card(
            draw,
            node,
            (x1, y1, x1 + card_width, y1 + card_h),
            accent=accents[(idx - 1) % len(accents)],
            palette=palette,
            index=None,
            title_font=card_title_font,
            body_font=body_font,
            title_lines=title_lines,
            body_lines=body_lines,
        )
        start_x = width // 2
        end_x = x1 + card_width // 2
        draw.line((start_x, hub_y + 10, end_x, y1 - 10), fill=palette["line"], width=4)
        col_y[col] += card_h + gap

    if footer_lines:
        y = max(col_y) + 12
        _draw_wrapped(draw, footer_lines, (margin, y), footer_font, palette["muted"])

    output_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(output_path, format="PNG", optimize=True)


def render(spec: dict[str, Any], output_path: str | Path) -> Path:
    palette = PALETTES.get(str(spec.get("palette") or "ocean"), PALETTES["ocean"])
    output = Path(output_path)
    layout = str(spec.get("layout") or "flow").lower()
    if layout in {"mindmap", "map", "cluster", "clusters"}:
        _render_mindmap(spec, output, palette)
    else:
        _render_flow(spec, output, palette)
    return output


def main() -> int:
    parser = argparse.ArgumentParser(description="Render a mind-map JSON spec to PNG")
    parser.add_argument("spec", help="Path to UTF-8 JSON spec")
    parser.add_argument("output", help="Path to output PNG")
    args = parser.parse_args()

    spec_path = Path(args.spec)
    with spec_path.open("r", encoding="utf-8") as fh:
        spec = json.load(fh)
    output = render(spec, args.output)
    with Image.open(output) as img:
        print(f"OK {output} {img.size[0]}x{img.size[1]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
