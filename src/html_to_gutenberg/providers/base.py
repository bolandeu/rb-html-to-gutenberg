from __future__ import annotations

import importlib
import pkgutil
from dataclasses import dataclass
from datetime import datetime
from typing import ClassVar, Literal

# What a provider's own health check can conclude. `missing` and `unchecked`
# are decided by `auth status` before a check ever runs.
HealthStatus = Literal["ok", "invalid", "expired", "quota_exhausted", "unreachable"]


@dataclass(frozen=True)
class Quota:
    remaining: int | None = None
    limit: int | None = None
    unit: str = "requests"


@dataclass(frozen=True)
class Health:
    """Result of `Provider.health_check()`. Never put a credential value in `message`."""

    status: HealthStatus = "ok"
    expires_at: datetime | None = None
    quota: Quota | None = None
    message: str | None = None


class Provider:
    """Base for every external integration, whatever its transport.

    A concrete provider sets `name` and `credential_fields` (the field names
    it reads via `credentials.manager` under `credential_name`; `()` if it
    needs none), `required` and `per_target` where they differ, and must
    implement `health_check()` — `tests/test_providers.py` fails for any
    provider that doesn't. It must be constructible with no arguments:
    `auth status --check` instantiates every provider found in this package.

    Classes that are only bases for others set `abstract = True` in their own
    body; everything else defined under `providers/` is discovered by
    `all_providers()`, so there is no registry to forget to update.
    """

    abstract: ClassVar[bool] = True
    name: ClassVar[str] = "default"
    credential_fields: ClassVar[tuple[str, ...]] = ("api_key",)
    # False for a provider the CLI works without: its missing credential is
    # reported but doesn't fail `auth status` (a wrong one still does).
    required: ClassVar[bool] = True
    # True when the credential is per target (a site, host, account): one
    # stored credential per target, named "<name>:<target>" — e.g.
    # `auth login --provider deploy:example.com`. `auth status` reports each
    # stored target separately and sets `target` before `health_check()`.
    per_target: ClassVar[bool] = False
    target: str | None = None

    @property
    def credential_name(self) -> str:
        """The key to read this provider's credential under in `credentials.manager`."""
        return f"{self.name}:{self.target}" if self.per_target and self.target else self.name

    def health_check(self) -> Health:
        """One cheap, read-only, non-billed call proving the credential works.

        Typically `self.get_json("/me")` (or whatever the API's cheapest
        authenticated read is) then `return Health()`; add `expires_at` for
        anything with a lifetime and `quota` if the API reports it. Just let
        `AuthRequired` / `ProviderError` propagate — `auth status` maps them
        to `invalid` / `unreachable`. Runs with a 10 s timeout and no retries.
        """
        raise NotImplementedError(f"{type(self).__name__} must implement health_check()")


def all_providers() -> list[type[Provider]]:
    """Every concrete Provider subclass defined in this package, sorted by name."""
    package = __name__.rsplit(".", 1)[0]
    for module in pkgutil.iter_modules(importlib.import_module(package).__path__):
        importlib.import_module(f"{package}.{module.name}")
    found: set[type[Provider]] = set()
    pending = list(Provider.__subclasses__())
    while pending:
        cls = pending.pop()
        pending.extend(cls.__subclasses__())
        if cls.__module__.startswith(f"{package}.") and not cls.__dict__.get("abstract", False):
            found.add(cls)
    return sorted(found, key=lambda cls: cls.name)
