"""Deterministic audit-only risk registry for Hermes tool calls.

This module is intentionally side-effect free except for the optional logging
helper. It does not block, mutate arguments, or make policy decisions for the
runtime yet. The first rollout goal is visibility: every tool call can be
classified without logging raw arguments or secret-bearing values.
"""

from __future__ import annotations

import hashlib
import json
import logging
from dataclasses import asdict, dataclass
from typing import Any, Mapping


READ_ONLY = "read_only"
LOW_RISK_WRITE = "low_risk_write"
MEDIUM_RISK_WRITE = "medium_risk_write"
HIGH_RISK_DELETE = "high_risk_delete"
CRITICAL_SYSTEM = "critical_system"
UNKNOWN = "unknown"


@dataclass(frozen=True)
class ToolRiskPolicy:
    """Static policy metadata for a Hermes tool.

    ``requires_confirmation`` is descriptive in this audit-only phase. Runtime
    enforcement remains unchanged until the registry is wired to a blocking
    policy engine in a later PR.
    """

    tool_name: str
    risk_level: str
    category: str
    requires_confirmation: bool
    direct_user_only: bool
    blocks_indirect_context: bool
    audit_log_required: bool
    rollback_behavior: str
    allowed_parameter_policy: str

    def to_audit_dict(self) -> dict[str, Any]:
        return asdict(self)


EXPLICIT_TOOL_RISK_POLICIES: dict[str, ToolRiskPolicy] = {}


def _register(
    tool_name: str,
    risk_level: str,
    category: str,
    *,
    requires_confirmation: bool = False,
    direct_user_only: bool = False,
    blocks_indirect_context: bool = False,
    audit_log_required: bool = True,
    rollback_behavior: str = "none",
    allowed_parameter_policy: str = "schema_only",
) -> None:
    EXPLICIT_TOOL_RISK_POLICIES[tool_name] = ToolRiskPolicy(
        tool_name=tool_name,
        risk_level=risk_level,
        category=category,
        requires_confirmation=requires_confirmation,
        direct_user_only=direct_user_only,
        blocks_indirect_context=blocks_indirect_context,
        audit_log_required=audit_log_required,
        rollback_behavior=rollback_behavior,
        allowed_parameter_policy=allowed_parameter_policy,
    )


for _tool in (
    "web_search",
    "web_extract",
    "read_file",
    "search_files",
    "vision_analyze",
    "skills_list",
    "skill_view",
    "browser_snapshot",
    "browser_get_images",
    "browser_vision",
    "browser_console",
    "session_search",
    "read_terminal",
    "ha_list_entities",
    "ha_get_state",
    "ha_list_services",
    "kanban_show",
    "kanban_list",
):
    _register(_tool, READ_ONLY, "read_only")


for _tool in (
    "todo",
    "clarify",
    "text_to_speech",
    "image_generate",
    "kanban_heartbeat",
):
    _register(
        _tool,
        LOW_RISK_WRITE,
        "low_risk_write",
        rollback_behavior="delete_created_artifact_or_update_state",
    )


for _tool in (
    "memory",
    "send_message",
    "browser_navigate",
    "browser_click",
    "browser_type",
    "browser_scroll",
    "browser_back",
    "browser_press",
    "browser_dialog",
    "kanban_complete",
    "kanban_block",
    "kanban_comment",
    "kanban_create",
    "kanban_link",
    "kanban_unblock",
):
    _register(
        _tool,
        MEDIUM_RISK_WRITE,
        "state_or_external_write",
        requires_confirmation=True,
        blocks_indirect_context=True,
        rollback_behavior="tool_specific_reverse_action_or_manual_restore",
    )


for _tool in (
    "terminal",
    "execute_code",
    "delegate_task",
    "write_file",
    "patch",
    "skill_manage",
    "cronjob",
    "process",
    "browser_cdp",
    "computer_use",
    "ha_call_service",
):
    _register(
        _tool,
        CRITICAL_SYSTEM,
        "host_or_system_modification",
        requires_confirmation=True,
        direct_user_only=True,
        blocks_indirect_context=True,
        rollback_behavior="pre_change_backup_or_manual_restore_required",
        allowed_parameter_policy="schema_plus_deterministic_policy",
    )


