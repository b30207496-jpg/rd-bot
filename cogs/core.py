import discord
from discord import app_commands
from discord.ext import commands
import platform
import time


class Core(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.started = time.time()

    @app_commands.command(
        name="ping",
        description="Check bot latency"
    )
    async def ping(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            f"🏓 Pong! `{round(self.bot.latency * 1000)}ms`"
        )

    @app_commands.command(
        name="botinfo",
        description="Show bot information"
    )
    async def botinfo(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="🤖 Bot Information",
            color=discord.Color.blurple()
        )

        embed.add_field(
            name="Python",
            value=platform.python_version()
        )
        embed.add_field(
            name="Discord.py",
            value=discord.__version__
        )
        embed.add_field(
            name="Servers",
            value=str(len(self.bot.guilds))
        )
        embed.add_field(
            name="Uptime",
            value=f"{int(time.time() - self.started)} seconds"
        )

        await interaction.response.send_message(embed=embed)

    @app_commands.command(
        name="invite",
        description="Get the bot invite URL"
    )
    async def invite(self, interaction: discord.Interaction):
        client_id = self.bot.user.id

        url = discord.utils.oauth_url(
            client_id,
            permissions=discord.Permissions(
                administrator=True
            )
        )

        await interaction.response.send_message(
            f"🔗 {url}",
            ephemeral=True
        )

    @app_commands.command(
        name="help",
        description="Show all RD Bot commands"
    )
    async def help(self, interaction: discord.Interaction):

        embed = discord.Embed(
            title="🤖 RD Bot — Command Center",
            description=(
                "Here are all available commands.\n"
                "Commands are grouped by category."
            ),
            color=discord.Color.blurple()
        )

        for cog_name, cog in self.bot.cogs.items():

            commands_list = cog.get_app_commands()

            if not commands_list:
                continue

            lines = []

            for command in sorted(commands_list, key=lambda x: x.name):
                lines.append(
                    f"`/{command.name}` — {command.description}"
                )

            if lines:
                embed.add_field(
                    name=f"📂 {cog_name}",
                    value="\n".join(lines),
                    inline=False
                )

        embed.set_footer(
            text=f"RD Bot • {len(self.bot.cogs)} categories"
        )

        await interaction.response.send_message(
            embed=embed
        )


async def setup(bot):
    await bot.add_cog(Core(bot))
