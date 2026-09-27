---
name: html-to-gutenberg
description: Conventions for driving the html-to-gutenberg CLI from an agent — install, JSON output, exit codes, credentials, destructive-command gating. Invoke when a task involves this project's operations.
---

# html-to-gutenberg

Everything command-specific is in the CLI itself — run `html-to-gutenberg`
with no arguments for version + command list, `html-to-gutenberg <command>
--help` for details. This document only covers what `--help` can't tell
you. If you can run the CLI but not read files, `html-to-gutenberg --ai`
prints this document.

## Install (if `html-to-gutenberg --version` fails)

```bash
uv tool install "git+https://github.com/bolandeu/html-to-gutenberg.git"
```

Same command on macOS, Linux and Windows; `uv tool upgrade html_to_gutenberg`
updates it. Do not run from source unless asked to develop the CLI.

The repository may be private. On an auth error (`Authentication failed`,
`could not read Username`, `Repository not found`) do not ask for a token:
run `gh auth status`; if it passes, `gh auth setup-git` and retry; if not,
ask the user to run `gh auth login`. With SSH keys configured, this works
without any of that:

```bash
uv tool install "git+ssh://git@github.com/bolandeu/html-to-gutenberg.git"
```

## Conventions

- **`--json` on every command.** Parse stdout; never scrape human output.
  stdout is data only, stderr is diagnostics.
- **Project-aware.** Commands find the project by walking up from the
  current directory, or take `--project PATH`. Not initialized →
  `html-to-gutenberg init --non-interactive`.
- **`--non-interactive`** on anything that could prompt. It fails with a
  structured error instead of hanging.
- **Credentials** live in the OS keychain or env vars
  (`HTML_TO_GUTENBERG_<PROVIDER>_<FIELD>`), never in arguments or
  config. `auth status --check --json` reports every provider (source,
  status, expiry, quota — never values; exit 3 if a required one isn't
  ok); log in with `auth login`; never ask the user to paste a secret into
  a command line.
- **Destructive commands** are the ones whose `--help` shows `--dry-run`
  and `--confirm`. Always: run with `--dry-run`, show the user, get
  explicit sign-off, then `--confirm --non-interactive`. Never chain
  straight to `--confirm` without a human having seen the dry-run.
- **`doctor --json`** first when something looks off — it reports
  project, config, version compatibility and credential readiness.

## Errors

Error envelope: `{"ok": false, "error": {"code", "message", "action"}}`.
Read exit code → `error.code` → `error.action` (the concrete next command).

    0  ok
    1  general (UNEXPECTED = a bug: re-run with --verbose, report; ABORTED = user said no)
    2  invalid arguments
    3  auth required          → html-to-gutenberg auth login
    4  project not initialized → html-to-gutenberg init
    5  provider error (network / external service; already retried) → retry later
    6  CLI too old for this project → uv tool upgrade html_to_gutenberg

Only exit 5 is worth an automatic retry.
