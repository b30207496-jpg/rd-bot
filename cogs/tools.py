import discord
from discord import app_commands
from discord.ext import commands


class Tools(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="servericon", description="Show the server icon")
    async def servericon(self, interaction):
        if not interaction.guild.icon:
            return await interaction.response.send_message("This server has no icon.")
        embed = discord.Embed(title=f"{interaction.guild.name} Icon")
        embed.set_image(url=interaction.guild.icon.url)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="channelstats", description="Show channel statistics")
    async def channelstats(self, interaction):
        g = interaction.guild
        text = sum(isinstance(c, discord.TextChannel) for c in g.channels)
        voice = sum(isinstance(c, discord.VoiceChannel) for c in g.channels)
        await interaction.response.send_message(f"🛠️ Text: **{text}**\n🔊 Voice: **{voice}**")


async def setup(bot):
    await bot.add_cog(Tools(bot))
