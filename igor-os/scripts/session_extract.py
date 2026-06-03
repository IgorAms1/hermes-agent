#!/usr/bin/env python3
"""Read-only Hermes session extractor for Igor OS skills.

Reads ~/.hermes/sessions JSON/JSONL files directly and emits compact JSON.
Designed for morning/evening skills when multiple session_search calls would be
slower or fragile around stale message IDs.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

try:
    from zoneinfo import ZoneInfo
except Exception:  # pragma: no cover - Python <3.9 fallback is not expected here.
    ZoneInfo = None  # type: ignore

DEFAULT_SIGNALS = (
    "completed", "done", "finished", "sent", "closed", "cancel", "cancelled",
    "завершил", "завершила", "сделал", "сделала", "готово", "отправил",
    "отправила", "закрыл", "закрыла", "перенос", "перенёс", "перенес",
    "отмена", "завтра", "tomorrow", "коррекция", "поправка", "неверно",
    "неправильно", "забыл", "уже",
)

SKILL_PROMPT_MARKERS = (
    '[IMPORTANT: The user has invoked the "',
    'The full skill content is loaded below.',
)

VOICE_RE = re.compile(r"\[The user sent a voice message~ Here's what they said: \"(.*)\"\]", re.S)


def _local_today() -> datetime:
    if ZoneInfo is not None:
        return datetime.now(ZoneInfo("Europe/Amsterdam"))
    return datetime.now()


def _target_date(value: str) -> str:
    today = _local_today().date()
    if value == "today":
        return today.strftime("%Y%m%d")
    if value == "yesterday":
        return (today - timedelta(days=1)).strftime("%Y%m%d")
    if re.fullmatch(r"\d{8}", value):
        return value
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        return value.replace("-", "")
    raise SystemExit(f"Unsupported --date value: {value!r}; use today, yesterday, YYYY-MM-DD, or YYYYMMDD")


def _sessions_dir() -> Path:
    root = os.environ.get("HERMES_HOME") or str(Path.home() / ".hermes")
    return Path(root) / "sessions"


def _session_id_from_path(path: Path) -> str:
    name = path.name
    if name.startswith("session_") and name.endswith(".json"):
        return name[len("session_") : -len(".json")]
    if name.endswith(".jsonl"):
        return name[:-len(".jsonl")]
    return path.stem


def _candidate_files(root: Path, yyyymmdd: str) -> list[Path]:
    if not root.exists():
        return []
    files = []
    for path in root.iterdir():
        if not path.is_file():
            continue
        if path.suffix not in {".json", ".jsonl"}:
            continue
        if path.name == "sessions.json":
            continue
        if yyyymmdd not in path.name:
            continue
        files.append(path)

    # Prefer full JSON dumps over JSONL for the same session id, and newer files first.
    chosen: dict[str, Path] = {}
    for path in sorted(files, key=lambda p: (p.stat().st_mtime, p.suffix == ".json"), reverse=True):
        sid = _session_id_from_path(path)
        current = chosen.get(sid)
        if current is None or (current.suffix == ".jsonl" and path.suffix == ".json"):
            chosen[sid] = path
    return sorted(chosen.values(), key=lambda p: p.stat().st_mtime, reverse=True)


def _load_json_messages(path: Path) -> list[dict[str, Any]]:
    data = json.loads(path.read_text(errors="replace"))
    if isinstance(data, dict):
        messages = data.get("messages", [])
        if isinstance(messages, list):
            return [m for m in messages if isinstance(m, dict)]
    if isinstance(data, list):
        return [m for m in data if isinstance(m, dict)]
    return []


def _load_jsonl_messages(path: Path) -> list[dict[str, Any]]:
    messages = []
    with path.open("r", encoding="utf-8", errors="replace") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            try:
                value = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(value, dict):
                messages.append(value)
    return messages


def _load_messages(path: Path) -> list[dict[str, Any]]:
    try:
        if path.suffix == ".jsonl":
            return _load_jsonl_messages(path)
        return _load_json_messages(path)
    except Exception as exc:
        return [{"role": "error", "content": f"failed to parse {path.name}: {exc}"}]


def _normalize_content(value: Any) -> str:
    if isinstance(value, str):
        text = value
    elif isinstance(value, list):
        parts = []
        for item in value:
            if isinstance(item, dict):
                if isinstance(item.get("text"), str):
                    parts.append(item["text"])
                elif isinstance(item.get("content"), str):
                    parts.append(item["content"])
            elif isinstance(item, str):
                parts.append(item)
        text = "\n".join(parts)
    else:
        text = str(value) if value is not None else ""

    voice = VOICE_RE.search(text)
    if voice:
        text = voice.group(1)
    return re.sub(r"\s+", " ", text).strip()


def _query_terms(query: str) -> list[str]:
    if not query:
        return []
    pieces = re.split(r"\s+OR\s+|\|", query, flags=re.I)
    return [p.strip().lower() for p in pieces if p.strip()]


def _matches_query(content: str, terms: list[str], require_all: bool) -> bool:
    if not terms:
        return True
    lower = content.lower()
    if require_all:
        return all(term in lower for term in terms)
    return any(term in lower for term in terms)


def _signals(content: str) -> list[str]:
    lower = content.lower()
    return [term for term in DEFAULT_SIGNALS if term.lower() in lower]


def main() -> int:
    parser = argparse.ArgumentParser(description="Extract compact raw messages from Hermes session files.")
    parser.add_argument("--date", default="today", help="today, yesterday, YYYY-MM-DD, or YYYYMMDD")
    parser.add_argument("--sessions-dir", default="", help="Override sessions directory; defaults to $HERMES_HOME/sessions")
    parser.add_argument("--roles", default="user", help="Comma-separated roles, e.g. user or user,assistant")
    parser.add_argument("--query", default="", help="Case-insensitive query; split alternatives with OR")
    parser.add_argument("--require-all", action="store_true", help="Require all query terms instead of any")
    parser.add_argument("--limit", type=int, default=40, help="Max messages returned")
    parser.add_argument("--max-chars", type=int, default=500, help="Max content chars per message")
    parser.add_argument("--session-limit", type=int, default=8, help="Max session files to scan")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON")
    parser.add_argument("--include-skill-prompts", action="store_true", help="Include internal skill invocation prompts")
    parser.add_argument("--no-dedupe", action="store_true", help="Do not deduplicate repeated content across session dumps")
    args = parser.parse_args()

    yyyymmdd = _target_date(args.date)
    root = Path(args.sessions_dir).expanduser() if args.sessions_dir else _sessions_dir()
    roles = {r.strip() for r in args.roles.split(",") if r.strip()}
    terms = _query_terms(args.query)

    files = _candidate_files(root, yyyymmdd)[: max(1, args.session_limit)]
    results = []
    seen_content = set()
    scanned_messages = 0
    scanned_sessions = []

    for path in files:
        sid = _session_id_from_path(path)
        messages = _load_messages(path)
        scanned_sessions.append({
            "session_id": sid,
            "file": str(path),
            "message_count": len(messages),
            "mtime": datetime.fromtimestamp(path.stat().st_mtime).isoformat(timespec="seconds"),
        })
        for msg in messages:
            role = str(msg.get("role", ""))
            if roles and role not in roles:
                continue
            content = _normalize_content(msg.get("content", ""))
            if not content:
                continue
            if not args.include_skill_prompts and any(marker in content for marker in SKILL_PROMPT_MARKERS):
                continue
            scanned_messages += 1
            if not _matches_query(content, terms, args.require_all):
                continue
            content_hash = hashlib.sha256(content.encode("utf-8", "ignore")).hexdigest()
            if not args.no_dedupe and content_hash in seen_content:
                continue
            seen_content.add(content_hash)
            item = {
                "session_id": sid,
                "message_id": msg.get("id") or msg.get("message_id"),
                "role": role,
                "timestamp": msg.get("timestamp") or msg.get("created_at") or "",
                "signals": _signals(content),
                "content": content[: args.max_chars],
            }
            if len(content) > args.max_chars:
                item["truncated"] = True
            results.append(item)
            if len(results) >= args.limit:
                break
        if len(results) >= args.limit:
            break

    output = {
        "date": yyyymmdd,
        "sessions_dir": str(root),
        "sessions_scanned": scanned_sessions,
        "messages_considered": scanned_messages,
        "query": args.query,
        "roles": sorted(roles),
        "result_count": len(results),
        "results": results,
    }
    print(json.dumps(output, ensure_ascii=False, indent=2 if args.pretty else None))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
