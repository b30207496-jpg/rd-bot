import discord
from discord import app_commands
from discord.ext import commands


class RoleButton(discord.ui.Button):
    def __init__(self, role):
        super().__init__(label=role.name[:80], style=discord.ButtonStyle.secondary, custom_id=f"rr:{role.id}")
        self.role_id = role.id

    async def callback(self, interaction):
        role = interaction.guild.get_role(self.role_id)
        if not role:
            return await interaction.response.send_message("❌ Role not found.", ephemeral=True)
        if role in interaction.user.roles:
            await interaction.user.remove_roles(role)
            await interaction.response.send_message(f"➖ Removed {role.mention}.", ephemeral=True)
        else:
            await interaction.user.add_roles(role)
            await interaction.response.send_message(f"➕ Added {role.mention}.", ephemeral=True)


class ReactionRoleView(discord.ui.View):
    def __init__(self, roles):
        super().__init__(timeout=None)
        for role in roles[:25]:
            self.add_item(RoleButton(role))


class ReactionRoles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="reactionrole_panel", description="Create a role button panel")
    @app_commands.checks.has_permissions(manage_roles=True)
    async def reactionrole_panel(self, interaction, roles: str):
        ids = []
        for part in roles.split():
            if part.isdigit():
                ids.append(int(part))
        found = [interaction.guild.get_role(x) for x in ids]
        found = [r for r in found if r]
        if not found:
            return await interaction.response.send_message("Mention roles or provide their IDs.", ephemeral=True)
        embed = discord.Embed(title="🔎 Role Selection", description="Click a button to toggle a role.", color=discord.Color.blurple())
        await interaction.channel.send(embed=embed, view=ReactionRoleView(found))
        await interaction.response.send_message("✅ Role panel posted.", ephemeral=True)


async def setup(bot):
    await bot.add_cog(ReactionRoles(bot))
