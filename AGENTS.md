# AGENTS.md

Guidance for coding agents working on the **html_to_gutenberg** package
itself (not its end users — see `src/html_to_gutenberg/data/SKILL.md` for
that).

## Development

```bash
uv sync                          # also writes uv.lock — commit it (CI runs `uv lock --check`)
uv run html_to_gutenberg --help
uv run ruff check . && uv run ruff format --check . && uv run ty check && uv run pytest
```

Before calling anything done, that last line must pass — it's exactly
what CI runs on Linux/macOS/Windows, followed by `uv tool install .` to
prove the package still installs as a tool.

Run `scripts/install_hooks.sh` once (`.git/hooks/` isn't versioned by git,
so this is also needed again after a fresh clone). It installs a
pre-commit hook that warns — never blocks — when a command's logic changed
without its docstring changing too, since that docstring is the `--help`
text agents read as this CLI's API contract.

## Architecture (do not violate)

- `commands/` — argument parsing only. No business logic here.
- `core/` — services, models, errors. All real logic lives here.
- `providers/` — external API/integration implementations. HTTP services
  subclass `providers.HttpProvider` (retries, timeouts and the mapping of
  401/429/5xx/network errors onto `AuthRequired`/`ProviderError` are done
  there once); never call `httpx` directly from `core/` or `commands/`.
- `credentials/` — secrets via OS keychain + env vars. Never write a secret
  to `.html_to_gutenberg/config.toml` or any other project-local file.
- `output/` — every command supports both human and `--json` output via
  `output.emit_success` / `output.guard`. Don't `print()` directly in a
  command. stdout is data only; errors, `--verbose` progress and `logging`
  go to stderr.
- Command groups are created with `output.group("...")`, not
  `typer.Typer(...)` — that's what makes `html_to_gutenberg <group>` with
  no subcommand print help (exit 0) instead of a usage error.
- Errors are `CliError` subclasses with a stable `code` and the fixed
  exit-code table (see `core/errors.py`). Don't raise bare exceptions as the
  intended user-facing failure path.
- Any new command that changes external state irreversibly (deletes,
  overwrites a remote resource, restarts something, ...) must support
  `--dry-run` (`output.is_dry_run`) and gate the actual action behind
  `output.require_confirmation`. Commands that only touch local project
  files (`init`, `config set`) don't need this.

## Releasing

Never edit `version =` in `pyproject.toml` by hand. Add a line under
`## [Unreleased]` in `CHANGELOG.md` with each change, and when it should
ship run `uv run scripts/release.py patch|minor|major` from a clean
`main` — it bumps the version, dates the changelog, commits, tags
`v<version>` and pushes. Projects pin the CLI they need via
`[cli] min_version` in their config, so a change a project depends on
needs a release before that project can require it.

## After changing the command surface

Nothing to update by hand: agents discover commands from a bare
`html_to_gutenberg` / `--help`, which is rendered from the command
docstrings — so the docstring *is* the API doc, keep it accurate (the
pre-commit hook warns when it drifts). `src/html_to_gutenberg/data/SKILL.md`
deliberately lists no commands, only conventions; touch it only if a
convention changes (a new exit code, a new credential rule).
