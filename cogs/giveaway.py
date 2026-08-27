import asyncio
import random
import discord
import datetime
from discord import app_commands
from discord.ext import commands


class GiveawayView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.entries = set()

    @discord.ui.button(label="Enter Giveaway", emoji="🎉", style=discord.ButtonStyle.success, custom_id="giveaway:enter")
    async def enter(self, interaction, button):
        self.entries.add(interaction.user.id)
        await interaction.response.send_message("🎉 You're entered!", ephemeral=True)


class Giveaway(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.active = {}

    @app_commands.command(name="giveaway_start", description="Start a giveaway")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def giveaway_start(self, interaction, minutes: app_commands.Range[int,1,10080], prize: str):
        end = discord.utils.utcnow() + datetime.timedelta(minutes=minutes)
        view = GiveawayView()
        embed = discord.Embed(title="🎉 Giveaway", description=f"**Prize:** {prize}\n**Ends:** {discord.utils.format_dt(end,'R')}\nClick below to enter!", color=discord.Color.gold())
        msg = await interaction.channel.send(embed=embed, view=view)
        self.active[msg.id] = view
        await interaction.response.send_message("✅ Giveaway started.", ephemeral=True)
        await asyncio.sleep(minutes * 60)
        view = self.active.pop(msg.id, None)
        if not view:
            return
        winner = random.choice(list(view.entries)) if view.entries else None
        embed.title = "🎉 Giveaway Ended"
        embed.description = f"**Prize:** {prize}\n" + (f"🏆 Winner: <@{winner}>" if winner else "No valid entries.")
        await msg.edit(embed=embed, view=None)

    @app_commands.command(name="giveaway_end", description="End a giveaway by message ID")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def giveaway_end(self, interaction, message_id: str):
        view = self.active.pop(int(message_id), None)
        if not view:
            return await interaction.response.send_message("❌ Giveaway not found or already ended.")
        winner = random.choice(list(view.entries)) if view.entries else None
        await interaction.response.send_message(f"🏆 Winner: <@{winner}>" if winner else "No entries.")

    @app_commands.command(name="giveaway_reroll", description="Reroll a giveaway")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def giveaway_reroll(self, interaction, message_id: str):
        view = self.active.get(int(message_id))
        if not view or not view.entries:
            return await interaction.response.send_message("❌ No active entries found.")
        await interaction.response.send_message(f"🎲 New winner: <@{random.choice(list(view.entries))}>")


async def setup(bot):
    await bot.add_cog(Giveaway(bot))
