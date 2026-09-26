"""CLI-обёртка для rb-html-gutenberg."""

from __future__ import annotations

from pathlib import Path

import click

from .core.html_to_gutenberg import HtmlToGutenberg


@click.command()
@click.argument("input_path", type=click.Path(exists=True))
@click.option("-o", "--output", type=click.Path(), default=None, help="Путь к выходному файлу")
def main(input_path: str, output: str | None) -> None:
    """Конвертировать HTML-файл в формат WordPress Gutenberg блоков."""
    path = Path(input_path)
    html = path.read_text(encoding="utf-8")

    converter = HtmlToGutenberg()
    result = converter.convert(html)

    if output:
        out = Path(output)
        out.write_text(result, encoding="utf-8")
        click.echo(f"Результат → {out}")
    else:
        click.echo(result)


if __name__ == "__main__":
    main()
