from discord.ext import commands
import discord
from utils.session_managers.roulette_manager import RouletteSessionManager
from games.roulette.roulette import Roulette
import asyncio

from db.database import SessionLocal
from db.models import UserEconomy
from games.bet import Bet

session_manager = RouletteSessionManager()

class RouletteCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def roulette(self, ctx, *, params):        
        try:
            # Handle incorrect command syntax
            usage_text = "Usage: !roulette <amount ('all', 'half', or number)> <bets...>\nExample: !roulette 10 red 24 25"

            tokens = params.split()
            if len(tokens) < 2:
                await ctx.send(usage_text)
                return
            
            user_id = ctx.author.id
            print(f"Playing roulette with {ctx.author}")
            
            with SessionLocal() as session:
                user = session.query(UserEconomy).filter_by(user_id=user_id).first()
                if not user:
                    await ctx.send("You don't have an economy account yet.")
                    return
                
                amount_token = tokens[0].lower()
                if amount_token == "all":
                    bet_amount = int(user.balance)
                elif amount_token == "half":
                    bet_amount = int(user.balance * 0.5)
                elif amount_token.isdigit():
                    bet_amount = int(amount_token)
                else:
                    await ctx.send("Invalid amount. Use 'all', 'half', or a number.")
                    return
                
                bets = tokens[1:]
                if not bets:
                    await ctx.send("You must specify at least one bet.")
                    return
                
                total_bet = bet_amount * len(bets) # total cost of all bets 
                try:
                    user_bet = Bet(user_id, total_bet)
                    user_bet.place()
                except ValueError as e:
                    await ctx.send(str(e))
                    return

                if session_manager.has_session(user_id):
                    await ctx.send(f"{ctx.author.mention} You already have a game in progress!")
                    return

                # Create game with bet information
                game = Roulette(bets, bet_amount)
                session_manager.create_session(user_id, game, user_bet)
                
                # Play the round
                result = game.play_round()
                
                # Handle the game result
                await self.handle_game_result(ctx, result)
                
        except Exception as e:
            print(f"[EXCEPTION] in !roulette: {e}")
            await ctx.send(f"An error occurred: {e}")
    
    async def handle_game_result(self, ctx, result):
        """Handle the roulette game result with structured data"""
        # Handle payout
        bet = session_manager.get_bet(ctx.author.id)
        if bet:
            bet.payout_total(result["total_winnings"])

        # Show spinning animation
        spinning_embed = self.build_spinning_embed(ctx, result)
        message = await ctx.send(embed=spinning_embed)
        await asyncio.sleep(3)

        # Show final result
        result_embed = self.build_result_embed(ctx, result)
        await message.edit(embed=result_embed)

        # Send payout message
        if result["total_winnings"] > 0:
            await ctx.send(f"🎉 {ctx.author.mention} won `${result['total_winnings']}` from roulette!")
        
        session_manager.reset_session(ctx.author.id)
    
    def build_spinning_embed(self, ctx, result):
        """Build the spinning animation embed"""
        embed = discord.Embed(
            title=f"Roulette | {ctx.author.display_name}",
            description=(
                f"🎰 **Spinning the wheel...**\n\n"
                f"**Your Bets:** `{', '.join(result['bets'])}`\n"
                f"**Total Wagered:** `${result['total_bet']}`"
            ),
            color=discord.Color.gold()
        )
        embed.set_footer(text="Good Luck!")
        return embed
    
    def build_result_embed(self, ctx, result):
        """Build the final result embed"""
        embed = discord.Embed(
            title=f"🎰 Roulette | {ctx.author.display_name}",
            description=(
                f"{result['outcome_message']}\n\n"
                f"🎯 **Spin Result:** `{result['spin_display']}`\n\n"
                f"💰 **Payout:** `${result['total_winnings']}`\n"
            ),
            color=result['embed_color']
        )
        
        embed.set_footer(text="Thanks for playing roulette!")
        return embed
    
    @roulette.error
    async def roulette_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            usage_text = "Usage: !roulette <amount ('all', 'half', or number)> <bets...>\nExample: !roulette 10 red 24 25"
            await ctx.send(usage_text)
        else:
            print(f"[ERROR in !roulette] {error}")
            await ctx.send("An unexpected error occurred.")

async def setup(bot):
    await bot.add_cog(RouletteCog(bot))