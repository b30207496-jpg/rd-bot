import discord
from discord import app_commands
from discord.ext import commands


class Welcome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="welcome_set", description="Set the welcome channel")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def welcome_set(self, interaction, channel: discord.TextChannel, message: str = "Welcome {user} to {server}!"):
        await self.bot.db.set_setting(interaction.guild.id, "welcome_channel", channel.id)
        await self.bot.db.set_setting(interaction.guild.id, "welcome_message", message)
        await interaction.response.send_message(f"👋 Welcome channel set to {channel.mention}.")

    @app_commands.command(name="welcome_disable", description="Disable welcome messages")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def welcome_disable(self, interaction):
        await self.bot.db.set_setting(interaction.guild.id, "welcome_channel", "")
        await interaction.response.send_message("✅ Welcome messages disabled.")

    @commands.Cog.listener()
    async def on_member_join(self, member):
        cid = await self.bot.db.setting(member.guild.id, "welcome_channel")
        if not cid:
            return
        channel = member.guild.get_channel(int(cid))
        if not channel:
            return
        message = await self.bot.db.setting(member.guild.id, "welcome_message", "Welcome {user} to {server}!")
        await channel.send(message.replace("{user}", member.mention).replace("{server}", member.guild.name))


async def setup(bot):
    await bot.add_cog(Welcome(bot))
