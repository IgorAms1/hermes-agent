from pathlib import Path
import re

import yaml


REPO_ROOT = Path(__file__).resolve().parents[2]
IGOR_OS = REPO_ROOT / "igor-os"


def _read(path: str) -> str:
    return (IGOR_OS / path).read_text(encoding="utf-8")


def test_morning_skill_uses_real_recall_surfaces():
    text = _read("skills/morning/SKILL.md")

    assert "session_search" in text
    assert "delegate_task" in text
    assert '$HERMES_HOME/sessions/' in text
    assert '$HERMES_HOME/memories/MEMORY.md' in text
    assert "always run a memory search" not in text


def test_evening_skill_does_not_claim_session_search_has_date_filter():
    text = _read("skills/evening/SKILL.md")

    assert "current visible Telegram conversation" in text
    assert "Use returned timestamps" in text
    assert '$HERMES_HOME/sessions/' in text
    assert "for today's date with query" not in text


def test_extract_skill_names_memory_tool_explicitly():
    text = _read("skills/extract/SKILL.md")

    assert "the `memory` tool" in text
    assert 'memory(action="add", target=...)' in text
    assert "memory()" not in text


def test_cron_examples_use_concrete_telegram_delivery_target():
    text = _read("cron/examples.md")
    readme = (REPO_ROOT / "README_IGOR_OS.md").read_text(encoding="utf-8")

    assert 'TELEGRAM_TARGET="telegram:1321905"' in text
    assert '--deliver "$TELEGRAM_TARGET"' in text
    assert "--deliver telegram" not in text
    assert "--deliver telegram " not in readme


def test_igor_os_docs_do_not_reference_legacy_memory_function_name():
    offenders = []
    for path in IGOR_OS.rglob("*.md"):
        if "memory()" in path.read_text(encoding="utf-8"):
            offenders.append(path.relative_to(REPO_ROOT).as_posix())

    assert offenders == []


def test_deep_research_skill_contract():
    text = _read("skills/deep_research/SKILL.md")

    assert "Clarify First" in text
    assert "Language And Encoding" in text
    assert "Match the user's language" in text
    assert "UTF-8" in text
    assert "Minimize unnecessary English code-switching" in text
    assert "daily driver" in text
    assert "product facts" in text
    assert "Executive Answer" in text
    assert "Короткий вывод" in text
    assert "Доказательная база" in text
    assert "summary labels" in text
    assert "Исследование: <тема>" in text
    assert "Уверенность" in text
    assert "Полный отчет приложен" in text
    assert "Do not send a corrupted report" in text
    assert "delegate_task" in text
    assert '"tasks"' in text
    assert '"toolsets": ["web"]' in text
    assert "$HERMES_HOME/research/YYYY-MM-DD-<topic-slug>/" in text
    assert "report.md" in text
    assert "send_message" in text
    assert "[[as_document]] MEDIA:" in text
    assert "Telegram Output" in text
    assert "Do not use for quick factual answers" in text


def test_deep_research_is_registered_in_igor_os_docs():
    hermes_context = _read(".hermes.md")
    telegram_commands = _read("workflows/telegram-commands.md")
    readme = (REPO_ROOT / "README_IGOR_OS.md").read_text(encoding="utf-8")

    assert "/deep_research" in hermes_context
    assert "/deep_research" in telegram_commands
    assert "/deep_research" in readme
    assert "deep_research/SKILL.md" in readme


def test_mindmap_skill_contract():
    text = _read("skills/mindmap/SKILL.md")

    assert "render_mindmap.py" in text
    assert "$HERMES_HOME/mindmaps/YYYY-MM-DD-<topic-slug>/" in text
    assert '"layout": "flow"' in text
    assert '"nodes"' in text
    assert "MEDIA:/absolute/path/to/mindmap.png" in text
    assert "send_message" in text
    assert "If image sending fails" in text
    assert "Match Igor's language" in text
    assert "most recent relevant `$HERMES_HOME/research/**/report.md`" in text


def test_mindmap_is_registered_in_igor_os_docs():
    hermes_context = _read(".hermes.md")
    telegram_commands = _read("workflows/telegram-commands.md")
    readme = (REPO_ROOT / "README_IGOR_OS.md").read_text(encoding="utf-8")

    assert "/mindmap" in hermes_context
    assert "/mindmap" in telegram_commands
    assert "/mindmap" in readme
    assert "mindmap/SKILL.md" in readme
    assert "render_mindmap.py" in readme


def test_igor_os_skill_frontmatter_names_match_directories():
    errors = []
    for skill_file in sorted((IGOR_OS / "skills").glob("*/SKILL.md")):
        text = skill_file.read_text(encoding="utf-8")
        match = re.match(r"---\n(.*?)\n---\n", text, re.S)
        if not match:
            errors.append(f"{skill_file}: missing frontmatter")
            continue
        frontmatter = yaml.safe_load(match.group(1)) or {}
        if frontmatter.get("name") != skill_file.parent.name:
            errors.append(
                f"{skill_file}: name {frontmatter.get('name')!r} != {skill_file.parent.name!r}"
            )
        if not frontmatter.get("description"):
            errors.append(f"{skill_file}: missing description")

    assert errors == []
