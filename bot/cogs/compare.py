"""Compare cog -- compare, analizar_equipo, sugerir_equipo, comparar_equipos."""

import discord
from discord.ext import commands

from bot.config import (
    CLAN_JSON_MAP,
    performance_color,
)
from bot.services.chart_renderer import render_kd_chart, render_comparison_chart


class Compare(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @property
    def fetcher(self):
        return self.bot.data_fetcher

    # ── -compare <entity1> <entity2> ──────────────────────────────────────

    @commands.command()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def compare(self, ctx: commands.Context, entity1: str = None, entity2: str = None):
        """Compara las estadísticas de dos jugadores o clanes."""
        if not entity1 or not entity2:
            await ctx.send(
                "❗ Uso: `-compare <jugador1|clan1> <jugador2|clan2>`."
            )
            return

        try:
            data_players = await self.fetcher.fetch_all_players()
        except Exception as e:
            await ctx.send("❌ Error al conectar con la base de datos. Inténtalo más tarde.")
            print(f"Error: {e}")
            return

        p1 = next((p for p in data_players if p["Player"] == entity1), None)
        p2 = next((p for p in data_players if p["Player"] == entity2), None)

        if p1 and p2:
            # Player vs Player
            embed = discord.Embed(
                title=f"🔍 Comparación entre {entity1} y {entity2}",
                description="Estadísticas detalladas comparadas:",
                color=discord.Color.purple(),
            )
            embed.add_field(
                name="Estadística",
                value=(
                    "💥 **K/D Ratio**\n"
                    "🔫 **Kills per Round**\n"
                    "🎯 **Score per Round**\n"
                    "🌟 **Performance Score**\n"
                    "🎮 **Rounds Jugados**\n"
                    "☠️ **Total Kills**\n"
                    "🏆 **Total Score**"
                ),
                inline=True,
            )
            embed.add_field(
                name=f"🎮 {entity1}",
                value=(
                    f"{p1['K/D Ratio']:.2f}\n"
                    f"{p1.get('Kills per Round', 'N/A')}\n"
                    f"{p1.get('Score per Round', 'N/A'):.2f}\n"
                    f"{p1.get('Performance Score', 'N/A'):.2f}\n"
                    f"{p1.get('Rounds', 'N/A')}\n"
                    f"{p1.get('Total Kills', 'N/A')}\n"
                    f"{p1.get('Total Score', 'N/A')}"
                ),
                inline=True,
            )
            embed.add_field(
                name=f"🎮 {entity2}",
                value=(
                    f"{p2['K/D Ratio']:.2f}\n"
                    f"{p2.get('Kills per Round', 'N/A')}\n"
                    f"{p2.get('Score per Round', 'N/A'):.2f}\n"
                    f"{p2.get('Performance Score', 'N/A'):.2f}\n"
                    f"{p2.get('Rounds', 'N/A')}\n"
                    f"{p2.get('Total Kills', 'N/A')}\n"
                    f"{p2.get('Total Score', 'N/A')}"
                ),
                inline=True,
            )

            if p1["Performance Score"] > p2["Performance Score"]:
                resolution = f"🌟 **{entity1}** parece ser mejor que **{entity2}**."
            elif p1["Performance Score"] < p2["Performance Score"]:
                resolution = f"🌟 **{entity2}** parece ser mejor que **{entity1}**."
            else:
                resolution = "🤝 Ambos jugadores tienen un desempeño similar."

            embed.add_field(name="Resolución", value=resolution, inline=False)
            embed.set_footer(text="📅 Datos actualizados recientemente.")
            await ctx.send(embed=embed)

        else:
            # Clan vs Clan comparison
            def sumar_estadisticas(clan_name):
                total_kills = total_deaths = total_score = total_rounds = 0
                for player in data_players:
                    if player.get("Clan", "") == clan_name:
                        total_kills += player.get("Total Kills", 0)
                        total_deaths += player.get("Total Deaths", 0)
                        total_score += player.get("Total Score", 0)
                        total_rounds += player.get("Rounds", 0)
                return total_kills, total_deaths, total_score, total_rounds

            kills1, deaths1, score1, rounds1 = sumar_estadisticas(entity1)
            kills2, deaths2, score2, rounds2 = sumar_estadisticas(entity2)

            embed = discord.Embed(
                title=f"🔍 Comparación entre los clanes {entity1} y {entity2}",
                description="Totales de estadísticas comparadas:",
                color=discord.Color.gold(),
            )
            embed.add_field(
                name="Estadística",
                value=(
                    "☠️ **Total Kills**\n"
                    "💀 **Total Deaths**\n"
                    "🏆 **Total Score**\n"
                    "🎮 **Total Rounds**"
                ),
                inline=True,
            )
            embed.add_field(
                name=f"🏅 {entity1}",
                value=f"{kills1}\n{deaths1}\n{score1}\n{rounds1}",
                inline=True,
            )
            embed.add_field(
                name=f"🏅 {entity2}",
                value=f"{kills2}\n{deaths2}\n{score2}\n{rounds2}",
                inline=True,
            )

            if score1 > score2:
                resolution = f"🌟 **{entity1}** parece ser mejor que **{entity2}**."
            elif score1 < score2:
                resolution = f"🌟 **{entity2}** parece ser mejor que **{entity1}**."
            else:
                resolution = "🤝 Ambos clanes tienen un desempeño similar."

            embed.add_field(name="Resolución", value=resolution, inline=False)
            embed.set_footer(text="📅 Datos actualizados recientemente.")
            await ctx.send(embed=embed)

    # ── -analizar_equipo <jugadores...> ───────────────────────────────────

    @commands.command()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def analizar_equipo(self, ctx: commands.Context, *jugadores: str):
        if len(jugadores) < 1:
            await ctx.send(
                "❗ Por favor, proporciona al menos un jugador. "
                "Ejemplo: `-analizar_equipo Jugador1 Jugador2 ... JugadorN`."
            )
            return

        try:
            data = await self.fetcher.fetch_all_players()
        except Exception as e:
            await ctx.send("❌ Error al conectar con la base de datos. Inténtalo más tarde.")
            print(f"Error: {e}")
            return

        equipo = []
        for nombre in jugadores:
            found = next(
                (e for e in data if e["Player"].lower() == nombre.lower()), None
            )
            if not found:
                await ctx.send(f"⚠️ Jugador '{nombre}' no encontrado en la base de datos.")
                return
            equipo.append(found)

        total_score = sum(j["Total Score"] for j in equipo)
        total_kills = sum(j["Total Kills"] for j in equipo)
        total_deaths = sum(j["Total Deaths"] for j in equipo)
        total_rounds = sum(j["Rounds"] for j in equipo)
        avg_ps = sum(j["Performance Score"] for j in equipo) / len(equipo)
        avg_kpr = total_kills / total_rounds if total_rounds > 0 else 0
        avg_dpr = total_deaths / total_rounds if total_rounds > 0 else 0
        team_kd = total_kills / total_deaths if total_deaths > 0 else 0

        nombres = [j["Player"] for j in equipo]
        kd_ratios = [j["K/D Ratio"] for j in equipo]

        buf = render_kd_chart(nombres, kd_ratios, "K/D Ratio de Jugadores")

        embed = discord.Embed(
            title="📊 Análisis de Composición de Equipo",
            description="Aquí tienes el análisis del equipo seleccionado:",
            color=discord.Color.blue(),
        )
        embed.add_field(
            name="**📊 Métricas del Equipo**",
            value=(
                f"**Total Score**: {total_score}\n"
                f"**Total Kills**: {total_kills}\n"
                f"**Total Deaths**: {total_deaths}\n"
                f"**Total Rounds**: {total_rounds}\n"
                f"**Average Kills per Round**: {avg_kpr:.2f}\n"
                f"**Average Deaths per Round**: {avg_dpr:.2f}\n"
                f"**Team K/D Ratio**: {team_kd:.2f}\n"
                f"**Average Performance Score**: {avg_ps:.2f}"
            ),
            inline=False,
        )

        file = discord.File(buf, filename="team_analysis.png")
        embed.set_image(url="attachment://team_analysis.png")
        await ctx.send(embed=embed, file=file)

    # ── -sugerir_equipo <clan> <num_jugadores> ────────────────────────────

    @commands.command()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def sugerir_equipo(self, ctx: commands.Context, clan: str = None, num_jugadores: int = 8):
        if not clan:
            await ctx.send("❗ Uso: `-sugerir_equipo <clan> <cantidad>`.")
            return

        if num_jugadores < 2 or num_jugadores > 8:
            await ctx.send(
                "❗ Por favor, selecciona entre 2 y 8 jugadores. "
                "Ejemplo: `-sugerir_equipo LDH 5`."
            )
            return

        if clan not in CLAN_JSON_MAP:
            await ctx.send(
                f"❗ Clan '{clan}' no reconocido. "
                f"Los clanes válidos son: {', '.join(CLAN_JSON_MAP.keys())}."
            )
            return

        try:
            data = await self.fetcher.fetch_json(CLAN_JSON_MAP[clan])
        except Exception as e:
            await ctx.send("❌ Error al conectar con la base de datos. Inténtalo más tarde.")
            print(f"Error: {e}")
            return

        jugadores_ordenados = sorted(
            data,
            key=lambda x: (x.get("Kills per Round", 0), -x.get("Deaths per Round", 0)),
            reverse=True,
        )
        equipo = jugadores_ordenados[:num_jugadores]

        total_score = sum(j["Total Score"] for j in equipo)
        total_kills = sum(j["Total Kills"] for j in equipo)
        total_deaths = sum(j["Total Deaths"] for j in equipo)
        total_rounds = sum(j["Rounds"] for j in equipo)
        avg_ps = sum(j["Performance Score"] for j in equipo) / len(equipo)
        avg_kpr = total_kills / total_rounds if total_rounds > 0 else 0
        avg_dpr = total_deaths / total_rounds if total_rounds > 0 else 0
        team_kd = total_kills / total_deaths if total_deaths > 0 else 0

        embed = discord.Embed(
            title=f"📊 Equipo Sugerido para {clan}",
            description=f"Aquí tienes el equipo sugerido del clan {clan}:",
            color=discord.Color.blue(),
        )

        for j in equipo:
            embed.add_field(
                name=f"🎮 {j['Player']}",
                value=(
                    f"**K/D Ratio**: {j['K/D Ratio']:.2f}\n"
                    f"**Kills per Round**: {j['Kills per Round']:.2f}\n"
                    f"**Deaths per Round**: {j['Deaths per Round']:.2f}\n"
                    f"**Total Kills**: {j['Total Kills']}\n"
                    f"**Total Deaths**: {j['Total Deaths']}\n"
                    f"**Rounds Jugados**: {j['Rounds']}\n"
                    f"**Performance Score**: {j['Performance Score']:.2f}"
                ),
                inline=True,
            )

        embed.add_field(
            name="**📊 Métricas del Equipo**",
            value=(
                f"**Total Score**: {total_score}\n"
                f"**Total Kills**: {total_kills}\n"
                f"**Total Deaths**: {total_deaths}\n"
                f"**Total Rounds**: {total_rounds}\n"
                f"**Average Kills per Round**: {avg_kpr:.2f}\n"
                f"**Average Deaths per Round**: {avg_dpr:.2f}\n"
                f"**Team K/D Ratio**: {team_kd:.2f}\n"
                f"**Average Performance Score**: {avg_ps:.2f}"
            ),
            inline=False,
        )

        await ctx.send(embed=embed)

    # ── -comparar_equipos <equipo1> <equipo2> <jugadores...> ──────────────

    @commands.command()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def comparar_equipos(
        self,
        ctx: commands.Context,
        equipo1: str = None,
        equipo2: str = None,
        *jugadores: str,
    ):
        if not equipo1 or not equipo2:
            await ctx.send(
                "❗ Uso: `-comparar_equipos Equipo1 Equipo2 Jugador1_E1 ... Jugador1_E2 ...`."
            )
            return

        if len(jugadores) < 2 or len(jugadores) % 2 != 0:
            await ctx.send(
                "❗ Por favor, proporciona un número par de jugadores. "
                "Ejemplo: `-comparar_equipos Equipo1 Equipo2 Jugador1_E1 Jugador2_E1 ... Jugador1_E2 Jugador2_E2 ...`."
            )
            return

        try:
            data = await self.fetcher.fetch_all_players()
        except Exception as e:
            await ctx.send("❌ Error al conectar con la base de datos. Inténtalo más tarde.")
            print(f"Error: {e}")
            return

        mitad = len(jugadores) // 2
        equipos = {
            equipo1: jugadores[:mitad],
            equipo2: jugadores[mitad:],
        }

        resultados = {}
        all_team_data = {}

        for equipo_name, nombres in equipos.items():
            equipo_data = []
            for nombre in nombres:
                found = next(
                    (e for e in data if e["Player"].lower() == nombre.lower()), None
                )
                if not found:
                    await ctx.send(f"⚠️ Jugador '{nombre}' no encontrado en la base de datos.")
                    return
                equipo_data.append(found)

            total_score = sum(j["Total Score"] for j in equipo_data)
            total_kills = sum(j["Total Kills"] for j in equipo_data)
            total_deaths = sum(j["Total Deaths"] for j in equipo_data)
            total_rounds = sum(j["Rounds"] for j in equipo_data)
            avg_ps = sum(j["Performance Score"] for j in equipo_data) / len(equipo_data)
            avg_kpr = total_kills / total_rounds if total_rounds > 0 else 0
            avg_dpr = total_deaths / total_rounds if total_rounds > 0 else 0
            team_kd = total_kills / total_deaths if total_deaths > 0 else 0

            resultados[equipo_name] = {
                "total_score": total_score,
                "total_kills": total_kills,
                "total_deaths": total_deaths,
                "total_rounds": total_rounds,
                "avg_performance_score": avg_ps,
                "avg_kills_per_round": avg_kpr,
                "avg_deaths_per_round": avg_dpr,
                "team_kd_ratio": team_kd,
            }
            all_team_data[equipo_name] = equipo_data

        # Generate comparison chart
        team_names = list(all_team_data.keys())
        buf = render_comparison_chart(
            team_names[0],
            all_team_data[team_names[0]],
            team_names[1],
            all_team_data[team_names[1]],
        )

        embed = discord.Embed(
            title="📊 Comparación de Equipos",
            description="Aquí tienes la comparación de los equipos seleccionados:",
            color=discord.Color.blue(),
        )

        for equipo_name, datos in resultados.items():
            embed.add_field(
                name=f"**📊 Métricas del Equipo {equipo_name}**",
                value=(
                    f"**Total Score**: {datos['total_score']}\n"
                    f"**Total Kills**: {datos['total_kills']}\n"
                    f"**Total Deaths**: {datos['total_deaths']}\n"
                    f"**Total Rounds**: {datos['total_rounds']}\n"
                    f"**Average Kills per Round**: {datos['avg_kills_per_round']:.2f}\n"
                    f"**Average Deaths per Round**: {datos['avg_deaths_per_round']:.2f}\n"
                    f"**Team K/D Ratio**: {datos['team_kd_ratio']:.2f}\n"
                    f"**Average Performance Score**: {datos['avg_performance_score']:.2f}"
                ),
                inline=False,
            )

        file = discord.File(buf, filename="team_comparison.png")
        embed.set_image(url="attachment://team_comparison.png")
        await ctx.send(embed=embed, file=file)


async def setup(bot: commands.Bot):
    await bot.add_cog(Compare(bot))
