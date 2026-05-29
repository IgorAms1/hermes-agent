import json

from agent.sensitive_access import (
    build_sensitive_access_audit_event,
    classify_sensitive_path,
    find_sensitive_references,
)


def test_classifies_runtime_secret_paths():
    cases = {
        "~/.hermes/.env": "hermes_env",
        "~/.hermes/auth.json": "hermes_auth",
        "~/.hermes/google_token.json": "google_oauth_token",
        "~/.hermes/google_client_secret.json": "google_client_secret",
        "~/.ssh/config": "ssh_secret",
        ".env": "env_file",
    }

    for path, category in cases.items():
        ref = classify_sensitive_path(path)
        assert ref is not None
        assert ref.category == category
        assert len(ref.reference_hash) == 64


def test_find_sensitive_references_in_command_without_raw_values():
    refs = find_sensitive_references("cat ~/.hermes/.env && sed -n '1p' ~/.ssh/config")
    categories = {ref.category for ref in refs}

    assert "hermes_env" in categories
    assert "ssh_secret" in categories
    assert all(".env" not in ref.reference_hash for ref in refs)


def test_audit_event_omits_raw_path_command_and_secret_values():
    command = "cat ~/.hermes/auth.json && echo sk-secret-value"
    event = build_sensitive_access_audit_event(
        "terminal.command",
        command,
        metadata={"tool": "terminal"},
    )

    assert event is not None
    encoded = json.dumps(event, ensure_ascii=False, sort_keys=True)
    assert "~/.hermes/auth.json" not in encoded
    assert "sk-secret-value" not in encoded
    assert "cat ~/.hermes/auth.json" not in encoded
    assert event["surface"] == "terminal.command"
    assert event["metadata"] == {"tool": "terminal"}
    assert len(event["value_hash"]) == 64


def test_non_sensitive_values_return_no_event():
    assert classify_sensitive_path("docs/plans/example.md") is None
    assert find_sensitive_references("pytest tests/agent/test_sensitive_access.py") == []
    assert build_sensitive_access_audit_event("terminal.command", "pytest -q") is None


def test_sensitive_access_block_mode_only_blocks_sensitive_values():
    from agent.sensitive_access import should_block_sensitive_access

    assert should_block_sensitive_access("cat ~/.hermes/.env", mode="block") is True
    assert should_block_sensitive_access("cat docs/README.md", mode="block") is False
    assert should_block_sensitive_access("cat ~/.hermes/.env", mode="audit") is False
    assert should_block_sensitive_access("cat ~/.hermes/.env", mode="confirm") is False


def test_sensitive_access_denial_payload_omits_raw_values():
    from agent.sensitive_access import sensitive_access_denied_result

    payload = sensitive_access_denied_result(
        "terminal.command",
        "cat ~/.hermes/google_token.json && echo sk-secret-value",
    )
    encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True)

    assert payload["success"] is False
    assert "google_oauth_token" in payload["reference_categories"]
    assert "~/.hermes/google_token.json" not in encoded
    assert "sk-secret-value" not in encoded
