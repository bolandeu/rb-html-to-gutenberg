from __future__ import annotations

from pathlib import Path

import typer

from .. import output
from ..core import services


@output.guard
def convert(
    ctx: typer.Context,
    input_path: Path = typer.Argument(..., help="HTML file to convert."),
    output_path: Path = typer.Option(None, "-o", "--output", help="Write the result to this file instead of stdout."),
    json_output: bool = output.JsonOption,
    quiet: bool = output.QuietOption,
) -> None:
    """Convert an HTML file to WordPress Gutenberg block markup.

    Top-level p, h1-h6, ul/ol, table, blockquote, img and strong/b/em/i
    become blocks; other top-level tags are skipped. Prints the markup to
    stdout, or writes it to --output (overwriting that file). Needs no
    project. --json returns {"blocks": <markup>, "output": <path or null>}.
    """
    markup = services.convert_file(input_path, output_path)
    output.emit_success(
        ctx,
        {"blocks": markup, "output": str(output_path) if output_path else None},
        # Plain echo, not rich: block markup contains [..] and long lines rich would mangle.
        render_human=lambda d: typer.echo(f"Результат → {d['output']}" if d["output"] else d["blocks"]),
    )
