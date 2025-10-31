"""
HTTP helpers used by Streamlit components to fetch backend data efficiently.

This module centralises the HTTP logic so that we can add caching and timeout
policies in a single location. All responses are cached via ``st.cache_data`` in
order to reduce the number of calls to the FastAPI backend and keep the frontend
snappy, which is particularly important when the dashboard is hosted on resource
constrained environments.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Mapping, Optional, Sequence, Tuple, cast

import requests
import streamlit as st

from ..domain import BASE_URL

DEFAULT_TIMEOUT = 10.0
DEFAULT_TTL = 60
CacheDecorator = Callable[[Callable[..., Any]], Callable[..., Any]]


@dataclass(frozen=True)
class BackendAPIError(RuntimeError):
    """Custom exception raised when the backend returns an error."""

    endpoint: str
    details: str

    def __str__(self) -> str:  # pragma: no cover - trivial repr
        return f"{self.endpoint}: {self.details}"


def _make_params_tuple(params: Mapping[str, Any]) -> Tuple[Tuple[str, str], ...]:
    """Normalise query parameters for caching."""
    processed: Sequence[Tuple[str, str]] = [
        (str(key), str(value))
        for key, value in sorted(params.items(), key=lambda item: item[0])
    ]
    return tuple(processed)


def fetch_backend_json(
    path: str,
    params: Optional[Mapping[str, Any]] = None,
    ttl: int = DEFAULT_TTL,
    timeout: float = DEFAULT_TIMEOUT,
) -> Any:
    """Fetch a JSON payload from the backend with caching and error handling.

    Args:
        path: Endpoint path located under ``/mange_ta_main`` (leading slash optional).
        params: Optional query parameters.
        ttl: Cache duration (in seconds) for ``st.cache_data``.
        timeout: HTTP timeout in seconds.

    Returns:
        The JSON payload decoded into Python objects (list/dict).

    Raises:
        BackendAPIError: If the request fails or returns a non-2xx status code.
    """

    normalised_params = params or {}
    params_items = _make_params_tuple(normalised_params)
    url = f"{BASE_URL}/mange_ta_main/{path.lstrip('/')}"

    def _request_impl(
        url: str,
        params_items: Tuple[Tuple[str, str], ...],
        timeout: float,
    ) -> Any:
        response = requests.get(url, params=dict(params_items), timeout=timeout)
        response.raise_for_status()
        return response.json()

    _request = _request_impl
    cache_enabled = ttl is not None and ttl > 0
    cache_fn = getattr(st, "cache_data", None) if cache_enabled else None
    if cache_fn is not None and cache_fn.__class__.__module__ != "unittest.mock":
        try:
            decorator = cast(Callable[..., CacheDecorator], cache_fn)
            cached = decorator(show_spinner=False, ttl=ttl, max_entries=16)(
                _request_impl
            )
            cached_module = getattr(cached, "__class__", object).__module__
            if cached_module != "unittest.mock":
                _request = cached
        except Exception:  # pragma: no cover - fallback when cache misbehaves
            _request = _request_impl

    try:
        return _request(url, params_items, timeout)
    except requests.RequestException as exc:
        raise BackendAPIError(endpoint=url, details=str(exc)) from exc
