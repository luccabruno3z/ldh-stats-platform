"""Tips cog -- tips command loading from bot/data/tips.json."""

import json
import os
import random

import discord
from discord.ext import commands

from bot.config import BOT_THUMBNAIL

# Path to the tips JSON file (relative to the repo root)
_TIPS_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "tips.json")


class Tips(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self._tips: dict = {}
        self._load_tips()

    def _load_tips(self):
        path = os.path.normpath(_TIPS_FILE)
        with open(path, "r", encoding="utf-8") as f:
            self._tips = json.load(f)

    @commands.command()
    async def tips(self, ctx: commands.Context, *, kit: str = None):
        """Proporciona consejos aleatorios según el kit seleccionado."""
        general = self._tips.get("general", [])
        kits = self._tips.get("kits", {})

        if kit is None:
            consejos = random.sample(general, k=min(5, len(general)))
            embed = discord.Embed(
                title="Consejos Generales Aleatorios",
                description="\n".join(f"- {c}" for c in consejos),
                color=discord.Color.blue(),
            )
        else:
            kit_lower = kit.lower()
            if kit_lower in kits:
                kit_tips = kits[kit_lower]
                consejos = random.sample(kit_tips, k=min(5, len(kit_tips)))
                embed = discord.Embed(
                    title=f"Consejos Aleatorios para {kit.capitalize()}",
                    description="\n".join(f"- {c}" for c in consejos),
                    color=discord.Color.green(),
                )
            else:
                embed = discord.Embed(
                    title="Kit no reconocido",
                    description=(
                        "Por favor, elige uno de los siguientes kits:\n"
                        "`rifleman`, `medic`, `automatic rifleman`, `grenadier`, "
                        "`sniper`, `lat`, `hat`, `combat engineer`."
                    ),
                    color=discord.Color.red(),
                )

        embed.set_footer(text="¡Practica y mejora tus habilidades en el campo de batalla!")
        embed.set_thumbnail(url=BOT_THUMBNAIL)
        await ctx.send(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(Tips(bot))