def classify_tool_risk(tool_name: str) -> ToolRiskPolicy:
    """Return risk metadata for ``tool_name``.

    Unknown tools fail open for behavior but classify conservatively for audit.
    """

    policy = EXPLICIT_TOOL_RISK_POLICIES.get(tool_name)
    if policy is not None:
        return policy

    if tool_name.startswith("mcp_filesystem_read") or tool_name.endswith("_read"):
        risk = READ_ONLY
        category = "read_only"
        requires_confirmation = False
    elif tool_name.endswith("_search") or tool_name.endswith("_list"):
        risk = READ_ONLY
        category = "read_only"
        requires_confirmation = False
    else:
        risk = MEDIUM_RISK_WRITE
        category = UNKNOWN
        requires_confirmation = True

    return ToolRiskPolicy(
        tool_name=tool_name,
        risk_level=risk,
        category=category,
        requires_confirmation=requires_confirmation,
        direct_user_only=requires_confirmation,
        blocks_indirect_context=requires_confirmation,
        audit_log_required=True,
        rollback_behavior="unknown_tool_manual_review_required",
        allowed_parameter_policy="unknown_tool_no_raw_args_logged",
    )


def canonical_args_hash(args: Mapping[str, Any] | None) -> str:
    """Hash canonicalized arguments without exposing their values in logs."""

    if not isinstance(args, Mapping):
        args = {}
    canonical = json.dumps(
        args,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        default=str,
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _sensitive_arg_keys(args: Mapping[str, Any] | None) -> list[str]:
    if not isinstance(args, Mapping):
        return []
    markers = ("token", "secret", "key", "password", "credential", "auth")
    return sorted(str(k) for k in args if any(marker in str(k).lower() for marker in markers))


def build_tool_risk_audit_event(
    tool_name: str,
    args: Mapping[str, Any] | None,
    *,
    source_context: str = "unknown",
    execution_blocked: bool = False,
) -> dict[str, Any]:
    """Build a structured audit event that never contains raw arg values."""

    policy = classify_tool_risk(tool_name)
    arg_keys = sorted(str(k) for k in args.keys()) if isinstance(args, Mapping) else []
    return {
        "event": "tool_risk_audit",
        "tool_name": tool_name,
        "risk_level": policy.risk_level,
        "category": policy.category,
        "requires_confirmation": policy.requires_confirmation,
        "direct_user_only": policy.direct_user_only,
        "blocks_indirect_context": policy.blocks_indirect_context,
        "audit_log_required": policy.audit_log_required,
        "rollback_behavior": policy.rollback_behavior,
        "allowed_parameter_policy": policy.allowed_parameter_policy,
        "source_context": source_context or "unknown",
        "execution_blocked": execution_blocked,
        "arg_keys": arg_keys,
        "arg_key_count": len(arg_keys),
        "sensitive_arg_keys": _sensitive_arg_keys(args),
        "args_hash": canonical_args_hash(args),
    }


def log_tool_risk_audit(
    logger: logging.Logger,
    tool_name: str,
    args: Mapping[str, Any] | None,
    *,
    source_context: str = "unknown",
    execution_blocked: bool = False,
) -> None:
    """Emit an audit-only risk event, swallowing failures to preserve behavior."""

    try:
        event = build_tool_risk_audit_event(
            tool_name,
            args,
            source_context=source_context,
            execution_blocked=execution_blocked,
        )
        logger.info("tool_risk_audit %s", json.dumps(event, ensure_ascii=False, sort_keys=True))
    except Exception:
        logger.debug("tool risk audit logging failed for %s", tool_name, exc_info=True)


__all__ = [
    "CRITICAL_SYSTEM",
    "EXPLICIT_TOOL_RISK_POLICIES",
    "HIGH_RISK_DELETE",
    "LOW_RISK_WRITE",
    "MEDIUM_RISK_WRITE",
    "READ_ONLY",
    "ToolRiskPolicy",
    "build_tool_risk_audit_event",
    "canonical_args_hash",
    "classify_tool_risk",
    "log_tool_risk_audit",
]
