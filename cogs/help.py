from discord.ext import commands
import discord

class HelpCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        # Mapping of command names to descriptions
        self.commands_info = {
            "blackjack": {
                "description": "Play a game of blackjack against the dealer.",
                "usage": "!blackjack <bet_amount>",
                "rules": (
                    "**Blackjack Rules:**\n"
                    "- Try to get as close to 21 as possible without going over.\n"
                    "- You start with 2 cards. `Hit` draws another card, or `Stand` ends your turn.\n"
                    "- `Double Down` to double your bet and receive only one more card (only allowed on your first move) and end your turn.\n"
                    "- Aces can count as 1 or 11.\n"
                    "- Face cards (J, Q, K) count as 10."
                )
            },
            "roulette": {
                "description": "Bet on a number or color in roulette.",
                "usage": "!roulette <amount> <bets>",
                "rules": (
                    "**Roulette Rules:**\n"
                    "- Choose numbers (0-36) or colors (red/black) to bet on.\n"
                    "- You can place multiple bets in one command.\n"
                    "- Example: `!roulette 100 red 7 20`\n"
                    "- Payouts: 1:1 for color, 35:1 for number, etc."
                )
            },
            # Add more game commands here
        }

    @commands.command(name="help")
    async def help_command(self, ctx, *, command_name: str = None):
        """
        Shows general or specific help.
        Usage:
        - !help → shows all commands
        - !help blackjack → shows help for blackjack
        """
        if command_name:
            cmd = command_name.lower()
            if cmd in self.commands_info:
                info = self.commands_info[cmd]
                embed = discord.Embed(
                    title=f"Help: {cmd.capitalize()}",
                    description=info["description"],
                    color=discord.Color.blurple()
                )
                embed.add_field(name="Usage", value=info["usage"], inline=False)
                embed.add_field(name="How to Play", value=info["rules"], inline=False)
                await ctx.send(embed=embed)
                return
            else:
                await ctx.send(f"No help found for `{command_name}`.")
                return

        # General help
        embed = discord.Embed(
            title="Available Commands",
            description="Use `!help <command>` to get more info about a specific game.",
            color=discord.Color.green()
        )
        for name, info in self.commands_info.items():
            embed.add_field(name=f"!{name}", value=info["description"], inline=False)

        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(HelpCog(bot))
