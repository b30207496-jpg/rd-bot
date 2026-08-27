import discord
from discord import app_commands
from discord.ext import commands


class Roles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # =========================
    # SELF ROLE
    # =========================

    @app_commands.command(
        name="role",
        description="Add or remove a role from yourself"
    )
    async def role(self, interaction: discord.Interaction, role: discord.Role):

        if role.is_default():
            return await interaction.response.send_message(
                "❌ You can't use the @everyone role.",
                ephemeral=True
            )

        if role.managed:
            return await interaction.response.send_message(
                "❌ That role is managed by Discord and can't be assigned.",
                ephemeral=True
            )

        if role >= interaction.guild.me.top_role:
            return await interaction.response.send_message(
                "❌ I can't manage that role. Move my bot role above it.",
                ephemeral=True
            )

        member = interaction.user

        try:
            if role in member.roles:
                await member.remove_roles(role)
                await interaction.response.send_message(
                    f"➖ Removed {role.mention} from you."
                )
            else:
                await member.add_roles(role)
                await interaction.response.send_message(
                    f"✅ Added {role.mention} to you."
                )

        except discord.Forbidden:
            await interaction.response.send_message(
                "❌ I don't have permission to manage that role.",
                ephemeral=True
            )

    # =========================
    # SHOW ROLES
    # =========================

    @app_commands.command(
        name="roles",
        description="Show the server's roles"
    )
    async def roles(self, interaction: discord.Interaction):

        roles = [
            role for role in interaction.guild.roles
            if not role.is_default()
        ]

        if not roles:
            return await interaction.response.send_message(
                "❌ This server has no custom roles."
            )

        # Discord messages have a character limit
        text = "\n".join(
            f"• {role.mention} — `{role.position}`"
            for role in reversed(roles)
        )

        embed = discord.Embed(
            title="🎭 Server Roles",
            description=text[:4000],
            color=discord.Color.blurple()
        )

        embed.set_footer(
            text=f"Total roles: {len(roles)}"
        )

        await interaction.response.send_message(embed=embed)

    # =========================
    # ADD ROLE
    # =========================

    @app_commands.command(
        name="addrole",
        description="Give a role to a member"
    )
    @app_commands.checks.has_permissions(manage_roles=True)
    async def addrole(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
        role: discord.Role
    ):

        if role.is_default() or role.managed:
            return await interaction.response.send_message(
                "❌ That role cannot be assigned.",
                ephemeral=True
            )

        if role >= interaction.guild.me.top_role:
            return await interaction.response.send_message(
                "❌ I can't manage that role. Move my bot role above it.",
                ephemeral=True
            )

        try:
            await member.add_roles(role)

            await interaction.response.send_message(
                f"✅ Added {role.mention} to {member.mention}."
            )

        except discord.Forbidden:
            await interaction.response.send_message(
                "❌ I don't have permission to manage that role.",
                ephemeral=True
            )

    # =========================
    # REMOVE ROLE
    # =========================

    @app_commands.command(
        name="removerole",
        description="Remove a role from a member"
    )
    @app_commands.checks.has_permissions(manage_roles=True)
    async def removerole(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
        role: discord.Role
    ):

        if role.is_default() or role.managed:
            return await interaction.response.send_message(
                "❌ That role cannot be removed.",
                ephemeral=True
            )

        if role >= interaction.guild.me.top_role:
            return await interaction.response.send_message(
                "❌ I can't manage that role.",
                ephemeral=True
            )

        try:
            await member.remove_roles(role)

            await interaction.response.send_message(
                f"✅ Removed {role.mention} from {member.mention}."
            )

        except discord.Forbidden:
            await interaction.response.send_message(
                "❌ I don't have permission to manage that role.",
                ephemeral=True
            )

    # =========================
    # ROLE INFO
    # =========================

    @app_commands.command(
        name="roleinfo",
        description="Show information about a role"
    )
    async def roleinfo(
        self,
        interaction: discord.Interaction,
        role: discord.Role
    ):

        embed = discord.Embed(
            title=f"🎭 {role.name}",
            color=role.color if role.color.value else discord.Color.blurple()
        )

        embed.add_field(
            name="🆔 Role ID",
            value=f"`{role.id}`",
            inline=False
        )

        embed.add_field(
            name="👥 Members",
            value=f"`{len(role.members)}`",
            inline=True
        )

        embed.add_field(
            name="📊 Position",
            value=f"`{role.position}`",
            inline=True
        )

        embed.add_field(
            name="🔒 Mentionable",
            value="Yes" if role.mentionable else "No",
            inline=True
        )

        embed.add_field(
            name="🤖 Managed",
            value="Yes" if role.managed else "No",
            inline=True
        )

        embed.add_field(
            name="📅 Created",
            value=discord.utils.format_dt(role.created_at, "F"),
            inline=False
        )

        await interaction.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(Roles(bot))
