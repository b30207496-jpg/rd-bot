import discord
from discord import app_commands
from discord.ext import commands


class ServerStats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="serverstats", description="Show detailed server statistics")
    async def serverstats(self, interaction):
        g = interaction.guild
        online = sum(1 for m in g.members if m.status != discord.Status.offline)
        embed = discord.Embed(title="📊 Server Statistics", color=discord.Color.blurple())
        embed.add_field(name="Members", value=str(g.member_count))
        embed.add_field(name="Online", value=str(online))
        embed.add_field(name="Text Channels", value=str(len(g.text_channels)))
        embed.add_field(name="Voice Channels", value=str(len(g.voice_channels)))
        embed.add_field(name="Categories", value=str(len(g.categories)))
        embed.add_field(name="Roles", value=str(len(g.roles)))
        await interaction.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(ServerStats(bot))
