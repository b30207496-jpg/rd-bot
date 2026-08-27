import discord
from discord import app_commands
from discord.ext import commands
import platform
import time


class Core(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.started = time.time()

    @app_commands.command(name="ping", description="Check bot latency")
    async def ping(self, interaction):
        await interaction.response.send_message(
            f"🏓 Pong! `{round(self.bot.latency * 1000)}ms`"
        )

    @app_commands.command(name="botinfo", description="Show bot information")
    async def botinfo(self, interaction):
        embed = discord.Embed(title="🤖 Bot Information", color=discord.Color.blurple())
        embed.add_field(name="Python", value=platform.python_version())
        embed.add_field(name="Discord.py", value=discord.__version__)
        embed.add_field(name="Servers", value=str(len(self.bot.guilds)))
        embed.add_field(name="Uptime", value=f"{int(time.time()-self.started)} seconds")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="invite", description="Get the bot invite URL")
    async def invite(self, interaction):
        client_id = self.bot.user.id
        perms = discord.Permissions(administrator=True).value
        url = discord.utils.oauth_url(client_id, permissions=discord.Permissions(administrator=perms))
        await interaction.response.send_message(f"🔗 {url}", ephemeral=True)


async def setup(bot):
    await bot.add_cog(Core(bot))
