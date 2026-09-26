from __future__ import annotations

import tomllib
from pathlib import Path

import tomli_w
from packaging.version import Version

from .converter import Conversion, HtmlToGutenberg
from .errors import CliTooOld, InvalidArguments, ProjectNotInitialized
from .models import ProjectConfig
from .version import installed_version

# Derived at import time from this package's own name, so this module never
# needs template substitution: it just works under whatever package_name
# the project was generated with.
_PACKAGE_NAME = __name__.split(".")[0]
PROJECT_DIR_NAME = f".{_PACKAGE_NAME}"
CONFIG_FILE_NAME = "config.toml"


def find_project_root(start: Path) -> Path | None:
    current = start.resolve()
    for candidate in (current, *current.parents):
        if (candidate / PROJECT_DIR_NAME).is_dir():
            return candidate
    return None


def require_project_root(start: Path) -> Path:
    root = find_project_root(start)
    if root is None:
        raise ProjectNotInitialized(str(start))
    return root


def config_path(project_root: Path) -> Path:
    return project_root / PROJECT_DIR_NAME / CONFIG_FILE_NAME


def check_cli_compat(config: ProjectConfig) -> None:
    """Raise CliTooOld if this installed CLI is older than the project's `cli.min_version`.

    A project outlives any single CLI release; this is how it refuses to be
    driven by a CLI that predates a config field or command it relies on.
    Skipped for an uninstalled (bare source) run, which has no version.
    """
    installed = installed_version()
    if installed is None:
        return
    if Version(installed) < Version(config.cli.min_version):
        raise CliTooOld(installed, config.cli.min_version)


def load_config(project_root: Path, *, check_compat: bool = True) -> ProjectConfig:
    """Load and validate the project config, enforcing `cli.min_version` by default.

    Only `doctor` passes `check_compat=False` — it reports the mismatch as
    one of its checks instead of failing on it.
    """
    data = tomllib.loads(config_path(project_root).read_text())
    config = ProjectConfig.model_validate(data)
    if check_compat:
        check_cli_compat(config)
    return config


def save_config(project_root: Path, config: ProjectConfig) -> None:
    path = config_path(project_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(tomli_w.dumps(config.model_dump()))


def init_project(project_root: Path, name: str) -> ProjectConfig:
    config = ProjectConfig(name=name)
    save_config(project_root, config)
    return config


def convert_file(input_path: Path, output_path: Path | None = None) -> Conversion:
    """Convert an HTML file to Gutenberg block markup; also write it to `output_path` if given."""
    if not input_path.is_file():
        raise InvalidArguments(f"Input file '{input_path}' does not exist.")
    conversion = HtmlToGutenberg().convert_report(input_path.read_text(encoding="utf-8"))
    if output_path is not None:
        output_path.write_text(conversion.blocks, encoding="utf-8")
    return conversion
