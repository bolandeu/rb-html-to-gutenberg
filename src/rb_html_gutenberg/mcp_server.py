"""MCP-сервер для rb-html-gutenberg."""

from __future__ import annotations

from mcp.server import Server
from mcp.types import TextContent

from .core.html_to_gutenberg import HtmlToGutenberg

server = Server("rb-html-gutenberg")


@server.tool()
async def convert_to_gutenberg(html: str) -> list[TextContent]:
    """Конвертировать HTML в WordPress Gutenberg блоки.

    Поддерживает: p, h1-h6, ul/ol, table, blockquote, img, strong/em.
    """
    converter = HtmlToGutenberg()
    result = converter.convert(html)
    return [TextContent(type="text", text=result)]


def serve():
    """Entry-point для MCP."""
    import asyncio
    asyncio.run(server.run())


if __name__ == "__main__":
    serve()
