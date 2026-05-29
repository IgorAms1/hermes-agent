"""Audit-only sensitive path and secret access detection.

The helpers in this module are intentionally non-blocking. They classify common
credential locations and emit structured audit metadata without logging raw
paths, commands, code, or file contents.
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Mapping


@dataclass(frozen=True)
class SensitiveReference:
    """A sensitive reference found in a path, glob, command, or code string."""

    category: str
    reference_hash: str
    matched_by: str

    def to_audit_dict(self) -> dict[str, str]:
        return asdict(self)


_SECRET_BASENAMES = frozenset(
    {
        ".env",
        "auth.json",
        "google_token.json",
        "google_client_secret.json",
        "authorized_keys",
        "id_rsa",
        "id_dsa",
        "id_ecdsa",
        "id_ed25519",
        "known_hosts",
        "config",
    }
)

_SECRET_TEXT_PATTERNS: tuple[tuple[re.Pattern[str], str, str], ...] = (
    (re.compile(r"(?:^|[\s'\"=:/])(?:~|\$HOME)?/?\.hermes/\.env(?:$|[\s'\";|&])"), "hermes_env", "hermes_env_path"),
    (re.compile(r"(?:^|[\s'\"=:/])(?:~|\$HOME)?/?\.hermes/auth\.json(?:$|[\s'\";|&])"), "hermes_auth", "hermes_auth_path"),
    (re.compile(r"(?:^|[\s'\"=:/])(?:~|\$HOME)?/?\.hermes/google_token\.json(?:$|[\s'\";|&])"), "google_oauth_token", "google_token_path"),
    (re.compile(r"(?:^|[\s'\"=:/])(?:~|\$HOME)?/?\.hermes/google_client_secret\.json(?:$|[\s'\";|&])"), "google_client_secret", "google_client_secret_path"),
    (re.compile(r"(?:^|[\s'\"=:/])(?:~|\$HOME)?/?\.ssh(?:/|$)"), "ssh_secret", "ssh_path"),
    (re.compile(r"(?:^|[\s'\"=:/])\.env(?:$|[\s'\";|&])"), "repo_env", "repo_env_path"),
)


def _hash_reference(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8", errors="replace")).hexdigest()


def _canonical_path_string(path: str) -> str:
    raw = str(path or "").strip()
    if not raw:
        return ""
    expanded = os.path.expandvars(os.path.expanduser(raw))
    try:
        return str(Path(expanded).resolve(strict=False))
    except (OSError, RuntimeError):
        return expanded


def classify_sensitive_path(path: str) -> SensitiveReference | None:
    """Classify a single path-like string without reading from disk."""

    canonical = _canonical_path_string(path)
    if not canonical:
        return None

    home = _canonical_path_string("~")
    default_hermes_home = _canonical_path_string("~/.hermes")
    configured_hermes_home = _canonical_path_string(os.getenv("HERMES_HOME", "~/.hermes"))
    hermes_homes = {default_hermes_home, configured_hermes_home}
    ssh_dir = _canonical_path_string("~/.ssh")
    name = Path(canonical).name

    exact_categories: dict[str, str] = {}
    for hermes_home in hermes_homes:
        exact_categories.update(
            {
                os.path.join(hermes_home, ".env"): "hermes_env",
                os.path.join(hermes_home, "auth.json"): "hermes_auth",
                os.path.join(hermes_home, "google_token.json"): "google_oauth_token",
                os.path.join(hermes_home, "google_client_secret.json"): "google_client_secret",
            }
        )
    category = exact_categories.get(canonical)
    matched_by = "exact_runtime_path" if category else ""

    if category is None and (canonical == ssh_dir or canonical.startswith(ssh_dir + os.sep)):
        category = "ssh_secret"
        matched_by = "ssh_dir"

    if category is None and name == ".env":
        category = "env_file"
        matched_by = "env_basename"

    if category is None and name in _SECRET_BASENAMES and canonical.startswith(home + os.sep):
        category = "home_secret_candidate"
        matched_by = "home_secret_basename"

    if category is None:
        return None

    return SensitiveReference(
        category=category,
        reference_hash=_hash_reference(canonical),
        matched_by=matched_by,
    )


def find_sensitive_references(text: str) -> list[SensitiveReference]:
    """Find sensitive path references in arbitrary command/code/glob text."""

    if not isinstance(text, str) or not text:
        return []

    found: list[SensitiveReference] = []
    seen: set[tuple[str, str, str]] = set()

    direct = classify_sensitive_path(text)
    if direct is not None:
        found.append(direct)
        seen.add((direct.category, direct.reference_hash, direct.matched_by))

    for pattern, category, matched_by in _SECRET_TEXT_PATTERNS:
        for match in pattern.finditer(text):
            matched = match.group(0).strip(" \t\n\r'\";|&=:")
            ref = SensitiveReference(
                category=category,
                reference_hash=_hash_reference(matched),
                matched_by=matched_by,
            )
            key = (ref.category, ref.reference_hash, ref.matched_by)
            if key not in seen:
                found.append(ref)
                seen.add(key)

    return found


def build_sensitive_access_audit_event(
    surface: str,
    value: str,
    *,
    metadata: Mapping[str, Any] | None = None,
) -> dict[str, Any] | None:
    """Return an audit event with no raw sensitive values, or None."""

    refs = find_sensitive_references(value)
    if not refs:
        return None
    safe_metadata = {str(k): str(v) for k, v in (metadata or {}).items()}
    return {
        "event": "sensitive_access_audit",
        "surface": surface,
        "reference_count": len(refs),
        "references": [ref.to_audit_dict() for ref in refs],
        "metadata": safe_metadata,
        "value_hash": _hash_reference(value),
    }


def log_sensitive_access_audit(
    logger: logging.Logger,
    surface: str,
    value: str,
    *,
    metadata: Mapping[str, Any] | None = None,
) -> None:
    """Log an audit-only sensitive-access event without changing behavior."""

    try:
        event = build_sensitive_access_audit_event(surface, value, metadata=metadata)
        if event is not None:
            logger.warning("sensitive_access_audit %s", json.dumps(event, ensure_ascii=False, sort_keys=True))
    except Exception:
        logger.debug("sensitive access audit failed for %s", surface, exc_info=True)


__all__ = [
    "SensitiveReference",
    "build_sensitive_access_audit_event",
    "classify_sensitive_path",
    "find_sensitive_references",
    "log_sensitive_access_audit",
]
