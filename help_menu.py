import discord

CATEGORIES = {
    "📋 All Commands": [
        "/help — Open this command center"
    ],
    "🎂 Birthday": [
        "/birthday set", "/birthday view", "/birthday remove"
    ],
    "👥 Community": [
        "/poll", "/announce", "/membercount"
    ],
    "ℹ️ Core": [
        "/ping", "/botinfo", "/invite", "/help"
    ],
    "💰 Economy": [
        "/balance", "/daily", "/work", "/pay", "/leaderboard"
    ],
    "🎮 Fun": [
        "/8ball", "/coinflip", "/roll", "/choose", "/ship"
    ],
    "🎉 Giveaway": [
        "/giveaway start", "/giveaway end", "/giveaway reroll"
    ],
    "🔨 Join To Create": [
        "/jtc setup", "/jtc disable"
    ],
    "📊 Leveling": [
        "/rank", "/levels", "/setlevel"
    ],
    "🔎 Logging": [
        "/logging set", "/logging disable"
    ],
    "🛡️ Moderation": [
        "/ban", "/kick", "/timeout", "/warn", "/warnings", "/clear"
    ],
    "🎵 Music": [
        "/play", "/pause", "/resume", "/skip", "/queue", "/stop"
    ],
    "🔎 Reactionroles": [
        "/reactionrole panel"
    ],
    "🔎 Search": [
        "/search"
    ],
    "🔎 Server Stats": [
        "/serverstats", "/channelstats", "/membercount"
    ],
    "🎟️ Ticket": [
        "/ticket panel", "/ticket close"
    ],
    "🛠️ Tools": [
        "/avatar", "/userinfo", "/servericon", "/poll", "/say"
    ],
    "🔧 Utility": [
        "/remind", "/afk", "/serverinfo"
    ],
    "✅ Verification": [
        "/verification setup", "/verification disable"
    ],
    "👋 Welcome": [
        "/welcome set", "/welcome disable"
    ],
}


class CategorySelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(
                label=name.split(" ", 1)[1],
                emoji=name.split(" ", 1)[0],
                value=name
            )
            for name in CATEGORIES
        ]
        super().__init__(
            placeholder="Select to view the commands",
            min_values=1,
            max_values=1,
            options=options
        )

    async def callback(self, interaction: discord.Interaction):
        category = self.values[0]
        commands = CATEGORIES[category]
        embed = discord.Embed(
            title=category,
            description="\n".join(f"• `{cmd}`" for cmd in commands),
            color=discord.Color.blurple()
        )
        embed.set_footer(text="Use /help to return to the category browser.")
        await interaction.response.edit_message(embed=embed, view=HelpView())


class HelpView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=180)
        self.add_item(CategorySelect())
