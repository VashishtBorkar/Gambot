from discord.ext import commands
import discord
from utils.session_managers.blackjack_manager import BlackjackSessionManager
from games.blackjack.blackjack import Blackjack

from db.database import SessionLocal
from db.models import UserEconomy
from games.bet import Bet

session_manager = BlackjackSessionManager()

class BlackjackView(discord.ui.View):
    def __init__(self, ctx, cog):
        super().__init__(timeout=120)
        self.ctx = ctx
        self.cog = cog
        self.message = None

        game = session_manager.get_game(ctx.author.id)
        if game.can_double_down():
            self.add_item(self.DoubleDownButton())

    class DoubleDownButton(discord.ui.Button):
        def __init__(self):
            super().__init__(label="Double Down", style=discord.ButtonStyle.success)

        async def callback(self, interaction: discord.Interaction):
            view = self.view
            game = session_manager.get_game(view.ctx.author.id)

            if not game.can_double_down():
                await interaction.response.send_message("You can't double down right now.", ephemeral=True)
                return

            bet = session_manager.get_bet(view.ctx.author.id)
            try:
                bet.double()
            except ValueError as e:
                await interaction.response.send_message(str(e), ephemeral=True)
                return

            result = game.double_down()
            await view.cog.finalize_game(interaction, view.ctx, game, result, view)


    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.ctx.author.id:
            await interaction.response.send_message("This isn't your game!", ephemeral=True)
            return False
        return True
    
    async def on_timeout(self):
        self.disable_all_items()
        session_manager.reset_session(self.ctx.author.id)

        try:
            if self.message:
                await self.message.edit(view=self)

            await self.ctx.send(f"{self.ctx.author.mention}, your Blackjack game timed out due to inactivity.")
        except Exception as e:
            print(f"Error during timeout handling: {e}")

    @discord.ui.button(label="Hit", style=discord.ButtonStyle.primary)
    async def hit(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            game = session_manager.get_game(self.ctx.author.id)
            result = game.hit()

            if result in ("blackjack", "dealer", "player", "push"):
                await self.cog.finalize_game(interaction, self.ctx, game, result, self)
            else: # continue
                embed = self.cog.build_embed(self.ctx, game)
                await interaction.response.edit_message(embed=embed, view=self)

        except Exception as e:
            await interaction.response.send_message(f"Error: {e}", ephemeral=True) 

    @discord.ui.button(label="Stay", style=discord.ButtonStyle.secondary)
    async def stay(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            game = session_manager.get_game(self.ctx.author.id)
            result = game.stay()
            await self.cog.finalize_game(interaction, self.ctx, game, result, self)

        except Exception as e:
            await interaction.response.send_message(f"Error: {e}", ephemeral=True)

    def disable_all_items(self):
        for item in self.children:
            item.disabled = True

class BlackjackCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    async def handle_payout(self, ctx, result):
        bet = session_manager.get_bet(ctx.author.id)
        if not bet:
            return 0
        
        if result == "player":
            winnings = bet.payout(multiplier=2)
        elif result == "blackjack":
            winnings = bet.payout(multiplier=2.5)
        elif result == "push":
            winnings = bet.payout(multiplier=1)
        else:
            winnings = 0

        return winnings
    
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
            outcome_text = {
                "dealer": "💥 Dealer wins!",
                "player": "🎉 You win!",
                "blackjack": "Blackjack!",
                "push": "🤝 Push!",
            }.get(result, "Game Over!")
            embed.description = f"{outcome_text}"

        embed.add_field(
            name="Your hand",
            value=f"{game.player}\nValue: {game.player.get_total()}",
            inline=False
        )

        embed.add_field(
            name="Dealer hand",
            value=f"{game.dealer}\nValue: {game.dealer.get_total()}",
            inline=False
        )

        return embed
    
    async def finalize_game(self, interaction, ctx, game, result, view=None):
        winnings = await self.handle_payout(ctx, result)
        session_manager.reset_session(ctx.author.id)

        embed = self.build_embed(ctx, game, result)
        await interaction.response.edit_message(embed=embed, view=None)

        if winnings > 0:
            await ctx.send(f"💰{ctx.author.mention} You won `${int(winnings)}` from blackjack!")

        if view:
            view.stop()

    @commands.command()
    async def blackjack(self, ctx, bet: str = None):
        try:
            if not bet:
                await ctx.send("Usage: !blackjack <all | half | bet_amount>")
                return 

            user_id = ctx.author.id
            print(f"Playing blackjack with {ctx.author}")

            # Handle betting amount
            with SessionLocal() as session:
                user = session.query(UserEconomy).filter_by(user_id=user_id).first()
                if not user:
                    await ctx.send("You don't have an economy account yet.")
                    return

                if bet.isdigit():
                    bet_amount = int(bet)
                elif bet.lower() == "all":
                    bet_amount = user.balance
                elif bet.lower() == "half":
                    bet_amount = 0.5 * user.balance
                else:
                    await ctx.send("Specified an invalid amount.")
                    return

                try:
                    user_bet = Bet(user_id, bet_amount)
                    user_bet.place()
                except ValueError as e:
                    await ctx.send(str(e))
                    return

            if session_manager.has_session(user_id):
                game = session_manager.get_game(user_id)
                embed = self.build_embed(ctx, game)
                view = BlackjackView(ctx, self)
                msg = await ctx.send(f"{ctx.author.mention} You already have a game in progress!", embed=embed, view=view)
                view.message = msg
                return

            # Create game and session
            
            session_manager.create_session(user_id, Blackjack(), user_bet)
            game = session_manager.get_game(user_id)
            result = game.deal_hand()
            
            embed = self.build_embed(ctx, game, result if result != "continue" else None)
            view = None

            if result == "continue":
                embed = self.build_embed(ctx, game)
                view = BlackjackView(ctx, self)
                msg = await ctx.send(embed=embed, view=view)
                view.message = msg
            else:
                await self.finalize_game(ctx, ctx, game, result)

        except Exception as e:
            print(f"[EXCEPTION] in !blackjack: {e}")
            await ctx.send(f"An error occurred: {e}")

async def setup(bot):
    await bot.add_cog(BlackjackCog(bot))
