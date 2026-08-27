import random
import discord
from discord import app_commands
from discord.ext import commands


class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="8ball", description="Ask the magic 8-ball")
    async def eightball(self, interaction, question: str):
        answers = ["Yes.", "No.", "Maybe.", "Definitely!", "Ask again later.", "Absolutely not."]
        await interaction.response.send_message(f"🎱 **Question:** {question}\n**Answer:** {random.choice(answers)}")

    @app_commands.command(name="coinflip", description="Flip a coin")
    async def coinflip(self, interaction):
        await interaction.response.send_message(f"🪙 **{random.choice(['Heads', 'Tails'])}**")

    @app_commands.command(name="roll", description="Roll a dice")
    async def roll(self, interaction, sides: app_commands.Range[int, 2, 1000] = 6):
        await interaction.response.send_message(f"🎲 You rolled **{random.randint(1, sides)}** / {sides}")

    @app_commands.command(name="choose", description="Choose between comma-separated options")
    async def choose(self, interaction, options: str):
        choices = [x.strip() for x in options.split(",") if x.strip()]
        if len(choices) < 2:
            return await interaction.response.send_message("Give me at least two options separated by commas.")
        await interaction.response.send_message(f"🎯 I choose: **{random.choice(choices)}**")

    @app_commands.command(name="ship", description="Calculate a fun compatibility score")
    async def ship(self, interaction, user1: discord.Member, user2: discord.Member):
        score = random.randint(0, 100)
        await interaction.response.send_message(f"💘 {user1.mention} + {user2.mention} = **{score}%**")


async def setup(bot):
    await bot.add_cog(Fun(bot))
