import discord
from discord import app_commands
from discord.ext import commands


class AutoRole(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="autorole",
        description="Set the role automatically given to new members"
    )
    @app_commands.checks.has_permissions(manage_guild=True)
    async def autorole(self, interaction: discord.Interaction, role: discord.Role):
        await self.bot.db.set_setting(
            interaction.guild.id,
            "autorole",
            str(role.id)
        )

        await interaction.response.send_message(
            f"✅ Auto role set to {role.mention}."
        )

    @app_commands.command(
        name="autorole_disable",
        description="Disable automatic roles"
    )
    @app_commands.checks.has_permissions(manage_guild=True)
    async def autorole_disable(self, interaction: discord.Interaction):
        await self.bot.db.set_setting(
            interaction.guild.id,
            "autorole",
            ""
        )

        await interaction.response.send_message(
            "✅ Auto role disabled."
        )

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        role_id = await self.bot.db.setting(
            member.guild.id,
            "autorole"
        )

        if not role_id:
            return

        role = member.guild.get_role(int(role_id))

        if not role:
            return

        try:
            await member.add_roles(role, reason="Auto role")
        except discord.Forbidden:
            pass


async def setup(bot):
    await bot.add_cog(AutoRole(bot))
