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

    Native blocks: p, h1-h6, ul/ol, table, blockquote, img, figure (img or
    table + figcaption), hr, pre/code, details, video, audio; loose text and
    inline tags become paragraphs. Wrappers (div, section, article, body,
    ...) are unwrapped. Anything else is kept as a Custom HTML (wp:html)
    block; script/style/head are dropped. Both cases are reported as
    warnings (stderr; "warnings" under --json) — nothing is lost silently.

    Prints the markup to stdout, or writes it to --output (overwriting that
    file). Needs no project. --json returns {"blocks": <markup>,
    "output": <path or null>, "warnings": [...]}.

    Example: {cli} convert page.html -o page.blocks.html
    """
    conversion = services.convert_file(input_path, output_path)
    output.emit_success(
        ctx,
        {
            "blocks": conversion.blocks,
            "output": str(output_path) if output_path else None,
            "warnings": conversion.warnings,
        },
        # Plain echo, not rich: block markup contains [..] and long lines rich would mangle.
        render_human=lambda d: typer.echo(f"Результат → {d['output']}" if d["output"] else d["blocks"]),
    )
