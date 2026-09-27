"""`auth status` — the cross-tool credentials report (tools/docs/standard-release.md §8).

This CLI talks to no external service, so it has no credentials: the report
always carries an empty `credentials` list and exits 0. The command exists so
`tools-watch` can poll every tool the same way; its shape is pinned by
`tests/test_auth.py`.
"""

from __future__ import annotations

from datetime import UTC, datetime

import typer

from .. import output
from ..core.errors import InvalidArguments
from ..core.version import DEV_VERSION, installed_version

_CLI = __name__.split(".")[0]

app = output.group("Report credentials (this tool needs none).")


@app.command("status")
@output.guard
def auth_status(
    ctx: typer.Context,
    check: bool = typer.Option(
        False, "--check", help="Also verify each credential with a live call (no-op: this tool has none)."
    ),
    provider: str | None = typer.Option(
        None, "--provider", help="Report only this provider; any name is unknown here (exit 2)."
    ),
    json_output: bool = output.JsonOption,
    quiet: bool = output.QuietOption,
) -> None:
    """Report credentials health in the cross-tool shape; this tool has no credentials.

    Always exits 0 with an empty `credentials` list; --provider NAME exits 2
    (unknown provider). The --json shape is a cross-tool contract: `tool`,
    `version`, `checked_at`, `credentials[]`.

    Example: {cli} auth status --check --json
    """
    if provider is not None:
        raise InvalidArguments(f"Unknown provider '{provider}' (known: none).")
    payload = {
        "tool": _CLI,
        "version": installed_version() or DEV_VERSION,
        "checked_at": datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "credentials": [],
    }
    output.emit_success(ctx, payload, lambda _: output.human.echo("No providers with credentials."))
