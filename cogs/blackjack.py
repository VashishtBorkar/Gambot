from discord.ext import commands
import discord
from utils.session_manager import get_blackjack_session, reset_blackjack_session

class BlackjackView(discord.ui.View):
    def __init__(self, ctx, build_embed, reset_session):
        super().__init__(timeout=60)
        self.ctx = ctx
        self.build_embed = build_embed
        self.reset_session = reset_session

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.ctx.author.id:
            await interaction.response.send_message("This isn't your game!", ephemeral=True)
            return False
        return True

    @discord.ui.button(label="Hit", style=discord.ButtonStyle.primary)
    async def hit(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            game = get_blackjack_session(self.ctx.author.id)
            result = game.hit()

            if result in ("dealer", "player", "push"):
                embed = self.build_embed(self.ctx, game, result)
                self.reset_session(self.ctx.author.id)
                await interaction.response.edit_message(embed=embed, view=None)
                return  # exit early to avoid sending a second message


            embed = self.build_embed(self.ctx, game, result if result != "continue" else None)
            await interaction.response.edit_message(embed=embed, view=self)

        except Exception as e:
            await interaction.response.send_message(f"Error: {e}", ephemeral=True) 

    @discord.ui.button(label="Stay", style=discord.ButtonStyle.secondary)
    async def stay(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            game = get_blackjack_session(self.ctx.author.id)
            result = game.stay()
            
            embed = self.build_embed(self.ctx, game, result)
            self.reset_session(self.ctx.author.id)
            await interaction.response.edit_message(embed=embed, view=None)
            return  # exit early to avoid sending a second message


            embed = self.build_embed(self.ctx, game, result)
            await interaction.response.edit_message(embed=embed, view=self)
        except Exception as e:
            await interaction.response.send_message(f"Error: {e}", ephemeral=True)

    def disable_all_items(self):
        for item in self.children:
            item.disabled = True

class BlackjackCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    def handle_result(self, result):
        if result == "dealer":
            return "💥 Dealer wins!"
        elif result == "player":
            return "🎉 You win!"
        elif result == "draw":
            return "🤝 It's a tie!"
        return None # For "continue" or unrecognized result
    
    def build_embed(self, ctx, game, result=None):
        color = (
            discord.Color.green() if result == "player"
            else discord.Color.red() if result == "dealer"
            else discord.Color.blurple()
        )

        embed = discord.Embed(
            title=f"Blackjack | {ctx.author.display_name}",
            color=color
        )

        if result:
            msg = {
                "dealer": "💥 Dealer wins!",
                "player": "🎉 You win!",
                "push": "🤝 Push!"
            }.get(result, "")
            embed.description = msg

        embed.add_field(
            name="Your hand",
            value=f"{game.player}\nValue: {game.player.get_total()}",
            inline=True
        )

        embed.add_field(
            name="Dealer hand",
            value=f"{game.dealer}\nValue: {game.dealer.get_total()}",
            inline=True
        )

        return embed
    
    @commands.command()
    async def blackjack(self, ctx):
        game = get_blackjack_session(ctx.author.id)
        game.reset()

        result = game.deal_hand()

        embed = self.build_embed(ctx, game, result if result != "continue" else None)

        if result != "continue":
            reset_blackjack_session(ctx.author.id)
            view = None
        else:
            view = BlackjackView(ctx, self.build_embed, reset_blackjack_session)

        await ctx.send(embed=embed, view=view)

async def setup(bot):
    await bot.add_cog(BlackjackCog(bot))
