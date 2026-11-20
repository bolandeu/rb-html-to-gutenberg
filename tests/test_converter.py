"""Тесты для HtmlToGutenberg."""

from rb_html_to_gutenberg import HtmlToGutenberg


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


# --- nothing is dropped silently -------------------------------------------------


def convert(html: str) -> str:
    return HtmlToGutenberg().convert(html)


def test_article_wrapped_in_div_is_unwrapped():
    result = convert("<div class='post'><section><h2>T</h2><p>Body</p></section></div>")
    assert '<!-- wp:heading {"level":2} -->\n<h2>T</h2>' in result
    assert "<p>Body</p>" in result
    assert "wp:html" not in result


def test_full_document_body_is_converted_and_head_dropped_with_warning():
    report = HtmlToGutenberg().convert_report(
        "<!DOCTYPE html><html><head><title>X</title></head><body><p>Hi</p></body></html>"
    )
    assert report.blocks == "<!-- wp:paragraph -->\n<p>Hi</p>\n<!-- /wp:paragraph -->"
    assert any("<head>" in w for w in report.warnings)


def test_loose_text_and_inline_tags_become_one_paragraph():
    result = convert("<div>Intro <a href='#'>link</a> &amp; <span>more</span><p>Next</p></div>")
    assert '<p>Intro <a href="#">link</a> &amp; <span>more</span></p>' in result
    assert result.count("<!-- wp:paragraph -->") == 2


def test_lone_top_level_strong_keeps_old_output():
    assert convert("<strong>S</strong>") == "<!-- wp:paragraph -->\n<p><strong>S</strong></p>\n<!-- /wp:paragraph -->"


def test_hr_becomes_separator():
    assert convert("<hr/>") == (
        '<!-- wp:separator -->\n<hr class="wp-block-separator has-alpha-channel-opacity"/>\n<!-- /wp:separator -->'
    )


def test_pre_code_becomes_code_block_and_plain_pre_preformatted():
    assert convert("<pre><code>a &lt; b\n  c</code></pre>") == (
        '<!-- wp:code -->\n<pre class="wp-block-code"><code>a &lt; b\n  c</code></pre>\n<!-- /wp:code -->'
    )
    assert convert("<pre>x\n y</pre>") == (
        '<!-- wp:preformatted -->\n<pre class="wp-block-preformatted">x\n y</pre>\n<!-- /wp:preformatted -->'
    )


def test_figure_with_image_and_caption_becomes_image_block():
    result = convert('<figure><img src="a.jpg" alt="A"/><figcaption>Cap</figcaption></figure>')
    assert result.startswith("<!-- wp:image")
    assert '<img src="a.jpg" alt="A"/><figcaption class="wp-element-caption">Cap</figcaption></figure>' in result


def test_figure_with_table_keeps_caption():
    result = convert("<figure><table><tr><td>1</td></tr></table><figcaption>T</figcaption></figure>")
    assert result.startswith("<!-- wp:table -->")
    assert '<figcaption class="wp-element-caption">T</figcaption></figure>' in result


def test_details_becomes_details_block_with_inner_blocks():
    result = convert("<details><summary>More</summary><p>Hidden</p></details>")
    assert result == (
        '<!-- wp:details -->\n<details class="wp-block-details"><summary>More</summary>'
        "<!-- wp:paragraph -->\n<p>Hidden</p>\n<!-- /wp:paragraph --></details>\n<!-- /wp:details -->"
    )


def test_video_and_audio_blocks():
    assert '<figure class="wp-block-video"><video controls src="v.mp4"></video></figure>' in convert(
        '<video><source src="v.mp4"></video>'
    )
    assert '<figure class="wp-block-audio"><audio controls src="a.mp3"></audio></figure>' in convert(
        '<audio src="a.mp3"></audio>'
    )


def test_unsupported_tag_is_kept_as_custom_html_with_warning():
    report = HtmlToGutenberg().convert_report('<iframe src="https://x.test/e"></iframe>')
    assert report.blocks == '<!-- wp:html -->\n<iframe src="https://x.test/e"></iframe>\n<!-- /wp:html -->'
    assert any("<iframe>" in w for w in report.warnings)


def test_script_is_dropped_with_warning():
    report = HtmlToGutenberg().convert_report("<p>A</p><script>x()</script>")
    assert "x()" not in report.blocks
    assert any("<script>" in w for w in report.warnings)
