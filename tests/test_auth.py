from __future__ import annotations

from datetime import datetime

from .test_cli import invoke, invoke_json

# The §8 report is a cross-tool contract (tools-watch reads it); changing it is breaking.
TOP_KEYS = ["ok", "tool", "version", "checked_at", "credentials"]


def test_auth_status_reports_no_credentials() -> None:
    for args in ((), ("--check",)):
        code, payload = invoke_json("auth", "status", *args)
        assert code == 0
        assert list(payload) == TOP_KEYS
        assert payload["ok"] is True
        assert payload["tool"] == "html_to_gutenberg"
        assert isinstance(payload["version"], str)
        assert payload["checked_at"].endswith("Z")
        assert datetime.fromisoformat(payload["checked_at"].replace("Z", "+00:00")).tzinfo is not None
        assert payload["credentials"] == []


def test_auth_status_human() -> None:
    result = invoke("auth", "status")
    assert result.exit_code == 0
    assert "No providers with credentials." in result.stdout


def test_auth_status_unknown_provider_is_usage_error() -> None:
    code, payload = invoke_json("auth", "status", "--provider", "x")
    assert code == 2
    assert payload["ok"] is False
    assert payload["error"]["code"] == "INVALID_ARGUMENTS"
