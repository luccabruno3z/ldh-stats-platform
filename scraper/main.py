"""Orchestrator entrypoint for the PR Stats scraper.

Usage:
    python -m scraper
    python scraper/main.py
"""

import asyncio
import logging
import os
import sys
from datetime import datetime

import numpy as np
import pandas as pd

# Allow running as `python scraper/main.py` by adjusting sys.path
if __name__ == "__main__" and __package__ is None:
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    __package__ = "scraper"

from .charts import generate_all_players_chart, generate_clan_charts
from .config import CLAN_URLS, OUTPUT_DIR
from .fetcher import fetch_all_clans
from .history import update_history
from .parser import parse_clan_html
from .scoring import calculate_scores

os.environ["OMP_NUM_THREADS"] = "1"

logger = logging.getLogger(__name__)


def setup_logging() -> None:
    """Configure logging for the scraper."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def run() -> None:
    """Main scraper pipeline."""
    setup_logging()
    logger.info("Starting PR Stats scraper...")

    # 1. Fetch all clan pages in parallel
    html_pages = asyncio.run(fetch_all_clans())

    if not html_pages:
        logger.error("No clan data fetched. Aborting.")
        sys.exit(1)

    # 2. Parse HTML for each clan
    all_players = []
    all_warnings = []

    for clan_name, html in html_pages.items():
        players, warnings = parse_clan_html(html, clan_name)
        all_players.extend(players)
        all_warnings.extend(warnings)

    if all_warnings:
        logger.warning("Total parsing warnings: %d", len(all_warnings))

    if not all_players:
        logger.error("No player data parsed. Aborting.")
        sys.exit(1)

    logger.info("Parsed %d total players from %d clans.", len(all_players), len(html_pages))

    # 3. Build DataFrame and clean
    df = pd.DataFrame(all_players).dropna()

    # Replace infinities (safety net — parser already handles division)
    df = df.replace([np.inf, -np.inf], np.nan).dropna()

    # 4. Calculate Performance Scores
    df = calculate_scores(df)

    # 5. Ensure output directories exist
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # 6. Generate JSON outputs (backward compatible)
    # All players JSON
    all_players_path = os.path.join(OUTPUT_DIR, "all_players_clusters.json")
    df.to_json(all_players_path, orient="records", lines=False)
    logger.info("Saved %s", all_players_path)

    # Clan averages JSON
    clan_averages = df.groupby("Clan")[[
        "Total Score",
        "Total Kills",
        "Total Deaths",
        "Rounds",
        "Kills per Round",
        "Score per Round",
        "Performance Score",
        "K/D Ratio",
    ]].mean().reset_index()

    averages_path = os.path.join(OUTPUT_DIR, "clan_averages.json")
    clan_averages.to_json(averages_path, orient="records", lines=False)
    logger.info("Saved %s", averages_path)

    # Per-clan JSONs with "Last Updated" field
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    for clan_name in CLAN_URLS:
        df_clan = df[df["Clan"] == clan_name]
        if df_clan.empty:
            logger.warning("No data for clan %s — skipping JSON.", clan_name)
            continue

        df_clan = df_clan.copy()
        df_clan["Last Updated"] = timestamp
        clan_path = os.path.join(OUTPUT_DIR, f"{clan_name}_players.json")
        df_clan.to_json(clan_path, orient="records", lines=False)
        logger.info("Saved %s", clan_path)

    # 7. Generate charts
    logger.info("Generating charts...")
    generate_all_players_chart(df)
    generate_clan_charts(df)

    # 8. Update player history
    logger.info("Updating player history...")
    update_history(df)

    logger.info("Scraper completed successfully.")


if __name__ == "__main__":
    run()
