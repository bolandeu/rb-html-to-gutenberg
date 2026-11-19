# html-to-gutenberg

Конвертация HTML в WordPress Gutenberg блоки — Python-библиотека и CLI

## Usage

**CLI** (for humans and agents; `html-to-gutenberg` and `html_to_gutenberg` are the same command):

```bash
html-to-gutenberg convert page.html              # markup to stdout
html-to-gutenberg convert page.html -o out.html  # write to a file
html-to-gutenberg convert page.html --json       # {"ok": true, "blocks": "...", "output": null}
```

Wrappers like `div`/`section` are unwrapped, tags without a native block
are kept as Custom HTML (`wp:html`), `script`/`style`/`head` are dropped —
each such case is a warning (stderr; `"warnings"` under `--json`), so
nothing disappears silently. `html-to-gutenberg convert --help` lists the
native blocks.

**Python library:**

```python
from html_to_gutenberg import HtmlToGutenberg

blocks = HtmlToGutenberg().convert("<h2>Title</h2><p>Text</p>")
report = HtmlToGutenberg().convert_report(html)  # report.blocks, report.warnings
```

In another uv project, depend on it editable (edits here are picked up
immediately) or from Gitea:

```bash
uv add --editable /Users/bolandau/Work/tools/rb-html-to-gutenberg
uv add "rb-html-to-gutenberg @ git+https://homeserver.tailee01ab.ts.net:3000/bolandeu/html-to-gutenberg.git@vX.Y.Z"
```

The distribution is `rb-html-to-gutenberg` (standard §10); the import package
(`html_to_gutenberg`) and the command (`html-to-gutenberg`) keep their names.
Pin a tag (`@vX.Y.Z`) rather than a branch.

## Development

```bash
uv sync
uv run html-to-gutenberg --help
uv run pytest --snapshot-update  # after changing a command's help; review tests/snapshots/help/
```

The gate is `gate check`, run on this machine before a commit (`.agents/antagor/antagor.toml`).
the changelog and the release are Antagor's (`antagor board`, `antagor publish`); the version is the git tag
(`vX.Y.Z`), `pyproject.toml` has no `version =`.

## Install

**On this machine, from a local checkout** — editable, so code edits take
effect in the global command without reinstalling:

```bash
uv tool install --editable .
```

**From the Gitea registry** (the package is released there):

```bash
uv tool uninstall html_to_gutenberg   # once: the old distribution name (before v0.4.0)
uv tool install rb-html-to-gutenberg --index https://homeserver.tailee01ab.ts.net:3000/api/packages/bolandeu/pypi/simple
```

**From the git tag** (any machine, any OS):

```bash
uv tool install "rb-html-to-gutenberg @ git+https://homeserver.tailee01ab.ts.net:3000/bolandeu/html-to-gutenberg.git@vX.Y.Z"
```

`vX.Y.Z` is a release tag cut by `antagor publish`. Uninstall the old
`html_to_gutenberg` tool first, otherwise two tools fight over the same command. This is also how an AI agent
bootstraps this CLI on a fresh machine/sandbox where it isn't installed
yet — see `src/html_to_gutenberg/data/SKILL.md`.

**Update** an installed copy to the latest commit:

```bash
uv tool upgrade rb-html-to-gutenberg
```

After install, the command `html_to_gutenberg` is available globally, on
macOS, Linux and Windows alike (see `architecture.md` in the cli-generator
plugin for why: no shelling out, no hardcoded POSIX paths).

To pick up later template changes, see `existing-package.md` in the `cli-generator` plugin (`copier update`).

## Architecture

This project follows a fixed CLI architecture:

- `src/html_to_gutenberg/commands/` — argument parsing only, no business logic.
- `src/html_to_gutenberg/core/` — services, models, errors: the real logic.
- `src/html_to_gutenberg/providers/` — external APIs/integrations.
- `src/html_to_gutenberg/credentials/` — secrets via the OS keychain (`keyring`)
  and environment variables. Secrets never live in `.html_to_gutenberg/config.toml`.
- `src/html_to_gutenberg/output/` — human (`rich`) and `--json` rendering.

Run `html_to_gutenberg doctor` to check environment/config/auth readiness, and
`html_to_gutenberg --help` for the full command surface. Every command supports
`--json` for machine/agent consumption; errors are structured (`error.code`,
fixed exit codes, `error.action` telling you what to do next) and go to
stderr in human mode, so stdout is always safe to pipe.

A project can require a minimum CLI version in its `.html_to_gutenberg/config.toml`
(`[cli] min_version = "..."`); an older install refuses with exit 6 and
`uv tool upgrade rb-html-to-gutenberg` fixes it.

See `src/html_to_gutenberg/data/SKILL.md` for the agent-facing usage guide
bundled with this package — install it into an AI tool with
`html_to_gutenberg skill install`, or get it as plain text with
`html_to_gutenberg --ai` (works even without file access).
