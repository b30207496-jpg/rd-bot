import discord
from discord import app_commands
from discord.ext import commands


class VerifyView(discord.ui.View):
    def __init__(self, role_id):
        super().__init__(timeout=None)
        self.role_id = role_id

    @discord.ui.button(label="Verify", emoji="✅", style=discord.ButtonStyle.success, custom_id="verification:verify")
    async def verify(self, interaction, button):
        role = interaction.guild.get_role(self.role_id)
        if not role:
            return await interaction.response.send_message("❌ Verification role no longer exists.", ephemeral=True)
        await interaction.user.add_roles(role, reason="Verification button")
        await interaction.response.send_message("✅ You are verified!", ephemeral=True)


class Verification(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="verification_setup", description="Create a verification panel")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def verification_setup(self, interaction, role: discord.Role):
        await self.bot.db.set_setting(interaction.guild.id, "verify_role", role.id)
        embed = discord.Embed(title="✅ Verification", description="Click **Verify** to receive the verified role.", color=discord.Color.green())
        await interaction.channel.send(embed=embed, view=VerifyView(role.id))
        await interaction.response.send_message("✅ Verification panel posted.", ephemeral=True)

    @app_commands.command(name="verification_disable", description="Disable verification")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def verification_disable(self, interaction):
        await self.bot.db.set_setting(interaction.guild.id, "verify_role", "")
        await interaction.response.send_message("✅ Verification setting cleared.", ephemeral=True)


async def setup(bot):
    await bot.add_cog(Verification(bot))
