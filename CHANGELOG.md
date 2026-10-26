# Changelog

All notable changes to this project are documented here. Versions follow
[SemVer](https://semver.org/) (while at `0.x`, a minor bump may break).

The changelog is written by `antagor publish`; don't edit it by hand.

## v0.5.1 — 2026-10-26

### Main

- Merge pull request #1: template v1.27.3 (Renovate)
- chore(template): Update dependency https://homeserver.tailee01ab.ts.net:3000/bolandeu/cli-generator.git to v1.27.3


## v0.5.0 — 2026-10-23

### Main

- antagor init: project html-to-gutenberg (H2G)
- antagor init: project html-to-gutenberg (H2)
- antagor init: project html-to-gutenberg (H2G)
- antagor init: project html-to-gutenberg (H2G)
- Template v1.27.1: update from v1.2.7
- chore: copier source moved to Gitea
- chore: пути ~/Projects → ~/Work после переезда
- chore(hooks): скрипты tools ищутся относительно репозитория (перенос tools не ломает хуки)
- chore(claude): при старте сессии агент берёт имя в herdr по команде
- chore(hooks): pre-push сообщает корневому агенту tools о пушнутых тегах
- docs: инструмент в системе (стандарт §13)
- docs: каждое заметное изменение выходит релизом


## [0.4.1] - 2026-09-27

### Fixed

- `--version` and the command name are also found for an install made under the old distribution name `html_to_gutenberg`; `httpx` is imported only by HTTP providers (cli-generator template v1.2.7).


## [0.4.0] - 2026-09-27

### Changed

- **Breaking:** the distribution is renamed `html_to_gutenberg` → `rb-html-to-gutenberg` (standard §10). The command (`html-to-gutenberg` / `html_to_gutenberg`) and the import package `html_to_gutenberg` are unchanged. Consumers: depend on `rb-html-to-gutenberg @ git+https://github.com/bolandeu/html-to-gutenberg.git@vX.Y.Z` (and rename the `[tool.uv.sources]` key); global tool: `uv tool uninstall html_to_gutenberg` before installing the new name; existing dev venv: `uv sync --reinstall-package rb-html-to-gutenberg`.


## [0.3.2] - 2026-09-27

### Changed

- Template v1.2.4: `auth status` comes from the template; help and `auth status`'s `tool` name the command as `html-to-gutenberg` (the `html_to_gutenberg` alias still works); `config get/set` examples use `cli.min_version`.


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
