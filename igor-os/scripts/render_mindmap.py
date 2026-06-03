#!/usr/bin/env python3
"""Renders Igor OS mind-map specs to nice-looking PNGs.

Depends only on Pillow.  Reads a UTF-8 JSON spec and writes a PNG.

Spec format:
{
  "title": "…",
  "subtitle": "…",
  "layout": "flow" | "mindmap",
  "palette": "ocean" | "forest" | "warm",
  "nodes": [
    {"title": "…", "body": "…", "items": ["…"]}
  ],
  "footer": "…"
}

Changes from v1:
- Much bigger fonts, tighter & cleaner cards.
- No more janky double-border shadow.
- Solid accent-left-bar cards.
- Thinner, cleaner connector lines for mindmap.
- Better padding and line spacing.
- Coloured section hints for mindmap layout.
"""

from __future__ import annotations

import argparse
import json
import sys
import textwrap
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont

# ---------------------------------------------------------------------------
# Palettes
# ---------------------------------------------------------------------------
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

# ---------------------------------------------------------------------------
# Font helpers
# ---------------------------------------------------------------------------
def _font_path(bold: bool = False) -> str | None:
    name = "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"
    candidates = [
        f"/usr/share/fonts/truetype/dejavu/{name}",
        f"/usr/share/fonts/dejavu/{name}",
    ]
    if sys.platform == "darwin":
        arial = "Arial Bold.ttf" if bold else "Arial.ttf"
        candidates.insert(0, f"/System/Library/Fonts/Supplemental/{arial}")
    for font_dir in Path(sys.prefix).glob("lib/python*/site-packages/matplotlib/mpl-data/fonts/ttf"):
        candidates.append(str(font_dir / name))
    for c in candidates:
        if c and Path(c).exists():
            return c
    return None


def _font(size: int, *, bold: bool = False) -> ImageFont.FreeTypeFont:
    path = _font_path(bold)
    if path:
        return ImageFont.truetype(path, size=size)
    return ImageFont.load_default()


# ---------------------------------------------------------------------------
# Measure / draw helpers
# ---------------------------------------------------------------------------
def _tw(draw: ImageDraw.Draw, text: str, font: ImageFont.FreeTypeFont) -> int:
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0]


def _lh(font: ImageFont.FreeTypeFont) -> int:
    bbox = font.getbbox("Ag")
    return bbox[3] - bbox[1] + 6


def _wrap(draw: ImageDraw.Draw, text: str, font: ImageFont.FreeTypeFont, width: int) -> list[str]:
    lines: list[str] = []
    for raw in str(text or "").splitlines() or [""]:
        raw = raw.strip()
        if not raw:
            lines.append("")
            continue
        words = raw.split()
        cur = ""
        for w in words:
            probe = w if not cur else f"{cur} {w}"
            if _tw(draw, probe, font) <= width:
                cur = probe
                continue
            if cur:
                lines.append(cur)
            if _tw(draw, w, font) <= width:
                cur = w
            else:
                fs = getattr(font, "size", 24)
                n = max(8, int(width / max(12, fs * 0.55)))
                wrapped = textwrap.wrap(w, width=n, break_long_words=True)
                lines.extend(wrapped[:-1])
                cur = wrapped[-1] if wrapped else ""
        if cur:
            lines.append(cur)
    return lines


def _draw_wrapped(
    draw: ImageDraw.Draw,
    lines: list[str],
    xy: tuple[int, int],
    font: ImageFont.FreeTypeFont,
    fill: str,
    *,
    gap: int = 3,
) -> int:
    x, y = xy
    h = _lh(font)
    for line in lines:
        if line:
            draw.text((x, y), line, font=font, fill=fill)
        y += h + gap
    return y


# ---------------------------------------------------------------------------
# Card measurement
# ---------------------------------------------------------------------------
def _normalize_nodes(spec: dict[str, Any]) -> list[dict[str, Any]]:
    raw = spec.get("nodes") or spec.get("blocks") or spec.get("steps") or []
    out: list[dict[str, Any]] = []
    for idx, r in enumerate(raw, 1):
        if isinstance(r, str):
            out.append({"title": f"{idx}. {r}", "body": ""})
            continue
        if not isinstance(r, dict):
            continue
        n = dict(r)
        n.setdefault("title", f"Блок {idx}")
        n.setdefault("body", n.get("summary", ""))
        out.append(n)
    return out[:12]


