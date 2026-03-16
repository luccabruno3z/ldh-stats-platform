"""Stats cog -- estadisticas, top, buscar_usuario, promedios, promedios_tops."""

import discord
from discord.ext import commands

from bot.config import (
    CLAN_EMOJIS,
    BOT_THUMBNAIL,
    METRIC_KEY_MAP,
    TOP_CATEGORIES,
    all_players_url,
    json_url,
    performance_color,
    BASE_URL,
)
from bot.services.chart_renderer import render_bar_chart


class Stats(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # ── Helper ────────────────────────────────────────────────────────────

    @property
    def fetcher(self):
        return self.bot.data_fetcher

    # ── -estadisticas <jugador> ───────────────────────────────────────────

    @commands.command()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def estadisticas(self, ctx: commands.Context, jugador: str = None):
        if not jugador:
            await ctx.send(
                "❗ Por favor, proporciona un nombre de jugador. "
                "Ejemplo: `-estadisticas W4RR10R`."
            )
            return

        try:
            data = await self.fetcher.fetch_all_players()
        except Exception as e:
            await ctx.send("❌ Error al conectar con la base de datos. Inténtalo más tarde.")
            print(f"Error: {e}")
            return

        # Sort by Performance Score for global ranking
        jugadores_ordenados = sorted(
            data, key=lambda x: x.get("Performance Score", 0), reverse=True
        )

        jugador_encontrado = next(
            (entry for entry in jugadores_ordenados if entry["Player"] == jugador), None
        )
        ranking_global = next(
            (i + 1 for i, entry in enumerate(jugadores_ordenados) if entry["Player"] == jugador),
            "N/A",
        )

        if not jugador_encontrado:
            await ctx.send(f"⚠️ Jugador '{jugador}' no encontrado en la base de datos.")
            return

        # Clan ranking
        jugadores_clan = [
            e for e in jugadores_ordenados
            if e.get("Clan") == jugador_encontrado.get("Clan")
        ]
        ranking_clan = next(
            (i + 1 for i, e in enumerate(jugadores_clan) if e["Player"] == jugador),
            "N/A",
        )

        ps = jugador_encontrado.get("Performance Score", 0)
        color = performance_color(ps)

        clan = jugador_encontrado.get("Clan", "N/A")
        clan_image_url = f"{BASE_URL}/logos/Logo_{clan}.png"

        # Check png availability via a quick HEAD (async)
        try:
            session = await self.fetcher._get_session()
            async with session.head(clan_image_url) as resp:
                if resp.status != 200:
                    clan_image_url = f"{BASE_URL}/logos/Logo_{clan}.gif"
        except Exception:
            pass

        total_deaths = jugador_encontrado.get("Total Deaths", 0)
        rounds_played = jugador_encontrado.get("Rounds", 1)
        deaths_per_round = total_deaths / rounds_played if rounds_played > 0 else 0

        embed = discord.Embed(
            title=f"📊 Estadísticas de {jugador}",
            description=(
                f"**Ranking Global:** #{ranking_global}\n"
                f"**Ranking en el Clan:** #{ranking_clan}"
            ),
            color=color,
        )
        embed.set_thumbnail(url=clan_image_url)

        embed.add_field(
            name="**📊 Datos Totales 📊**",
            value=(
                f"💥 **K/D Ratio**: {jugador_encontrado['K/D Ratio']:.2f}\n\n"
                f"☠️ **Total Kills**: {jugador_encontrado.get('Total Kills', 'N/A')}\n\n"
                f"💀 **Total Muertes**: {total_deaths}\n\n"
                f"🏆 **Total Score**: {jugador_encontrado.get('Total Score', 'N/A')}\n\n"
                f"🎮 **Rounds Jugados**: {jugador_encontrado.get('Rounds', 'N/A')}"
            ),
            inline=True,
        )

        embed.add_field(
            name="**📉 Tasas 📉**",
            value=(
                f"🔫 **Tasa de Kills**: {jugador_encontrado.get('Kills per Round', 'N/A')}\n\n"
                f"📉 **Tasa de Muertes**: {deaths_per_round:.2f}\n\n"
                f"🎯 **Tasa de Score**: {jugador_encontrado['Score per Round']:.2f}"
            ),
            inline=True,
        )

        embed.add_field(
            name="**🌟 Otros 🌟**",
            value=(
                f"🌟 **Performance Score**: {ps:.2f}\n\n"
                f"🎖️ **Clan**: {clan}"
            ),
            inline=True,
        )

        embed.set_footer(text="📅 Datos actualizados recientemente.")
        await ctx.send(embed=embed)

    # ── -top <cantidad> <categoria> <metrica> ─────────────────────────────

    @commands.command()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def top(
        self,
        ctx: commands.Context,
        cantidad: int = 15,
        categoria: str = "general",
        metrica: str = "performance",
    ):
        if categoria.lower() not in TOP_CATEGORIES:
            await ctx.send(
                "❗ **Categoría inválida.** Las categorías válidas son:\n"
                f"`{'`, `'.join(TOP_CATEGORIES.keys())}`."
            )
            return

        if cantidad <= 0:
            await ctx.send("❗ **La cantidad debe ser mayor a 0.**")
            return

        metricas_validas = ["performance", "kd", "kills", "deaths", "rounds"]
        if metrica not in metricas_validas:
            await ctx.send(
                "❗ **Métrica inválida.** Las métricas válidas son:\n"
                "`performance`, `kd`, `kills`, `deaths`, `rounds`."
            )
            return

        clan_name = TOP_CATEGORIES[categoria.lower()]
        try:
            if clan_name is None:
                data = await self.fetcher.fetch_all_players()
            else:
                data = await self.fetcher.fetch_clan_players(clan_name)
        except Exception as e:
            await ctx.send("❌ **Error al conectar con la base de datos.** Inténtalo más tarde.")
            print(f"Error: {e}")
            return

        metric_key = METRIC_KEY_MAP.get(metrica, metrica)

        jugadores_ordenados = sorted(
            data, key=lambda x: x.get(metric_key, 0), reverse=True
        )

        cantidad = min(cantidad, len(jugadores_ordenados))
        top_jugadores = jugadores_ordenados[:cantidad]

        embed = discord.Embed(
            title=f"🏆 **Top {cantidad} Jugadores** ({categoria.upper()} - {metrica})",
            description=(
                f"Clasificación basada en **{metrica}**.\n"
                f"Aquí están los mejores {cantidad} jugadores en esta categoría:"
            ),
            color=discord.Color.orange(),
        )
        embed.set_thumbnail(url=BOT_THUMBNAIL)

        jugadores_lista = ""
        for index, jugador in enumerate(top_jugadores, start=1):
            nombre = jugador.get("Player", "Desconocido")
            valor_metrica = jugador.get(metric_key, 0)
            clan = jugador.get("Clan", "N/A")
            clan_emoji = CLAN_EMOJIS.get(clan, "")
            jugadores_lista += f"**#{index}** - {clan_emoji} {nombre} ({valor_metrica:.2f})\n"

        embed.add_field(
            name="🔝 **Ranking**",
            value=jugadores_lista if jugadores_lista else "No hay jugadores en esta categoría.",
            inline=False,
        )
        embed.set_footer(text="📅 Datos actualizados recientemente.")
        await ctx.send(embed=embed)

    # ── -buscar_usuario <parte_nombre> ────────────────────────────────────

    @commands.command()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def buscar_usuario(self, ctx: commands.Context, *, nombre_parcial: str = None):
        if not nombre_parcial:
            await ctx.send(
                "❗ Por favor, proporciona una parte del nombre de usuario que deseas buscar. "
                "Ejemplo: `-buscar_usuario parte_del_nombre`."
            )
            return

        try:
            data = await self.fetcher.fetch_all_players()
        except Exception as e:
            await ctx.send("❌ Error al conectar con la base de datos. Inténtalo más tarde.")
            print(f"Error: {e}")
            return

        resultados = [
            j for j in data if nombre_parcial.lower() in j["Player"].lower()
        ]

        if not resultados:
            await ctx.send(
                f"⚠️ No se encontraron usuarios que contengan '{nombre_parcial}' en su nombre."
            )
            return

        embed = discord.Embed(
            title="🔍 Resultados de la Búsqueda de Usuarios",
            description=f"Usuarios que contienen '{nombre_parcial}' en su nombre:",
            color=discord.Color.green(),
        )

        for jugador in resultados:
            embed.add_field(
                name=jugador["Player"],
                value=(
                    f"**Clan**: {jugador['Clan']}\n"
                    f"**K/D Ratio**: {jugador['K/D Ratio']:.2f}\n"
                    f"**Performance Score**: {jugador['Performance Score']:.2f}"
                ),
                inline=True,
            )

        await ctx.send(embed=embed)

    # ── -promedios ────────────────────────────────────────────────────────

    @commands.command()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def promedios(self, ctx: commands.Context):
        try:
            data = await self.fetcher.fetch_clan_averages()
        except Exception as e:
            await ctx.send("Error al conectar con la base de datos. Inténtalo más tarde.")
            print(f"Error: {e}")
            return

        if not isinstance(data, list):
            await ctx.send("El formato de los datos no es válido.")
            return

        embed = discord.Embed(
            title="Promedios de Clanes",
            description="Promedios calculados para cada clan:",
            color=discord.Color.blue(),
        )

        clan_names = []
        performance_scores = []

        for clan_data in data:
            clan_name = clan_data.get("Clan", "Desconocido")
            kd_ratio = clan_data.get("K/D Ratio", 0)
            score_per_round = clan_data.get("Score per Round", 0)
            kills_per_round = clan_data.get("Kills per Round", 0)
            ps = clan_data.get("Performance Score", 0)

            clan_names.append(clan_name)
            performance_scores.append(ps)

            embed.add_field(
                name=f"🏅 {clan_name}",
                value=(
                    f"**🔹 Promedio K/D:** {kd_ratio:.2f}\n"
                    f"**🔹 Promedio Score:** {score_per_round:.2f}\n"
                    f"**🔹 Promedio Kills:** {kills_per_round:.2f}\n"
                    f"**🔹 Performance Score:** {ps:.2f}"
                ),
                inline=False,
            )

        buf = render_bar_chart(
            clan_names,
            performance_scores,
            "Performance Score de Clanes",
            "Clanes",
            "Performance Score",
        )
        file = discord.File(buf, filename="performance_scores_clanes.png")
        embed.set_image(url="attachment://performance_scores_clanes.png")
        await ctx.send(embed=embed, file=file)

    # ── -promedios_tops <cantidad> <metrica> ──────────────────────────────

    @commands.command()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def promedios_tops(
        self,
        ctx: commands.Context,
        cantidad: int = 15,
        metrica: str = "performance",
    ):
        if cantidad <= 0:
            await ctx.send("❗ **La cantidad debe ser mayor a 0.**")
            return

        metricas_validas = ["performance", "kd", "kills", "deaths", "rounds", "score"]
        if metrica not in metricas_validas:
            await ctx.send(
                "❗ **Métrica inválida.** Las métricas válidas son:\n"
                "`performance`, `kd`, `kills`, `deaths`, `rounds`, `score`."
            )
            return

        try:
            data = await self.fetcher.fetch_all_players()
        except Exception as e:
            await ctx.send("❌ **Error al conectar con la base de datos.** Inténtalo más tarde.")
            print(f"Error: {e}")
            return

        metric_key = METRIC_KEY_MAP.get(metrica, metrica)

        # Group players by clan
        clans: dict[str, list] = {}
        for player in data:
            cn = player.get("Clan", "Sin Clan")
            clans.setdefault(cn, []).append(player)

        embed = discord.Embed(
            title=f"🏆 **Promedios de los Mejores {cantidad} de Cada Clan** (Métrica: {metrica.capitalize()})",
            description=f"Promedios calculados usando los mejores {cantidad} jugadores de cada clan.",
            color=discord.Color.green(),
        )

        clan_names = []
        avg_values = []

        for cn, players in clans.items():
            top_players = sorted(
                players, key=lambda x: x.get(metric_key, 0), reverse=True
            )[:cantidad]
            avg = (
                sum(p.get(metric_key, 0) for p in top_players) / len(top_players)
                if top_players
                else 0
            )
            clan_names.append(cn)
            avg_values.append(avg)
            embed.add_field(
                name=f"🏅 {cn}",
                value=f"**🔹 Promedio {metrica.capitalize()}:** {avg:.2f}",
                inline=False,
            )

        buf = render_bar_chart(
            clan_names,
            avg_values,
            f"Promedio {metrica.capitalize()} de los Mejores {cantidad} Jugadores por Clan",
            "Clanes",
            f"Promedio {metrica.capitalize()}",
        )
        file = discord.File(buf, filename="promedios_tops.png")
        embed.set_image(url="attachment://promedios_tops.png")
        await ctx.send(embed=embed, file=file)


async def setup(bot: commands.Bot):
    await bot.add_cog(Stats(bot))
