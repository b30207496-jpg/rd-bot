import discord
from discord import app_commands
from discord.ext import commands


class Community(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="poll", description="Create a yes/no poll")
    @app_commands.describe(question="Poll question")
    async def poll(self, interaction, question: str):
        embed = discord.Embed(title="📊 Poll", description=question, color=discord.Color.blurple())
        embed.set_footer(text=f"Poll by {interaction.user}")
        msg = await interaction.channel.send(embed=embed)
        await msg.add_reaction("👍")
        await msg.add_reaction("👎")
        await interaction.response.send_message("✅ Poll created.", ephemeral=True)

    @app_commands.command(name="announce", description="Send an announcement")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def announce(self, interaction, channel: discord.TextChannel, message: str):
        await channel.send(embed=discord.Embed(
            title="📢 Announcement", description=message, color=discord.Color.blurple()
        ))
        await interaction.response.send_message("✅ Announcement sent.", ephemeral=True)

    @app_commands.command(name="membercount", description="Show member counts")
    async def membercount(self, interaction):
        g = interaction.guild
        await interaction.response.send_message(
            f"👥 Members: **{g.member_count}**\n"
            f"🤖 Bots: **{sum(m.bot for m in g.members)}**"
        )


async def setup(bot):
    await bot.add_cog(Community(bot))
