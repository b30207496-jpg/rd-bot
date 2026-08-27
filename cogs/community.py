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

    @app_commands.command(name="coinflip", description="Flip a coin")
    async def coinflip(self, interaction: discord.Interaction):
        import random

        result = random.choice(["Heads", "Tails"])

        await interaction.response.send_message(
            f"🪙 The coin landed on **{result}**!"
        )

    @app_commands.command(name="roll", description="Roll a dice")
    async def roll(
        self,
        interaction: discord.Interaction,
        sides: app_commands.Range[int, 2, 100]
    ):
        import random

        result = random.randint(1, sides)

        await interaction.response.send_message(
            f"🎲 You rolled **{result}** (1-{sides})!"
        )

    @app_commands.command(
        name="choose",
        description="Choose randomly between options"
    )
    async def choose(
        self,
        interaction: discord.Interaction,
        choices: str
    ):
        import random

        options = [
            option.strip()
            for option in choices.split(",")
            if option.strip()
        ]

        if len(options) < 2:
            return await interaction.response.send_message(
                "❌ Give me at least two choices separated by commas.",
                ephemeral=True
            )

        result = random.choice(options)

        await interaction.response.send_message(
            f"🎯 I choose: **{result}**"
        )

    @app_commands.command(
        name="8ball",
        description="Ask the magic 8-ball"
    )
    async def eightball(
        self,
        interaction: discord.Interaction,
        question: str
    ):
        import random

        answers = [
            "Yes! ✨",
            "No. ❌",
            "Definitely! 🔥",
            "Probably. 🤔",
            "Ask me again later. 🔮",
            "Absolutely not. 💀",
            "It is very likely. 👀",
            "I don't think so. 😭"
        ]

        answer = random.choice(answers)

        embed = discord.Embed(
            title="🎱 Magic 8-Ball",
            color=discord.Color.blurple()
        )

        embed.add_field(
            name="Question",
            value=question,
            inline=False
        )

        embed.add_field(
            name="Answer",
            value=answer,
            inline=False
        )

        await interaction.response.send_message(embed=embed)

    @app_commands.command(
        name="ship",
        description="Check compatibility between two members"
    )
    async def ship(
        self,
        interaction: discord.Interaction,
        user1: discord.Member,
        user2: discord.Member
    ):
        import random

        percentage = random.randint(0, 100)

        if percentage >= 90:
            message = "💖 Perfect match!"
        elif percentage >= 70:
            message = "💕 Looking good!"
        elif percentage >= 40:
            message = "💛 There might be something there!"
        else:
            message = "💀 Better stay friends!"

        await interaction.response.send_message(
            f"💘 **Compatibility Test**\n"
            f"{user1.mention} ❤️ {user2.mention}\n\n"
            f"💯 Compatibility: **{percentage}%**\n"
            f"{message}"
        )
async def setup(bot):
    await bot.add_cog(Community(bot))
