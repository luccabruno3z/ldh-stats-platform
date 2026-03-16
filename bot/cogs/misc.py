"""Misc cog -- ayuda, hola, guias, visualizador, pagina, apagar, on_ready, on_command_error."""

import discord
from discord.ext import commands

from bot.config import GITHUB_INDEX, GITHUB_GUIDES, GITHUB_VISUALIZER_2D


class Misc(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # ── on_ready ──────────────────────────────────────────────────────────

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Bot conectado como {self.bot.user}")

    # ── on_command_error ──────────────────────────────────────────────────

    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error):
        # Unwrap if wrapped
        error = getattr(error, "original", error)

        if isinstance(error, commands.CommandNotFound):
            await ctx.send(
                "❌ **Comando no reconocido.** Usa `-ayuda` para ver la lista de comandos disponibles."
            )
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(
                f"❗ Faltan argumentos. Asegúrate de usar el comando correctamente. "
                f"Ejemplo: `-estadisticas <jugador>`."
            )
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send("🚫 No tienes permisos para ejecutar este comando.")
        elif isinstance(error, commands.BadArgument):
            await ctx.send("⚠️ Argumento inválido. Revisa los parámetros del comando.")
        elif isinstance(error, commands.CommandOnCooldown):
            await ctx.send(
                f"⏳ Este comando está en cooldown. Intenta de nuevo en {error.retry_after:.1f}s."
            )
        else:
            await ctx.send("❗ Ocurrió un error inesperado. Intenta de nuevo más tarde.")
            print(f"Error inesperado: {error}")

    # ── -hola ─────────────────────────────────────────────────────────────

    @commands.command()
    async def hola(self, ctx: commands.Context):
        await ctx.send("¡Hola! ¿En qué puedo ayudarte?")

    # ── -guias ────────────────────────────────────────────────────────────

    @commands.command()
    async def guias(self, ctx: commands.Context):
        await ctx.send(f"[Aquí tienes acceso a las guías de la página!]({GITHUB_GUIDES})")

    # ── -visualizador ─────────────────────────────────────────────────────

    @commands.command()
    async def visualizador(self, ctx: commands.Context):
        await ctx.send(f"[Aquí tienes acceso al visualizador 2D!]({GITHUB_VISUALIZER_2D})")

    # ── -pagina ───────────────────────────────────────────────────────────

    @commands.command()
    async def pagina(self, ctx: commands.Context):
        await ctx.send(f"[Aquí tienes la pagina de la LDH!]({GITHUB_INDEX})")

    # ── -apagar (owner only) ──────────────────────────────────────────────

    @commands.command()
    @commands.is_owner()
    async def apagar(self, ctx: commands.Context):
        await ctx.send("🔌 Apagando el bot...")
        await self.bot.close()

    # ── -ayuda ────────────────────────────────────────────────────────────

    @commands.command()
    async def ayuda(self, ctx: commands.Context):
        embed = discord.Embed(
            title="📜 **Lista de Comandos Disponibles**",
            description="Aquí tienes todos los comandos organizados por categorías:",
            color=discord.Color.blue(),
        )

        embed.add_field(
            name="🔧 **Comandos Básicos**",
            value=(
                "`-hola` - Saluda al bot.\n"
                "**Uso:** `-hola`\n\n"
                "`-guias` - Accede a las guías de la página.\n"
                "**Uso:** `-guias`\n\n"
                "`-visualizador` - Accede al visualizador 2D.\n"
                "**Uso:** `-visualizador`\n\n"
                "`-pagina` - Muestra el enlace a la página principal.\n"
                "**Uso:** `-pagina`\n\n"
                "`-apagar` - Apaga el bot (solo el dueño del bot puede usar este comando).\n"
                "**Uso:** `-apagar`"
            ),
            inline=False,
        )

        embed.add_field(
            name="📊 **Estadísticas y Análisis**",
            value=(
                "`-estadisticas <jugador>` - Muestra estadísticas detalladas de un jugador.\n"
                "**Uso:** `-estadisticas {nombre_jugador}`\n\n"
                "`-compare <jugador1> <jugador2>` - Compara estadísticas de dos jugadores.\n"
                "**Uso:** `-compare {jugador1} {jugador2}`\n\n"
                "`-analizar_equipo <jugadores>` - Analiza estadísticas de un equipo de jugadores.\n"
                "**Uso:** `-analizar_equipo {jugador1} {jugador2} ...`\n\n"
                "`-sugerir_equipo <clan> <num_jugadores>` - Sugiere un equipo del clan especificado.\n"
                "**Uso:** `-sugerir_equipo {clan} {cantidad_jugadores}`\n\n"
                "`-buscar_usuario <parte_nombre>` - Busca jugadores por parte de su nombre.\n"
                "**Uso:** `-buscar_usuario {parte_nombre}`\n\n"
                "`-historial <jugador>` - Muestra un gráfico histórico del Performance Score de un jugador.\n"
                "**Uso:** `-historial {nombre_jugador}`"
            ),
            inline=False,
        )

        embed.add_field(
            name="🏅 **Rankings y Promedios**",
            value=(
                "`-top <cantidad> <categoría> <métrica>` - Muestra el top de jugadores según la categoría y métrica especificada.\n"
                "**Uso:** `-top {cantidad} {categoría} {métrica}`\n"
                "**Categorías:** `general`, `ldh`, `sae`, `fi`, `141`, `fi-r`, `r-ldh`, `e-lam`, `300`, `rim-la`, `adg`\n"
                "**Métricas:** `performance`, `kd`, `kills`, `deaths`, `rounds`\n\n"
                "`-promedios_tops <cantidad> <métrica>` - Calcula los promedios de los mejores jugadores por clan.\n"
                "**Uso:** `-promedios_tops {cantidad} {métrica}`\n"
                "**Métricas:** `performance`, `kd`, `kills`, `deaths`, `rounds`, `score`\n\n"
                "`-promedios` - Muestra los promedios de estadísticas por clan.\n"
                "**Uso:** `-promedios`"
            ),
            inline=False,
        )

        embed.add_field(
            name="📈 **Gráficos Interactivos**",
            value=(
                "`-grafico <clan>` - Muestra el gráfico interactivo de un clan (o `all`/`todos` para todos).\n"
                "**Uso:** `-grafico {clan}`\n\n"
                "`-graficoldh` - Muestra el gráfico interactivo de la LDH.\n"
                "**Uso:** `-graficoldh`\n\n"
                "`-graficosae` - Muestra el gráfico interactivo de la SAE.\n"
                "**Uso:** `-graficosae`\n\n"
                "`-graficofi` - Muestra el gráfico interactivo de la FI.\n"
                "**Uso:** `-graficofi`\n\n"
                "`-graficofi_r` - Muestra el gráfico interactivo de la FI-R.\n"
                "**Uso:** `-graficofi_r`\n\n"
                "`-grafico141` - Muestra el gráfico interactivo del 141.\n"
                "**Uso:** `-grafico141`\n\n"
                "`-grafico300` - Muestra el gráfico interactivo de 300.\n"
                "**Uso:** `-grafico300`\n\n"
                "`-graficoe_lam` - Muestra el gráfico interactivo de la E-LAM.\n"
                "**Uso:** `-graficoe_lam`\n\n"
                "`-graficor_ldh` - Muestra el gráfico interactivo de la R-LDH.\n"
                "**Uso:** `-graficor_ldh`"
            ),
            inline=False,
        )

        embed.add_field(
            name="📚 **Consejos y Otros**",
            value=(
                "`-tips <kit>` - Proporciona consejos según el kit seleccionado.\n"
                "**Uso:** `-tips {kit}`\n"
                "**Kits disponibles:** `rifleman`, `medic`, `automatic rifleman`, `grenadier`, `sniper`, `lat`, `hat`, `combat engineer`\n\n"
                "`-countdown <fecha> <hora>` - Inicia un countdown hasta una fecha y hora específica.\n"
                "**Uso:** `-countdown {DD/MM/YYYY} {HH:MM}`"
            ),
            inline=False,
        )

        embed.set_footer(
            text="Usa los comandos con el prefijo `-` para interactuar con el bot. ¡Diviértete!"
        )
        await ctx.send(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(Misc(bot))
