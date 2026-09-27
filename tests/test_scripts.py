"""The repo's own tooling scripts: the parts of their logic that decide what the gate demands."""

from __future__ import annotations

import importlib.util
from pathlib import Path
from types import ModuleType

import pytest

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"


def _load(name: str) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / f"{name}.py")
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


release = _load("release")
hook = _load("check_changelog_fragment")


@pytest.mark.parametrize(
    "path",
    [
        "uv.lock",
        ".github/workflows/ci.yml",
        "scripts/release.py",
        "tests/test_cli.py",
        ".githooks/pre-commit",
        ".claude/settings.json",
        "AGENTS.md",
        "CLAUDE.md",
    ],
)
def test_tooling_changes_need_no_fragment(path: str) -> None:
    assert not release.needs_fragment(path)


@pytest.mark.parametrize("path", ["src/pkg/cli.py", "pyproject.toml", "README.md", "scripts.py", "testsuite/x.py"])
def test_package_changes_need_a_fragment(path: str) -> None:
    assert release.needs_fragment(path)


def test_gate_and_pre_commit_hook_agree() -> None:
    assert release.NO_FRAGMENT_NEEDED == hook.NO_FRAGMENT_NEEDED
