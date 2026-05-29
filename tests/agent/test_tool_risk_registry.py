import json

from agent.tool_risk_registry import (
    CRITICAL_SYSTEM,
    EXPLICIT_TOOL_RISK_POLICIES,
    READ_ONLY,
    build_tool_risk_audit_event,
    classify_tool_risk,
)
from toolsets import resolve_toolset


def test_hermes_cli_tools_have_explicit_risk_policies():
    missing = sorted(set(resolve_toolset("hermes-cli")) - set(EXPLICIT_TOOL_RISK_POLICIES))
    assert missing == []


def test_critical_tools_are_marked_for_confirmation():
    critical_tools = {
        "terminal",
        "execute_code",
        "write_file",
        "patch",
        "skill_manage",
        "cronjob",
    }

    for tool_name in critical_tools:
        policy = classify_tool_risk(tool_name)
        assert policy.risk_level == CRITICAL_SYSTEM
        assert policy.requires_confirmation is True
        assert policy.direct_user_only is True
        assert policy.blocks_indirect_context is True


def test_read_only_tools_do_not_require_confirmation():
    read_only_tools = {
        "read_file",
        "search_files",
        "web_search",
        "web_extract",
        "session_search",
        "skills_list",
        "skill_view",
        "browser_snapshot",
    }

    for tool_name in read_only_tools:
        policy = classify_tool_risk(tool_name)
        assert policy.risk_level == READ_ONLY
        assert policy.requires_confirmation is False


def test_audit_event_omits_raw_argument_values():
    event = build_tool_risk_audit_event(
        "terminal",
        {
            "command": "cat ~/.hermes/.env",
            "api_key": "sk-secret-value",
            "path": "/home/igor1/.hermes/auth.json",
        },
        source_context="telegram",
    )

    encoded = json.dumps(event, ensure_ascii=False, sort_keys=True)
    assert "cat ~/.hermes/.env" not in encoded
    assert "sk-secret-value" not in encoded
    assert "/home/igor1/.hermes/auth.json" not in encoded
    assert event["arg_keys"] == ["api_key", "command", "path"]
    assert event["sensitive_arg_keys"] == ["api_key"]
    assert len(event["args_hash"]) == 64
    assert event["risk_level"] == CRITICAL_SYSTEM
