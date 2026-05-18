#!/usr/bin/env python3
"""Report ChatGPT/Codex usage remaining limits.

This is for Codex plan windows shown in the ChatGPT/Codex UI, e.g.
5h and Weekly remaining percentages. It is NOT the OpenAI organization
costs API.

Requires Hermes OpenAI Codex OAuth credentials (`hermes auth`).
"""

from __future__ import annotations

import sys
from pathlib import Path


def find_repo_root() -> Path:
    here = Path(__file__).resolve()
    for parent in [here.parent, *here.parents]:
        if (parent / "agent" / "account_usage.py").exists():
            return parent
    fallback = Path.home() / "hermes-agent"
    if (fallback / "agent" / "account_usage.py").exists():
        return fallback
    raise RuntimeError("Could not find hermes-agent repo root containing agent/account_usage.py")


def main() -> int:
    repo = find_repo_root()
    sys.path.insert(0, str(repo))

    from agent.account_usage import fetch_account_usage, render_account_usage_lines

    snapshot = fetch_account_usage(
        "openai-codex",
        base_url="https://chatgpt.com/backend-api/codex",
    )
    if not snapshot or not snapshot.available:
        print("Codex limits unavailable")
        print("Needed: usable Hermes OpenAI Codex OAuth credentials.")
        print("Re-auth in remote/Telegram sessions: `hermes auth add openai-codex --type oauth --no-browser`")
        print("Then rerun this script or Telegram `/usage`.")
        print("Note: this is not the OpenAI organization costs API; Codex limits come from ChatGPT/Codex account usage.")
        return 2

    print("Codex usage remaining")
    for line in render_account_usage_lines(snapshot)[1:]:
        print(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
