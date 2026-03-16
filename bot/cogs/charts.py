"""Charts cog -- grafico, historial, and backward-compatible aliases."""

import os
import re
import json

import discord
from discord.ext import commands

from bot.config import (
    graph_url,
    all_players_graph_url,
    GRAPH_ALIASES,
    CLAN_NAMES,
)
from bot.services.chart_renderer import render_history_chart


def _safe_filename(filename: str) -> str:
    """Return a filesystem-safe version of *filename*."""
    return re.sub(r"[^a-zA-Z0-9_\-]", "_", filename)


class Charts(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        # Register backward-compatible aliases as commands
        for alias, clan in GRAPH_ALIASES.items():
            self._register_alias(alias, clan)

    # ── Dynamic alias registration ────────────────────────────────────────

    def _register_alias(self, alias: str, clan: str):
        """Create a command with *alias* that sends the graph link for *clan*."""

        async def _alias_callback(ctx: commands.Context):
            url = graph_url(clan)
            await ctx.send(
                f"[Aquí tienes el gráfico interactivo de {clan}!]({url})"
            )

        # Build a proper Command and attach it to the bot
        cmd = commands.Command(
            _alias_callback,
            name=alias,
            help=f"Gráfico interactivo de {clan}.",
        )
        cmd._buckets = commands.CooldownMapping.from_cooldown(
            1, 10, commands.BucketType.user,
        )
        cmd.cog = self
        self.bot.add_command(cmd)

    # ── -grafico <clan|all|todos> ─────────────────────────────────────────

    @commands.command(name="grafico")
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def grafico(self, ctx: commands.Context, clan: str = None):
        """Muestra el gráfico interactivo de un clan o de todos los jugadores."""
        if clan is None or clan.lower() in ("all", "todos"):
            url = all_players_graph_url()
            await ctx.send(
                f"[Aquí tienes el gráfico interactivo de los usuarios!]({url})"
            )
            return

        # Normalize: accept lowercase input
        clan_upper = clan.upper()
        if clan_upper not in CLAN_NAMES:
            valid = ", ".join(CLAN_NAMES)
            await ctx.send(
                f"❗ Clan '{clan}' no reconocido. Clanes válidos: {valid}, `all`/`todos`."
            )
            return

        url = graph_url(clan_upper)
        await ctx.send(
            f"[Aquí tienes el gráfico interactivo de {clan_upper}!]({url})"
        )

    # ── -historial <jugador> ──────────────────────────────────────────────

    @commands.command()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def historial(self, ctx: commands.Context, jugador: str = None):
        """Muestra un gráfico histórico del Performance Score de un jugador."""
        if not jugador:
            await ctx.send(
                "❗ Por favor, proporciona un nombre de jugador. "
                "Ejemplo: `-historial W4RR10R`."
            )
            return

        try:
            safe_name = _safe_filename(jugador)
            history_file = f"graphs/history/{safe_name}_history.json"

            if not os.path.exists(history_file):
                await ctx.send(
                    f"No se encontró historial de performance para el jugador {jugador}."
                )
                return

            with open(history_file, "r") as f:
                history_data = json.load(f)

            dates = [entry["Date"] for entry in history_data]
            scores = [entry["Performance Score"] for entry in history_data]

            buf = render_history_chart(jugador, dates, scores)
            file = discord.File(buf, filename=f"{safe_name}_history_chart.png")
            await ctx.send(
                f"Aquí tienes el gráfico histórico del Performance Score de {jugador}:",
                file=file,
            )
        except Exception as e:
            await ctx.send("❗ Ocurrió un error inesperado. Intenta de nuevo más tarde.")
            print(f"Error: {e}")


async def setup(bot: commands.Bot):
    await bot.add_cog(Charts(bot))
