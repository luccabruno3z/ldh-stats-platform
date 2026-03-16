"""Async HTTP client with TTL-based in-memory cache."""

import time
import aiohttp

from bot.config import all_players_url, json_url, clan_averages_url


class DataFetcher:
    """Cached async HTTP client for fetching JSON data from GitHub Pages.

    Attributes:
        ttl: Cache time-to-live in seconds (default 300).
        timeout: Per-request timeout in seconds (default 10).
    """

    def __init__(self, ttl: int = 300, timeout: int = 10):
        self.ttl = ttl
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self._cache: dict[str, tuple[float, object]] = {}
        self._session: aiohttp.ClientSession | None = None

    # ── Session lifecycle ─────────────────────────────────────────────────

    async def _get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(timeout=self.timeout)
        return self._session

    async def get_session(self) -> aiohttp.ClientSession:
        """Public access to the underlying aiohttp session."""
        return await self._get_session()

    async def close(self) -> None:
        """Close the underlying aiohttp session."""
        if self._session and not self._session.closed:
            await self._session.close()

    # ── Core fetch ────────────────────────────────────────────────────────

    async def fetch_json(self, url: str):
        """Fetch JSON from *url*, returning cached data when fresh."""
        now = time.monotonic()
        cached = self._cache.get(url)
        if cached is not None:
            ts, data = cached
            if now - ts < self.ttl:
                return data

        session = await self._get_session()
        async with session.get(url) as resp:
            resp.raise_for_status()
            data = await resp.json(content_type=None)

        self._cache[url] = (now, data)
        return data

    # ── Convenience methods ───────────────────────────────────────────────

    async def fetch_all_players(self):
        """Fetch the all-players cluster JSON."""
        return await self.fetch_json(all_players_url())

    async def fetch_clan_players(self, clan: str):
        """Fetch the players JSON for a specific clan."""
        return await self.fetch_json(json_url(clan))

    async def fetch_clan_averages(self):
        """Fetch the clan averages JSON."""
        return await self.fetch_json(clan_averages_url())
