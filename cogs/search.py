import urllib.parse
import discord
from discord import app_commands
from discord.ext import commands


class Search(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="search", description="Create a web search link")
    async def search(self, interaction, query: str):
        q = urllib.parse.quote_plus(query)
        await interaction.response.send_message(
            f"🔎 Search results for **{discord.utils.escape_markdown(query)}**:\n"
            f"https://www.google.com/search?q={q}"
        )


async def setup(bot):
    await bot.add_cog(Search(bot))
