# Changelog

All notable changes to this project are documented here. Versions follow
[SemVer](https://semver.org/) (while at `0.x`, a minor bump may break).

Don't edit this file between releases: each change adds a fragment to
`changelog.d/` (`uv run towncrier create +<slug>.<type>.md -c "..."`, type
one of added/changed/deprecated/removed/fixed/security), and
`scripts/release.py` assembles them into a new section below the marker.

<!-- towncrier release notes start -->

## [0.3.1] - 2026-09-27

### Added

- `auth status [--check] [--provider NAME] --json`: the cross-tool credentials report; this tool has no credentials, so the list is empty and it exits 0.

### Changed

- Adopted the tools release standard (template v1.2.0): version comes from the git tag, changelog from changelog.d/ fragments, one `scripts/release.py` gate; `--help` of every command is covered by a contract test and snapshots.


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
