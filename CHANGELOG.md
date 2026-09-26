# Changelog

All notable changes to this project are documented here. The format is
[Keep a Changelog](https://keepachangelog.com/), versions follow
[SemVer](https://semver.org/). `scripts/release.py` moves the Unreleased
section under a new version heading — add entries here as you go, don't
write them at release time.

## [Unreleased]

## [0.3.0] - 2026-09-26

### Added

- Moved onto the cli-generator template (v1.0.0): `--json` on every command,
  structured errors with fixed exit codes, `doctor`, `init`/`status`/`config`,
  bundled agent skill (`--ai`, `skill install`), CI with coverage floor and
  dependency audit.
- `convert INPUT [-o OUTPUT]` command wrapping the existing converter
  (output unchanged byte-for-byte).
- Nothing is dropped silently any more: wrappers (`div`, `section`,
  `article`, `main`, `header`, `footer`, `aside`, `html`, `body`) are
  unwrapped; loose text and inline tags become paragraphs; tags without a
  native block are kept as `wp:html`; `script`/`style`/`head` are dropped.
  Both cases are reported: `HtmlToGutenberg().convert_report()` →
  `Conversion(blocks, warnings)`, `logging` warnings, and `"warnings"` in
  `convert --json`.
- Native blocks: `hr` → separator, `pre`/`pre>code` → preformatted/code,
  `figure` (img or table + figcaption) → image/table with caption,
  `details` → details, `video`/`audio` → video/audio.

### Changed

- Renamed: package `rb_html_gutenberg` → `html_to_gutenberg` (import
  `from html_to_gutenberg import HtmlToGutenberg`), command
  `rb-html-gutenberg FILE` → `html-to-gutenberg convert FILE`.

- Adjacent top-level inline tags (`<strong>a</strong><em>b</em>`) now form
  one paragraph instead of one paragraph each; a lone one is unchanged.

### Removed

- MCP server (`mcp_server.py`, `.mcp.json`, the `mcp` extra); the CLI with
  `--json` replaces it for agents.
