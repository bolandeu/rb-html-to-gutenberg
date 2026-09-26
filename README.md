# html-to-gutenberg

Конвертация HTML в WordPress Gutenberg блоки — Python-библиотека и CLI

## Usage

**CLI** (for humans and agents; `html-to-gutenberg` and `html_to_gutenberg` are the same command):

```bash
html-to-gutenberg convert page.html              # markup to stdout
html-to-gutenberg convert page.html -o out.html  # write to a file
html-to-gutenberg convert page.html --json       # {"ok": true, "blocks": "...", "output": null}
```

**Python library:**

```python
from html_to_gutenberg import HtmlToGutenberg

blocks = HtmlToGutenberg().convert("<h2>Title</h2><p>Text</p>")
```

In another uv project, depend on it editable (edits here are picked up
immediately) or from GitHub:

```bash
uv add --editable /Users/bolandau/Projects/tools/html-to-gutenberg
uv add "git+https://github.com/bolandeu/html-to-gutenberg.git"
```

## Development

```bash
uv sync
uv run html_to_gutenberg --help
uv run ruff check . && uv run ruff format --check . && uv run ty check && uv run pytest
scripts/install_hooks.sh  # installs a pre-commit hook warning on stale --help docstrings
```

`pytest` fails below the coverage floor in `pyproject.toml`; `ruff` includes
the security (`S`) rules; CI additionally scans `uv.lock` for known
vulnerabilities (OSV-Scanner) — the same as `osv-scanner --lockfile=uv.lock`
locally.

## Release

```bash
uv run scripts/release.py patch   # or minor / major
```

Bumps the version in `pyproject.toml`, dates the `## [Unreleased]` section
of `CHANGELOG.md`, commits, tags `v<version>` and pushes. Keep the changelog
current as you work; the release script only stamps it.

## Install

**On this machine, from a local checkout** — editable, so code edits take
effect in the global command without reinstalling:

```bash
uv tool install --editable .
```

**On any other machine (any OS), once this repo is pushed to GitHub — no
PyPI publish needed:**

```bash
uv tool install "git+https://github.com/bolandeu/html-to-gutenberg.git"
```

Pin a release by appending `@v<version>` (a tag cut by `scripts/release.py`)
to the URL, or a branch/commit the same way. This is also how an AI agent
bootstraps this CLI on a fresh machine/sandbox where it isn't installed
yet — see `src/html_to_gutenberg/data/SKILL.md`.

**Private repo?** The command above is unchanged — `uv` runs git under the
hood, so it authenticates the same way `git clone` does. On a machine
where the install is refused with an auth error, do one of these once:

```bash
gh auth login          # interactive login also sets up git's credential helper
gh auth setup-git      # only needed if gh was logged in with --with-token / in CI
```

or use the SSH form instead of HTTPS:

```bash
uv tool install "git+ssh://git@github.com/bolandeu/html-to-gutenberg.git"
```

**Update** an installed copy to the latest commit:

```bash
uv tool upgrade html_to_gutenberg
```

After install, the command `html_to_gutenberg` is available globally, on
macOS, Linux and Windows alike (see `architecture.md` in the cli-generator
plugin for why: no shelling out, no hardcoded POSIX paths).

To pick up later architecture changes from the `cli-generator` template
itself, run `copier update` in this repo (requires this repo and the
template to both be git repos; see the `cli-generator` plugin's README).

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
`uv tool upgrade html_to_gutenberg` fixes it.

See `src/html_to_gutenberg/data/SKILL.md` for the agent-facing usage guide
bundled with this package — install it into an AI tool with
`html_to_gutenberg skill install`, or get it as plain text with
`html_to_gutenberg --ai` (works even without file access).
