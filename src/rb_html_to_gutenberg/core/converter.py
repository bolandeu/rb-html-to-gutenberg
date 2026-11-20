"""Конвертация HTML в Gutenberg блоки WordPress."""

import json
import logging
from collections.abc import Callable
from dataclasses import dataclass, field

from bs4 import BeautifulSoup, NavigableString, Tag
from bs4.element import PreformattedString

logger = logging.getLogger(__name__)

# Wrappers with no block of their own: their children are converted in place,
# so an article wrapped in <div>/<section> is not lost.
CONTAINER_TAGS = frozenset({"html", "body", "div", "section", "article", "main", "header", "footer", "aside"})
# Never content: dropped, but always reported in warnings.
DROP_TAGS = frozenset({"head", "title", "meta", "link", "script", "style", "noscript", "template"})
# Runs of loose text and these tags are joined into one paragraph.
INLINE_TAGS = frozenset(
    {
        "a", "abbr", "b", "bdi", "bdo", "br", "cite", "code", "del", "dfn", "em", "i", "ins", "kbd",
        "mark", "q", "s", "samp", "small", "span", "strong", "sub", "sup", "time", "u", "var", "wbr",
    }
)  # fmt: skip


@dataclass
class Conversion:
    """Conversion result: block markup plus warnings about anything that did not become a native block."""

    blocks: str
    warnings: list[str] = field(default_factory=list)


