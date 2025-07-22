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
            await view.cog.handle_game_result(interaction, view.ctx, result, view)

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
            await self.cog.handle_game_result(interaction, self.ctx, result, self)
        except Exception as e:
            await interaction.response.send_message(f"Error: {e}", ephemeral=True) 

    @discord.ui.button(label="Stay", style=discord.ButtonStyle.secondary)
    async def stay(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            game = session_manager.get_game(self.ctx.author.id)
            result = game.stay()
            await self.cog.handle_game_result(interaction, self.ctx, result, self)
        except Exception as e:
            await interaction.response.send_message(f"Error: {e}", ephemeral=True)

    def disable_all_items(self):
        for item in self.children:
            item.disabled = True

class BlackjackCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    def build_embed(self, ctx, game_state):
        """Build Discord embed from game state"""
        color = (
            discord.Color.green() if game_state["outcome"] == "player_wins"
            else discord.Color.red() if game_state["outcome"] == "dealer_wins"
            else discord.Color.gold() if game_state["outcome"] == "blackjack"
            else discord.Color.blurple()
        )

        embed = discord.Embed(
            title=f"Blackjack | {ctx.author.display_name}",
            color=color
        )

        if game_state["game_over"]:
            embed.description = game_state["message"]

        embed.add_field(
            name="Your hand",
            value=f"{game_state['player_display']}\nValue: {game_state['player_total']}",
            inline=False
        )

        embed.add_field(
            name="Dealer hand",
            value=f"{game_state['dealer_display']}\nValue: {game_state['dealer_total']}",
            inline=False
        )

        return embed
    
    async def handle_game_result(self, interaction, ctx, result, view=None):
        """Handle the result of a game action"""
        if result["game_over"]:
            # Game is finished, handle payout and cleanup
            winnings = result["payout"]
            session_manager.reset_session(ctx.author.id)

            embed = self.build_embed(ctx, result)
            await interaction.response.edit_message(embed=embed, view=None)

            if winnings > 0:
                await ctx.send(f"💰{ctx.author.mention} You won ${int(winnings)} from blackjack!")

            if view:
                view.stop()
        else:
            # Game continues, update the view
            embed = self.build_embed(ctx, result)
            await interaction.response.edit_message(embed=embed, view=view)

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
                    bet_amount = int(0.5 * user.balance)
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
                game_state = game.get_game_state()
                embed = self.build_embed(ctx, game_state)
                view = BlackjackView(ctx, self)
                msg = await ctx.send(f"{ctx.author.mention} You already have a game in progress!", embed=embed, view=view)
                view.message = msg
                return

            # Create game and session
            game = Blackjack(bet_amount)
            session_manager.create_session(user_id, game, user_bet)
            
            result = game.deal_hand()
            
            if result["game_over"]:
                await self.handle_game_result(None, ctx, result)
                # For initial deal, we need to send a message instead of editing
                embed = self.build_embed(ctx, result)
                await ctx.send(embed=embed)
                
                if result["payout"] > 0:
                    await ctx.send(f"💰{ctx.author.mention} You won ${int(result['payout'])} from blackjack!")
                
                session_manager.reset_session(user_id)
            else:
                embed = self.build_embed(ctx, result)
                view = BlackjackView(ctx, self)
                msg = await ctx.send(embed=embed, view=view)
                view.message = msg

        except Exception as e:
            print(f"[EXCEPTION] in !blackjack: {e}")
            await ctx.send(f"An error occurred: {e}")

async def setup(bot):
    await bot.add_cog(BlackjackCog(bot))