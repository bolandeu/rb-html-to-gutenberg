"""External integrations (HTTP APIs, LLMs, ...) live here, one module per service.

Subclass `HttpProvider` for anything that speaks HTTP — it already maps
auth failures, rate limits, outages and network errors onto the CLI's
error codes and retries what's safe to retry. Keep API calls out of
`commands/` and `core/services.py`; services call a provider, commands
call a service.

Every concrete provider implements `health_check()` — the hook behind
`<cli> auth status --check` (see `base.Provider`).
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from .base import Health, Provider, Quota, all_providers

if TYPE_CHECKING:
    from .http import HttpProvider

__all__ = ["Health", "HttpProvider", "Provider", "Quota", "all_providers"]


def __getattr__(name: str) -> Any:
    # HttpProvider (and so httpx) is loaded only by code that uses it: a CLI
    # whose providers aren't HTTP can drop the httpx dependency.
    if name == "HttpProvider":
        from .http import HttpProvider

        return HttpProvider
    raise AttributeError(name)
