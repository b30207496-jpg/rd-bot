import discord
from discord import app_commands
from discord.ext import commands


class LoggingCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="logging_set", description="Set the moderation/event log channel")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def logging_set(self, interaction, channel: discord.TextChannel):
        await self.bot.db.set_setting(interaction.guild.id, "log_channel", channel.id)
        await interaction.response.send_message(f"🔎 Logging channel set to {channel.mention}.")

    @app_commands.command(name="logging_disable", description="Disable logging")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def logging_disable(self, interaction):
        await self.bot.db.set_setting(interaction.guild.id, "log_channel", "")
        await interaction.response.send_message("✅ Logging disabled.")

    async def log(self, guild, title, description):
        cid = await self.bot.db.setting(guild.id, "log_channel")
        if not cid:
            return
        channel = guild.get_channel(int(cid))
        if channel:
            await channel.send(embed=discord.Embed(title=title, description=description, color=discord.Color.blurple()))

    @commands.Cog.listener()
    async def on_member_join(self, member):
        await self.log(member.guild, "📥 Member Joined", member.mention)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        await self.log(member.guild, "📤 Member Left", str(member))

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if message.guild and not message.author.bot:
            await self.log(message.guild, "🗑️ Message Deleted", f"Author: {message.author.mention}\nChannel: {message.channel.mention}")


async def setup(bot):
    await bot.add_cog(LoggingCog(bot))
