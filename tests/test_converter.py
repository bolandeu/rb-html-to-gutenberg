"""Тесты для HtmlToGutenberg."""

from html_to_gutenberg import HtmlToGutenberg


def test_paragraph():
    html = "<p>Hello world</p>"
    result = HtmlToGutenberg().convert(html)
    assert "<!-- wp:paragraph -->" in result
    assert "<!-- /wp:paragraph -->" in result
    assert "Hello world" in result


def test_heading_levels():
    for level in range(2, 7):
        html = f"<h{level}>Title</h{level}>"
        result = HtmlToGutenberg().convert(html)
        assert f'"level":{level}' in result
        assert "<!-- wp:heading" in result
        assert "Title" in result


def test_unordered_list():
    html = "<ul><li>One</li><li>Two</li></ul>"
    result = HtmlToGutenberg().convert(html)
    assert "<!-- wp:list" in result
    assert "<ul>" in result
    assert "<li>One</li>" in result


def test_ordered_list():
    html = "<ol><li>First</li><li>Second</li></ol>"
    result = HtmlToGutenberg().convert(html)
    assert "<!-- wp:list" in result
    assert '"ordered": true' in result or '"ordered":true' in result
    assert "<ol>" in result


def test_table():
    html = "<table><thead><tr><th>A</th></tr></thead><tbody><tr><td>1</td></tr></tbody></table>"
    result = HtmlToGutenberg().convert(html)
    assert "<!-- wp:table -->" in result
    assert "has-fixed-layout" in result


def test_image():
    html = '<img src="https://example.com/img.jpg" alt="Photo"/>'
    result = HtmlToGutenberg().convert(html)
    assert "<!-- wp:image" in result
    assert "wp-block-image" in result
    assert "https://example.com/img.jpg" in result


def test_blockquote():
    html = "<blockquote>Quote text</blockquote>"
    result = HtmlToGutenberg().convert(html)
    assert "<!-- wp:quote -->" in result
    assert "wp-block-quote" in result


def test_empty_html():
    result = HtmlToGutenberg().convert("")
    assert result == ""


def test_mixed_content():
    html = "<h2>Title</h2><p>Text</p><ul><li>Item</li></ul>"
    result = HtmlToGutenberg().convert(html)
    assert "wp:heading" in result
    assert "wp:paragraph" in result
    assert "wp:list" in result
