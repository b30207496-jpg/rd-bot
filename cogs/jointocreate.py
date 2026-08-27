import discord
from discord import app_commands
from discord.ext import commands


class JoinToCreate(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.owners = {}

    @app_commands.command(name="jtc_setup", description="Create a Join To Create voice channel")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def jtc_setup(self, interaction):
        channel = await interaction.guild.create_voice_channel("🔨 Join To Create")
        await self.bot.db.set_setting(interaction.guild.id, "jtc_channel", channel.id)
        await interaction.response.send_message(f"🔨 Join **{channel.name}** to create a temporary voice channel.")

    @app_commands.command(name="jtc_disable", description="Disable Join To Create")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def jtc_disable(self, interaction):
        await self.bot.db.set_setting(interaction.guild.id, "jtc_channel", "")
        await interaction.response.send_message("✅ Join To Create disabled.")

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if not after.channel:
            return
        cid = await self.bot.db.setting(member.guild.id, "jtc_channel")
        if not cid or after.channel.id != int(cid):
            return
        channel = await member.guild.create_voice_channel(f"🔊 {member.display_name}'s Room")
        self.owners[channel.id] = member.id
        await member.move_to(channel)

    @commands.Cog.listener()
    async def on_voice_state_update_cleanup(self, member, before, after):
        if before.channel and before.channel.id in self.owners and len(before.channel.members) == 0:
            try:
                await before.channel.delete()
            except discord.HTTPException:
                pass


async def setup(bot):
    await bot.add_cog(JoinToCreate(bot))
