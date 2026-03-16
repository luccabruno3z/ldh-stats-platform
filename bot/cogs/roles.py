"""Roles cog -- message command and reaction-based role assignment.

Stores role configs per guild (not global bot attributes) to fix the
duplicate-handler / single-config bug from the original bot.
"""

import discord
from discord.ext import commands


class Roles(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        # Per-guild role configs: {guild_id: {message_id: (emoji_str, role_id)}}
        self._configs: dict[int, dict[int, tuple[str, int]]] = {}

    # ── -message <emoji> <role_name> <message text> ───────────────────────

    @commands.command(name="message")
    async def message_cmd(self, ctx: commands.Context, emoji: str, role_name: str, *, message: str):
        """Envía un mensaje con reacción; los usuarios que reaccionen reciben un rol."""
        if not ctx.author.guild_permissions.administrator:
            await ctx.send("❌ No tienes permisos para usar este comando.")
            return

        role = discord.utils.get(ctx.guild.roles, name=role_name)
        if not role:
            await ctx.send(f"❌ El rol '{role_name}' no existe.")
            return

        msg = await ctx.send(message)
        await msg.add_reaction(emoji)

        # Store config per guild
        guild_configs = self._configs.setdefault(ctx.guild.id, {})
        guild_configs[msg.id] = (emoji, role.id)

        await ctx.send(
            f"✅ Mensaje enviado y reacción {emoji} añadida. "
            f"Los usuarios que reaccionen recibirán el rol '{role_name}'."
        )

    # ── Reaction add ──────────────────────────────────────────────────────

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        if payload.user_id == self.bot.user.id:
            return

        guild_configs = self._configs.get(payload.guild_id)
        if not guild_configs:
            return

        config = guild_configs.get(payload.message_id)
        if not config:
            return

        emoji_str, role_id = config
        if str(payload.emoji) != emoji_str:
            return

        guild = self.bot.get_guild(payload.guild_id)
        if not guild:
            return
        member = guild.get_member(payload.user_id)
        if not member:
            return

        role = guild.get_role(role_id)
        if role:
            await member.add_roles(role)
            try:
                await member.send(
                    f"🎉 ¡Has recibido el rol '{role.name}' por reaccionar con {payload.emoji}!"
                )
            except discord.Forbidden:
                pass  # DMs disabled
        else:
            try:
                await member.send("❌ El rol no existe o no se pudo asignar.")
            except discord.Forbidden:
                pass

    # ── Reaction remove ───────────────────────────────────────────────────

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload: discord.RawReactionActionEvent):
        if payload.user_id == self.bot.user.id:
            return

        guild_configs = self._configs.get(payload.guild_id)
        if not guild_configs:
            return

        config = guild_configs.get(payload.message_id)
        if not config:
            return

        emoji_str, role_id = config
        if str(payload.emoji) != emoji_str:
            return

        guild = self.bot.get_guild(payload.guild_id)
        if not guild:
            return
        member = guild.get_member(payload.user_id)
        if not member:
            return

        role = guild.get_role(role_id)
        if role:
            await member.remove_roles(role)
            try:
                await member.send(
                    f"❌ El rol '{role.name}' ha sido removido al quitar la reacción de {payload.emoji}."
                )
            except discord.Forbidden:
                pass


async def setup(bot: commands.Bot):
    await bot.add_cog(Roles(bot))
