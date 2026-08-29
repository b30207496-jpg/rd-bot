import discord
from discord import app_commands
from discord.ext import commands
import platform
import time


class HelpView(discord.ui.View):
    def __init__(self, pages, user):
        super().__init__(timeout=300)
        self.pages = pages
        self.user = user
        self.current_page = 0
        self.message = None
        self.update_buttons()

    def update_buttons(self):
        self.previous.disabled = self.current_page == 0
        self.next.disabled = self.current_page >= len(self.pages) - 1

    async def interaction_check(self, interaction: discord.Interaction):
        if interaction.user.id != self.user.id:
            await interaction.response.send_message(
                "❌ This help menu isn't yours.",
                ephemeral=True
            )
            return False

        return True

    @discord.ui.button(
        label="Previous",
        emoji="◀️",
        style=discord.ButtonStyle.secondary
    )
    async def previous(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        if self.current_page > 0:
            self.current_page -= 1

        self.update_buttons()

        await interaction.response.edit_message(
            embed=self.pages[self.current_page],
            view=self
        )

    @discord.ui.button(
        label="Next",
        emoji="▶️",
        style=discord.ButtonStyle.primary
    )
    async def next(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        if self.current_page < len(self.pages) - 1:
            self.current_page += 1

        self.update_buttons()

        await interaction.response.edit_message(
            embed=self.pages[self.current_page],
            view=self
        )

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True

        if self.message:
            try:
                await self.message.edit(view=self)
            except discord.NotFound:
                pass
class Core(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.started = time.time()

    @app_commands.command(
        name="ping",
        description="Check bot latency"
    )
    async def ping(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            f"🏓 Pong! `{round(self.bot.latency * 1000)}ms`"
        )

    @app_commands.command(
        name="botinfo",
        description="Show bot information"
    )
    async def botinfo(self, interaction: discord.Interaction):

        embed = discord.Embed(
            title="🤖 Bot Information",
            color=discord.Color.blurple()
        )

        embed.add_field(
            name="🐍 Python",
            value=platform.python_version(),
            inline=True
        )

        embed.add_field(
            name="📦 Discord.py",
            value=discord.__version__,
            inline=True
        )

        embed.add_field(
            name="🌐 Servers",
            value=str(len(self.bot.guilds)),
            inline=True
        )

        uptime = int(time.time() - self.started)

        embed.add_field(
            name="⏱️ Uptime",
            value=f"{uptime} seconds",
            inline=True
        )

        await interaction.response.send_message(
            embed=embed
        )

    @app_commands.command(
        name="invite",
        description="Get the bot invite URL"
    )
    async def invite(self, interaction: discord.Interaction):

        client_id = self.bot.user.id

        url = discord.utils.oauth_url(
            client_id,
            permissions=discord.Permissions(
                administrator=True
            )
        )

        await interaction.response.send_message(
            f"🔗 {url}"
        )

    @app_commands.command(
        name="help",
        description="Show all RD Bot commands"
    )
    async def help(self, interaction: discord.Interaction):

        commands_data = []

        # Collect commands from every loaded Cog
        for cog_name, cog in self.bot.cogs.items():

            try:
                cog_commands = cog.get_app_commands()
            except AttributeError:
                continue

            for command in cog_commands:

                # Main command
                commands_data.append(
                    (
                        cog_name,
                        command.qualified_name,
                        command.description or "No description"
                    )
                )

                # Subcommands
                try:
                    for subcommand in command.walk_commands():
                        commands_data.append(
                            (
                                cog_name,
                                subcommand.qualified_name,
                                subcommand.description or "No description"
                            )
                        )
                except AttributeError:
                    pass

        # Remove duplicates
        commands_data = list(dict.fromkeys(commands_data))

        # Sort by category and command
        commands_data.sort(
            key=lambda x: (
                x[0].lower(),
                x[1].lower()
            )
        )

        if not commands_data:

            embed = discord.Embed(
                title="📚 RD Bot — All Commands",
                description="No commands were found.",
                color=discord.Color.blurple()
            )

            return await interaction.response.send_message(
                embed=embed
            )

        # Number of commands per page
        commands_per_page = 12

        pages = []

        for start in range(
            0,
            len(commands_data),
            commands_per_page
        ):

            page_commands = commands_data[
                start:start + commands_per_page
            ]

            embed = discord.Embed(
                title="📚 RD Bot — All Commands",
                description=(
                    "Browse every available command.\n"
                    "Use the buttons below to move through the pages."
                ),
                color=discord.Color.blurple()
            )

            current_category = None
            category_lines = []

            for (
                cog_name,
                command_name,
                description
            ) in page_commands:

                if current_category != cog_name:

                    if category_lines:
                        embed.add_field(
                            name=f"📂 {current_category}",
                            value="\n".join(category_lines),
                            inline=False
                        )

                    current_category = cog_name
                    category_lines = []

                category_lines.append(
                    f"**/{command_name}** — {description}"
                )

            # Add final category
            if category_lines:
                embed.add_field(
                    name=f"📂 {current_category}",
                    value="\n".join(category_lines),
                    inline=False
                )

            page_number = len(pages) + 1

            total_pages = (
                (len(commands_data) + commands_per_page - 1)
                // commands_per_page
            )

            embed.set_footer(
                text=(
                    f"RD Bot • Page {page_number}/{total_pages} "
                    f"• {len(commands_data)} commands"
                )
            )

            pages.append(embed)

        view = HelpView(pages, interaction.user)

        # PUBLIC help message
        await interaction.response.send_message(
    embed=pages[0],
    view=view
)



async def setup(bot):
    await bot.add_cog(Core(bot))