class HtmlToGutenberg:
    """Конвертер HTML в формат Gutenberg блоков WordPress.

    Nothing is dropped silently: wrappers are unwrapped, tags without a
    native block are kept as `wp:html`, and non-content tags (`script`,
    `head`, ...) are dropped with a warning in `Conversion.warnings`.
    """

    def __init__(self) -> None:
        # A handler returns None when it can't produce a native block; the
        # element is then kept as a Custom HTML (wp:html) block.
        self.tag_mapping: dict[str, Callable[[Tag], str | None]] = {
            "p": self._convert_paragraph,
            "h1": self._convert_heading,
            "h2": self._convert_heading,
            "h3": self._convert_heading,
            "h4": self._convert_heading,
            "h5": self._convert_heading,
            "h6": self._convert_heading,
            "img": self._convert_image,
            "ul": self._convert_list,
            "ol": self._convert_list,
            "table": self._convert_table,
            "blockquote": self._convert_blockquote,
            "hr": self._convert_separator,
            "pre": self._convert_pre,
            "figure": self._convert_figure,
            "details": self._convert_details,
            "video": self._convert_media,
            "audio": self._convert_media,
        }
        self._warnings: list[str] = []

    def convert(self, html: str) -> str:
        """Конвертировать HTML строку в Gutenberg блоки."""
        return self.convert_report(html).blocks

    def convert_report(self, html: str) -> Conversion:
        """Convert and also return warnings (each is logged via `logging` as well)."""
        self._warnings = []
        blocks = self._convert_children(BeautifulSoup(html, "html.parser"))
        for warning in self._warnings:
            logger.warning(warning)
        return Conversion("\n".join(blocks), self._warnings)

    def _convert_children(self, parent: Tag) -> list[str]:
        blocks: list[str] = []
        run: list[str] = []
        for node in parent.children:
            if isinstance(node, PreformattedString):  # comments, doctype, CDATA
                continue
            if isinstance(node, NavigableString):
                run.append(node.output_ready())
            elif isinstance(node, Tag) and node.name in INLINE_TAGS:
                run.append(str(node))
            elif isinstance(node, Tag):
                self._flush_inline(run, blocks)
                blocks.extend(self._convert_element(node))
        self._flush_inline(run, blocks)
        return blocks

    def _flush_inline(self, run: list[str], blocks: list[str]) -> None:
        content = "".join(run).replace("\n", " ").strip()
        run.clear()
        if content:
            blocks.append(f"<!-- wp:paragraph -->\n<p>{content}</p>\n<!-- /wp:paragraph -->")

    def _convert_element(self, element: Tag) -> list[str]:
        name = element.name
        if name in DROP_TAGS:
            self._warnings.append(f"<{name}> dropped: not article content")
            return []
        if name in CONTAINER_TAGS:
            return self._convert_children(element)
        handler = self.tag_mapping.get(name)
        block = handler(element) if handler else None
        if block:
            return [block]
        self._warnings.append(f"<{name}> kept as Custom HTML (wp:html): no native block for it")
        return [f"<!-- wp:html -->\n{element}\n<!-- /wp:html -->"]

    def _convert_paragraph(self, element: Tag) -> str:
        content = str(element).replace("\n", "").strip()
        return f"<!-- wp:paragraph -->\n{content}\n<!-- /wp:paragraph -->"

    def _convert_heading(self, element: Tag) -> str:
        level = int(element.name[1])
        content = element.decode_contents().strip()
        return (
            f'<!-- wp:heading {{"level":{level}}} -->\n<{element.name}>{content}</{element.name}>\n<!-- /wp:heading -->'
        )

    def _convert_image(self, element: Tag, caption: str = "") -> str | None:
        src = element.get("src", "")
        alt = element.get("alt", "")
        if not src:
            return None
        attrs = {"src": src}
        if alt:
            attrs["alt"] = alt
        attrs_json = json.dumps(attrs)
        return f'<!-- wp:image {attrs_json} -->\n<figure class="wp-block-image"><img src="{src}" alt="{alt}"/>{caption}</figure>\n<!-- /wp:image -->'

    def _convert_list(self, element: Tag) -> str:
        ordered = element.name == "ol"
        items = [f"<li>{li.decode_contents().strip()}</li>" for li in element.find_all("li", recursive=False)]
        list_content = "\n".join(items)
        tag = "ol" if ordered else "ul"
        attrs = {"ordered": True} if ordered else {}
        attrs_json = json.dumps(attrs)
        return f"<!-- wp:list {attrs_json} -->\n<{tag}>\n{list_content}\n</{tag}>\n<!-- /wp:list -->"

    def _convert_table(self, element: Tag, caption: str = "") -> str:
        thead = element.find("thead")
        tbody = element.find("tbody")
        if thead or tbody:
            parts: list[str] = []
            if thead:
                parts.append(str(thead).replace("\n", "").strip())
            if tbody:
                parts.append(str(tbody).replace("\n", "").strip())
            table_content = "".join(parts)
        else:
            table_content = str(element).replace("\n", "").strip()
        return f'<!-- wp:table -->\n<figure class="wp-block-table"><table class="has-fixed-layout">{table_content}</table>{caption}</figure>\n<!-- /wp:table -->'

    def _convert_blockquote(self, element: Tag) -> str:
        content = element.decode_contents().strip()
        return f'<!-- wp:quote -->\n<blockquote class="wp-block-quote">{content}</blockquote>\n<!-- /wp:quote -->'

    def _convert_separator(self, element: Tag) -> str:
        return (
            '<!-- wp:separator -->\n<hr class="wp-block-separator has-alpha-channel-opacity"/>\n<!-- /wp:separator -->'
        )

    def _convert_pre(self, element: Tag) -> str:
        children = [c for c in element.children if not (isinstance(c, NavigableString) and not c.strip())]
        if len(children) == 1 and isinstance(children[0], Tag) and children[0].name == "code":
            code = children[0].decode_contents()
            return f'<!-- wp:code -->\n<pre class="wp-block-code"><code>{code}</code></pre>\n<!-- /wp:code -->'
        content = element.decode_contents()
        return (
            f'<!-- wp:preformatted -->\n<pre class="wp-block-preformatted">{content}</pre>\n<!-- /wp:preformatted -->'
        )

    def _convert_figure(self, element: Tag) -> str | None:
        """A <figure> with exactly one img or table (+ optional figcaption); otherwise None (-> wp:html)."""
        tags = [c for c in element.children if isinstance(c, Tag)]
        body = [t for t in tags if t.name != "figcaption"]
        figcaption = next((t for t in tags if t.name == "figcaption"), None)
        caption = (
            f'<figcaption class="wp-element-caption">{figcaption.decode_contents().strip()}</figcaption>'
            if figcaption
            else ""
        )
        if len(body) != 1:
            return None
        if body[0].name == "img":
            return self._convert_image(body[0], caption)
        if body[0].name == "table":
            return self._convert_table(body[0], caption)
        return None

    def _convert_details(self, element: Tag) -> str:
        summary = element.find("summary", recursive=False)
        summary_html = summary.decode_contents().strip() if summary else ""
        if summary:
            summary.extract()
        inner = "\n".join(self._convert_children(element))
        return (
            f'<!-- wp:details -->\n<details class="wp-block-details"><summary>{summary_html}</summary>'
            f"{inner}</details>\n<!-- /wp:details -->"
        )

    def _convert_media(self, element: Tag) -> str | None:
        source = element.find("source")
        src = element.get("src") or (source.get("src") if source else None)
        if not src:
            return None
        name = element.name
        return f'<!-- wp:{name} -->\n<figure class="wp-block-{name}"><{name} controls src="{src}"></{name}></figure>\n<!-- /wp:{name} -->'
