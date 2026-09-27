# AGENTS.md

Guidance for coding agents working on the **html_to_gutenberg** package
itself (not its end users — see `src/html_to_gutenberg/data/SKILL.md` for
that).

## Development

```bash
uv sync                          # also writes uv.lock — commit it
uv run html-to-gutenberg --help
uv run scripts/release.py --check   # the whole gate — run it before every commit
```

**Before every commit, `uv run scripts/release.py --check` must pass.**
It is the authoritative gate (CI, if the repo keeps it, runs exactly this,
and every release runs it too): `uv lock --check`, ruff check + format,
ty, pytest (coverage floor, help contract + snapshots, `auth status`
shape), a changelog fragment for any change since the last tag, and a
wheel build installed into a throwaway venv where `html-to-gutenberg
--version` must match the built version. A failure names the step and
shows its output — fix the cause, never skip the step.

**Renamed distribution (v0.4.0, standard §10):** `[project] name` is
`rb-html-to-gutenberg` (import package and command unchanged). In a dev venv
created before the rename, `uv sync` removes the old dist together with the
shared console script, so `uv run html-to-gutenberg` silently runs another
copy from PATH. Fix once: `uv sync --reinstall-package rb-html-to-gutenberg`.

Run `scripts/install_hooks.sh` once per clone: it points git at the
versioned hooks in `.githooks/` (Claude Code sessions do this themselves
via `.claude/settings.json`). The pre-commit hook **blocks** a commit where
a command's logic changed but its docstring didn't, and warns when `src/`
changed with no changelog fragment on the branch.

## Architecture (do not violate)

- `commands/` — argument parsing only. No business logic here.
- `core/` — services, models, errors. All real logic lives here.
- `providers/` — external API/integration implementations. HTTP services
  subclass `providers.HttpProvider` (retries, timeouts and the mapping of
  401/429/5xx/network errors onto `AuthRequired`/`ProviderError` are done
  there once); never call `httpx` directly from `core/` or `commands/`.
  Every provider sets `name`, `credential_fields`, `required` and
  implements `health_check()` (one cheap, read-only, non-billed call —
  `tests/test_providers.py` fails without it). `auth status --check --json`
  runs those checks; its JSON shape is a cross-tool contract pinned by
  `tests/test_auth.py` — changing it is a breaking change.
- `credentials/` — secrets via OS keychain + env vars. Never write a secret
  to `.html_to_gutenberg/config.toml` or any other project-local file.
- `output/` — every command supports both human and `--json` output via
  `output.emit_success` / `output.guard`. Don't `print()` directly in a
  command. stdout is data only; errors, `--verbose` progress and `logging`
  go to stderr.
- Command groups are created with `output.group("...")`, not
  `typer.Typer(...)` — that's what makes `html-to-gutenberg <group>` with
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

- **Version = git tag.** There is no `version =` in `pyproject.toml`;
  uv-dynamic-versioning reads the latest `vX.Y.Z` tag at build time. Don't
  add one back, don't hard-code a version string anywhere.
- **Changelog = fragments.** Don't edit `CHANGELOG.md`. Every user-visible
  change adds one fragment:
  `uv run towncrier create +<slug>.<type>.md -c "One or two sentences."`
  (type: added/changed/deprecated/removed/fixed/security). CI fails a PR
  without one.
- **Release** from a clean, up-to-date `main`:
  `uv run scripts/release.py patch|minor|major` — gate, towncrier build,
  commit `Release vX.Y.Z`, annotated tag. It prints the push command;
  pushing needs the user's confirmation.
- **SemVer is a promise about the CLI surface.** Removing/renaming/changing
  commands, flags, the `--json` shape, exit or error codes is breaking —
  major, or **minor while at `0.x`**. A new feature with old behaviour
  intact is minor (**patch while at `0.x`**); a fix is patch. Deprecate first
  (warning + a `deprecated` fragment), remove in the next breaking release.
- **Depending on another of our tools**: pin by tag in `[tool.uv.sources]`
  (`{ git = "...", tag = "vX.Y.Z" }`) with a compatible range in
  `dependencies` (`>=0.2,<0.3`) — never `branch = "main"`, never a
  committed `path =`. Bump = new tag + `uv lock --upgrade-package <name>`
  + full gate, one commit.

Projects pin the CLI they need via `[cli] min_version` in their config, so
a change a project depends on needs a release before that project can
require it.

## After changing the command surface

Agents discover commands from a bare `html-to-gutenberg` / `--help`,
rendered from the command docstrings and `help=` strings — so the
docstring *is* the API doc. **Changed a command's behaviour → update its
docstring in the same commit**:

- docstring = one-line summary, optional paragraph, and an
  `Example: {cli} <command> ...` line (`output.guard` turns `{cli}` into
  `html-to-gutenberg`); every `typer.Option`/`Argument` has `help=`;
- then `uv run pytest --snapshot-update` and read the diff in
  `tests/snapshots/help/` — that diff is the user-visible change.

Enforced: Claude Code hooks (`.claude/settings.json`: PostToolUse after
editing a command file, Stop before ending the turn), the pre-commit hook,
and `tests/test_help.py` in the gate. If a hook fires on a refactor that
truly doesn't change behaviour, say so — don't bypass it silently. `src/html_to_gutenberg/data/SKILL.md`
deliberately lists no commands, only conventions; touch it only if a
convention changes (a new exit code, a new credential rule).
