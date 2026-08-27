import discord
from discord import app_commands
from discord.ext import commands


class TicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Create Ticket", emoji="🎟️", style=discord.ButtonStyle.primary, custom_id="ticket:create")
    async def create(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        existing = discord.utils.get(guild.text_channels, name=f"ticket-{interaction.user.id}")
        if existing:
            return await interaction.response.send_message(f"❌ You already have {existing.mention}.", ephemeral=True)
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True),
            guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True)
        }
        channel = await guild.create_text_channel(f"ticket-{interaction.user.id}", overwrites=overwrites)
        await channel.send(f"🎟️ {interaction.user.mention}", view=CloseTicketView())
        await interaction.response.send_message(f"✅ Ticket created: {channel.mention}", ephemeral=True)


class CloseTicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Close Ticket", emoji="🔒", style=discord.ButtonStyle.danger, custom_id="ticket:close")
    async def close(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("🔒 Closing ticket...")
        await interaction.channel.delete(reason=f"Ticket closed by {interaction.user}")


class Ticket(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        bot.add_view(TicketView())
        bot.add_view(CloseTicketView())

    @app_commands.command(name="ticket_panel", description="Post a ticket panel")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def ticket_panel(self, interaction):
        embed = discord.Embed(title="🎟️ Support Tickets", description="Click the button below to create a private support ticket.", color=discord.Color.blurple())
        await interaction.channel.send(embed=embed, view=TicketView())
        await interaction.response.send_message("✅ Ticket panel posted.", ephemeral=True)

    @app_commands.command(name="ticket_close", description="Close the current ticket")
    async def ticket_close(self, interaction):
        if not interaction.channel.name.startswith("ticket-"):
            return await interaction.response.send_message("❌ This isn't a ticket channel.", ephemeral=True)
        await interaction.response.send_message("🔒 Closing...")
        await interaction.channel.delete()


async def setup(bot):
    await bot.add_cog(Ticket(bot))