def _node_text(node: dict[str, Any]) -> str:
    parts: list[str] = []
    body = str(node.get("body") or "").strip()
    if body:
        parts.append(body)
    items = node.get("items") or node.get("bullets") or []
    if isinstance(items, list):
        for it in items:
            s = str(it).strip()
            if s:
                parts.append(f"• {s}")
    children = node.get("children") or []
    if isinstance(children, list):
        for ch in children:
            s = str(ch).strip()
            if s:
                parts.append(f"• {s}")
    return "\n".join(parts)


def _measure_card(
    draw: ImageDraw.Draw,
    node: dict[str, Any],
    card_w: int,
    title_font: ImageFont.FreeTypeFont,
    body_font: ImageFont.FreeTypeFont,
) -> tuple[int, list[str], list[str]]:
    inner = card_w - 56
    title_lines = _wrap(draw, node.get("title", ""), title_font, inner)
    body_lines = _wrap(draw, _node_text(node), body_font, inner)
    h = 28
    h += len(title_lines) * (_lh(title_font) + 3)
    if body_lines:
        h += 10 + len(body_lines) * (_lh(body_font) + 3)
    return max(120, h), title_lines, body_lines


# ---------------------------------------------------------------------------
# Card rendering
# ---------------------------------------------------------------------------
def _draw_card(
    draw: ImageDraw.Draw,
    node: dict[str, Any],
    box: tuple[int, int, int, int],
    *,
    accent: str,
    palette: dict[str, Any],
    index: int | None,
    title_font: ImageFont.FreeTypeFont,
    body_font: ImageFont.FreeTypeFont,
    title_lines: list[str],
    body_lines: list[str],
) -> None:
    x1, y1, x2, y2 = box
    # Card background with subtle shadow
    draw.rounded_rectangle((x1, y1 + 2, x2, y2 + 2), radius=14, fill=palette["line"])
    draw.rounded_rectangle((x1, y1, x2, y2), radius=14, fill=palette["card"])
    # Accent bar (left edge, thicker)
    draw.rounded_rectangle((x1, y1, x1 + 10, y2), radius=5, fill=accent)

    if index is not None:
        # Flow layout: numbered circle badge
        badge = str(index)
        bx, by = x1 + 28, y1 + 18
        r = 24
        draw.ellipse((bx - r, by - r, bx + r, by + r), fill=accent)
        tw_val = _tw(draw, badge, body_font)
        draw.text((bx - tw_val // 2, by - _lh(body_font) // 2 + 1), badge, font=body_font, fill="#FFFFFF")
        text_x = x1 + 80
    else:
        text_x = x1 + 32
    text_y = y1 + 18
    text_y = _draw_wrapped(draw, title_lines, (text_x, text_y), title_font, palette["ink"], gap=2)
    if body_lines:
        text_y += 6
        _draw_wrapped(draw, body_lines, (text_x, text_y), body_font, palette["muted"], gap=2)


def _draw_arrow(draw: ImageDraw.Draw, x: int, y1: int, y2: int, color: str) -> None:
    draw.line((x, y1, x, y2 - 14), fill=color, width=4)
    draw.polygon([(x - 12, y2 - 14), (x + 12, y2 - 14), (x, y2 + 6)], fill=color)


# ---------------------------------------------------------------------------
# Flow layout (left → right, stacked)
# ---------------------------------------------------------------------------
def _render_flow(spec: dict[str, Any], output_path: Path, palette: dict[str, Any]) -> None:
    width = int(spec.get("width", 1600))
    margin = 80
    gap = 36
    title_font = _font(64, bold=True)
    subtitle_font = _font(34)
    card_title_font = _font(38, bold=True)
    body_font = _font(30)
    footer_font = _font(24)

    scratch = Image.new("RGB", (width, 200), palette["bg"])
    draw = ImageDraw.Draw(scratch)
    nodes = _normalize_nodes(spec)
    card_w = width - margin * 2
    measured = [_measure_card(draw, n, card_w, card_title_font, body_font) for n in nodes]

    title_lines = _wrap(draw, spec.get("title", "Карта"), title_font, width - margin * 2)
    subtitle_lines = _wrap(draw, spec.get("subtitle", ""), subtitle_font, width - margin * 2)
    footer_lines = _wrap(draw, spec.get("footer", ""), footer_font, width - margin * 2)

    h = margin
    h += len(title_lines) * (_lh(title_font) + 6)
    if subtitle_lines:
        h += 20 + len(subtitle_lines) * (_lh(subtitle_font) + 4)
    h += 48
    h += sum(m[0] for m in measured) + max(0, len(measured) - 1) * gap
    if footer_lines:
        h += 48 + len(footer_lines) * (_lh(footer_font) + 4)
    h += margin
    h = max(800, min(h, 12000))

    img = Image.new("RGB", (width, h), palette["bg"])
    draw = ImageDraw.Draw(img)
    y = margin
    y = _draw_wrapped(draw, title_lines, (margin, y), title_font, palette["ink"], gap=6)
    if subtitle_lines:
        y += 20
        y = _draw_wrapped(draw, subtitle_lines, (margin, y), subtitle_font, palette["muted"])

    # Thin separator
    y += 14
    draw.rounded_rectangle((margin, y, width - margin, y + 2), radius=1, fill=palette["line"])
    y += 32

    accents = palette["accents"]
    for idx, (node, meas) in enumerate(zip(nodes, measured), 1):
        card_h, tl, bl = meas
        _draw_card(
            draw, node, (margin, y, width - margin, y + card_h),
            accent=accents[(idx - 1) % len(accents)],
            palette=palette, index=idx,
            title_font=card_title_font, body_font=body_font,
            title_lines=tl, body_lines=bl,
        )
        if idx < len(nodes):
            _draw_arrow(draw, width // 2, y + card_h + 4, y + card_h + gap - 10, palette["line"])
        y += card_h + gap

    if footer_lines:
        y += 20
        _draw_wrapped(draw, footer_lines, (margin, y), footer_font, palette["muted"])

    output_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(output_path, format="PNG", optimize=True)


# ---------------------------------------------------------------------------
# Mindmap layout (central hub, cards branching left/right)
# ---------------------------------------------------------------------------
def _render_mindmap(spec: dict[str, Any], output_path: Path, palette: dict[str]) -> None:
    width = int(spec.get("width", 2000))
    margin = 80
    gap = 40
    title_font = _font(72, bold=True)
    subtitle_font = _font(36)
    card_title_font = _font(36, bold=True)
    body_font = _font(28)
    footer_font = _font(24)

    scratch = Image.new("RGB", (width, 200), palette["bg"])
    draw = ImageDraw.Draw(scratch)
    nodes = _normalize_nodes(spec)
    card_w = (width - margin * 2 - gap) // 2
    measured = [_measure_card(draw, n, card_w, card_title_font, body_font) for n in nodes]

    # Hub sizing
    hub_title = spec.get("title", "Карта")
    hub_sub = spec.get("subtitle", "")
    hub_font = _font(48, bold=True)
    hub_sub_font = _font(30)
    hub_pad = 48
    hub_w = _tw(draw, hub_title, hub_font) + hub_pad * 2
    hub_h_val = 64

    # Title + subtitle above hub
    title_lines = _wrap(draw, hub_title, title_font, width - margin * 2)
    subtitle_lines = _wrap(draw, hub_sub, subtitle_font, width - margin * 2)
    footer_lines = _wrap(draw, spec.get("footer", ""), footer_font, width - margin * 2)

    head_h = margin
    head_h += len(title_lines) * (_lh(title_font) + 6)
    if subtitle_lines:
        head_h += 20 + len(subtitle_lines) * (_lh(subtitle_font) + 4)
    head_h += 60 + hub_h_val + 40

    # Calculate column heights
    col_y = [head_h, head_h]
    for i, meas in enumerate(measured):
        col = i % 2
        col_y[col] += meas[0] + gap

    # Balance shorter column by adding centering offset
    max_col_h = max(col_y)
    min_col_h = min(col_y)
    col_offsets = [0, 0]
    if max_col_h - min_col_h > 20:
        shorter_idx = 0 if col_y[0] < col_y[1] else 1
        col_offsets[shorter_idx] = (max_col_h - min_col_h) // 2

    h = max_col_h + margin
    if footer_lines:
        h += 48 + len(footer_lines) * (_lh(footer_font) + 4)
    h = max(1000, min(h, 14000))

    img = Image.new("RGB", (width, h), palette["bg"])
    draw = ImageDraw.Draw(img)

    # Draw title
    y = margin
    y = _draw_wrapped(draw, title_lines, (margin, y), title_font, palette["ink"], gap=6)
    if subtitle_lines:
        y += 20
        y = _draw_wrapped(draw, subtitle_lines, (margin, y), subtitle_font, palette["muted"])
    y += 30

    # Central hub — large visible pill with the topic name
    hub_center_x = width // 2
    hub_x1 = hub_center_x - hub_w // 2
    hub_x2 = hub_center_x + hub_w // 2
    hub_y_top = y
    draw.rounded_rectangle((hub_x1, hub_y_top, hub_x2, hub_y_top + hub_h_val), radius=32, fill=palette["accents"][0], width=0)
    # Hub shadow
    draw.rounded_rectangle((hub_x1 + 2, hub_y_top + 3, hub_x2 + 2, hub_y_top + hub_h_val + 3), radius=32, fill="#B0C8E0")
    draw.rounded_rectangle((hub_x1, hub_y_top, hub_x2, hub_y_top + hub_h_val), radius=32, fill=palette["accents"][0])
    tw_hub = _tw(draw, hub_title, hub_font)
    lh_hub = _lh(hub_font)
    draw.text((hub_center_x - tw_hub // 2, hub_y_top + (hub_h_val - lh_hub) // 2), hub_title, font=hub_font, fill="#FFFFFF")

    hub_bottom = hub_y_top + hub_h_val

    # Branch lines from hub bottom to card tops
    acc = palette["accents"]
    col_y_reset = [head_h, head_h]

    # Draw all connector lines first (cards drawn on top so lines don't show through)
    for idx, (node, meas) in enumerate(zip(nodes, measured), 1):
        col = (idx - 1) % 2
        x1 = margin + col * (card_w + gap)
        y1 = col_y_reset[col] + col_offsets[col]
        card_cx = x1 + card_w // 2
        # Vertical line from hub bottom to this card's top
        draw.line((card_cx, hub_bottom + 6, card_cx, y1 - 4), fill=palette["line"], width=2)
        # Small dots at both ends
        draw.ellipse((card_cx - 4, hub_bottom + 2, card_cx + 4, hub_bottom + 10), fill=palette["accents"][(idx - 1) % len(acc)])
        draw.ellipse((card_cx - 4, y1 - 6, card_cx + 4, y1 + 2), fill=palette["accents"][(idx - 1) % len(acc)])

    # Draw cards ON TOP of the lines so lines only show in the gap
    col_y_reset = [head_h, head_h]
    for idx, (node, meas) in enumerate(zip(nodes, measured), 1):
        col = (idx - 1) % 2
        x1 = margin + col * (card_w + gap)
        y1 = col_y_reset[col] + col_offsets[col]
        card_h, tl, bl = meas

        _draw_card(
            draw, node, (x1, y1, x1 + card_w, y1 + card_h),
            accent=acc[(idx - 1) % len(acc)],
            palette=palette, index=None,
            title_font=card_title_font, body_font=body_font,
            title_lines=tl, body_lines=bl,
        )
        col_y_reset[col] += card_h + gap

    if footer_lines:
        yf = max(col_y_reset) + 8
        _draw_wrapped(draw, footer_lines, (margin, yf), footer_font, palette["muted"])

    output_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(output_path, format="PNG", optimize=True)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------
def render(spec: dict[str, Any], output_path: str | Path) -> Path:
    palette = PALETTES.get(str(spec.get("palette", "ocean")), PALETTES["ocean"])
    out = Path(output_path)
    layout = str(spec.get("layout", "flow")).lower()
    if layout in {"mindmap", "map", "cluster", "clusters"}:
        _render_mindmap(spec, out, palette)
    else:
        _render_flow(spec, out, palette)
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description="Render mind-map JSON spec to PNG")
    parser.add_argument("spec", help="Path to UTF-8 JSON spec")
    parser.add_argument("output", help="Path to output PNG")
    args = parser.parse_args()

    with Path(args.spec).open("r", encoding="utf-8") as fh:
        spec = json.load(fh)
    out = render(spec, args.output)
    from PIL import Image
    with Image.open(out) as img:
        print(f"OK {out} {img.size[0]}x{img.size[1]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
