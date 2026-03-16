"""Async HTTP fetcher with retries and exponential backoff."""

import asyncio
import logging
from typing import Dict

import aiohttp

from .config import CLAN_URLS, MAX_RETRIES, REQUEST_TIMEOUT

logger = logging.getLogger(__name__)


async def _fetch_one(
    session: aiohttp.ClientSession,
    clan_name: str,
    url: str,
) -> tuple[str, str | None]:
    """Fetch a single clan page with exponential backoff retries.

    Returns (clan_name, html_text) on success or (clan_name, None) on failure.
    """
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            logger.info("Fetching %s (attempt %d/%d): %s", clan_name, attempt, MAX_RETRIES, url)
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=REQUEST_TIMEOUT)) as resp:
                resp.raise_for_status()
                html = await resp.text()
                logger.info("Successfully fetched %s (%d bytes)", clan_name, len(html))
                return clan_name, html
        except Exception as exc:
            wait = 2 ** (attempt - 1)
            logger.warning(
                "Attempt %d/%d failed for %s: %s. Retrying in %ds...",
                attempt,
                MAX_RETRIES,
                clan_name,
                exc,
                wait,
            )
            if attempt < MAX_RETRIES:
                await asyncio.sleep(wait)

    logger.error("All %d attempts failed for clan %s — skipping.", MAX_RETRIES, clan_name)
    return clan_name, None


async def fetch_all_clans(clan_urls: Dict[str, str] | None = None) -> Dict[str, str]:
    """Fetch HTML for all clans in parallel.

    Args:
        clan_urls: Optional override; defaults to config.CLAN_URLS.

    Returns:
        Dict mapping clan_name -> html_text (only successful fetches).
    """
    if clan_urls is None:
        clan_urls = CLAN_URLS

    results: Dict[str, str] = {}

    async with aiohttp.ClientSession() as session:
        tasks = [
            _fetch_one(session, name, url)
            for name, url in clan_urls.items()
        ]
        completed = await asyncio.gather(*tasks)

    for clan_name, html in completed:
        if html is not None:
            results[clan_name] = html
        else:
            logger.warning("No data for clan %s", clan_name)

    logger.info("Fetched %d / %d clans successfully.", len(results), len(clan_urls))
    return results
