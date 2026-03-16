"""Bot entrypoint. Run as `python bot/main.py` or `python -m bot`."""

import asyncio
import os

from dotenv import load_dotenv
import discord
from discord.ext import commands

from bot.config import COMMAND_PREFIX
from bot.services.data_fetcher import DataFetcher

# ── Cogs to load ──────────────────────────────────────────────────────────────
EXTENSIONS = [
    "bot.cogs.stats",
    "bot.cogs.charts",
    "bot.cogs.compare",
    "bot.cogs.tips",
    "bot.cogs.roles",
    "bot.cogs.countdown",
    "bot.cogs.misc",
]


async def main():
    # Load .env if present (local dev)
    if os.path.exists(".env"):
        load_dotenv()

    token = os.getenv("DISCORD_TOKEN")
    if not token:
        raise ValueError("El token del bot no está definido en las variables de entorno")
    print("Token detectado correctamente")

    # Configure intents (NOT all() -- only what we need)
    intents = discord.Intents.default()
    intents.message_content = True
    intents.members = True
    intents.reactions = True

    bot = commands.Bot(command_prefix=COMMAND_PREFIX, intents=intents)

    # Disable the built-in help so our custom -ayuda works without conflict
    bot.remove_command("help")

    # Initialize the shared data fetcher and attach it to the bot
    bot.data_fetcher = DataFetcher(ttl=300, timeout=10)

    # Load all cogs
    for ext in EXTENSIONS:
        await bot.load_extension(ext)
        print(f"  Cog cargado: {ext}")

    # Run the bot; ensure clean shutdown of aiohttp session
    try:
        await bot.start(token)
    finally:
        await bot.data_fetcher.close()


if __name__ == "__main__":
    asyncio.run(main())
