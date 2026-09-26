# Changelog

All notable changes to this project are documented here. The format is
[Keep a Changelog](https://keepachangelog.com/), versions follow
[SemVer](https://semver.org/). `scripts/release.py` moves the Unreleased
section under a new version heading — add entries here as you go, don't
write them at release time.

## [Unreleased]

### Added

- Moved onto the cli-generator template (v1.0.0): `--json` on every command,
  structured errors with fixed exit codes, `doctor`, `init`/`status`/`config`,
  bundled agent skill (`--ai`, `skill install`), CI with coverage floor and
  dependency audit.
- `convert INPUT [-o OUTPUT]` command wrapping the existing converter
  (output unchanged byte-for-byte).

### Changed

- Renamed: package `rb_html_gutenberg` → `html_to_gutenberg` (import
  `from html_to_gutenberg import HtmlToGutenberg`), command
  `rb-html-gutenberg FILE` → `html-to-gutenberg convert FILE`.

### Removed

- MCP server (`mcp_server.py`, `.mcp.json`, the `mcp` extra); the CLI with
  `--json` replaces it for agents.
