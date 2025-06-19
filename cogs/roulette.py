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

                session_manager.create_session(user_id, Roulette(), user_bet)
                game = session_manager.get_game(user_id)
                
                total_winnings = game.play_round(bets, bet_amount)

                await self.finalize_game(
                    ctx,
                    bets, # list of all of the roulette choices the user made
                    total_bet, # total amount of money bet
                    total_winnings, # total amount of money won
                )
                
        except Exception as e:
            print(f"[EXCEPTION] in !roulette: {e}")
    
    async def handle_payout(self, ctx, total_winnings):
        print("handling payout")
        bet = session_manager.get_bet(ctx.author.id)
        if not bet:
            return 0
        
        return bet.payout_total(total_winnings)
    
    async def finalize_game(self, ctx, roulette_choices, total_bet, total_winnings):
        game = session_manager.get_game(ctx.author.id)
        await self.handle_payout(ctx, total_winnings)

        spinning_embed = self.build_spinning_embed(ctx, roulette_choices, total_bet)
        message = await ctx.send(embed=spinning_embed)
        await asyncio.sleep(3)

        spin_number, spin_color = game.get_spin()
        result_embed = self.build_result_embed(ctx, roulette_choices, total_bet, total_winnings, spin_number, spin_color)
        await message.edit(embed=result_embed)

        if total_winnings > 0:
            await ctx.send(f"🎉 {ctx.author.mention} won `${total_winnings}` from roulette!")
        # net_gain = total_winnings - total_bet
        # if net_gain > 0:
        #     await ctx.send(f"🎉 {ctx.author.mention} won `${net_gain}` from roulette!")
        # elif net_gain < 0:
        #     await ctx.send(f"😢 {ctx.author.mention} lost `${abs(net_gain)}`.")
        # else:
        #     await ctx.send(f"⚖️ {ctx.author.mention} broke even.")
        
        session_manager.reset_session(ctx.author.id)
    
    def build_spinning_embed(self, ctx, bets, total_bet):
        embed = discord.Embed(
            title=f"Roulette | {ctx.author.display_name}",
            description=(
                f"🎰 **Spinning the wheel...**\n\n"
                f"**Your Bets:** `{', '.join(bets)}`\n"
                f"**Total Wagered:** `${total_bet}`"
            ),
            color=discord.Color.gold()
        )
        embed.set_footer(text="Good Luck!")
        return embed
    
    def build_result_embed(self, ctx, bets, total_bet, total_winnings, spin_number, spin_color):
        color_map = {
            "red": "🔴",
            "black": "⚫",
            "green": "🟢"
        }

        emoji = color_map.get(spin_color, spin_color)
        net_gain = total_winnings - total_bet

        win_status = ""
        if net_gain > 0:
            win_status = "🤑 You won!"
            embed_color = discord.Color.green()
        elif net_gain < 0:
            win_status = "❌ You lost."
            embed_color = discord.Color.red()
        else:
            win_status = "⚖️ You broke even."
            embed_color = discord.Color.blurple()
        
        description=(
            f"{win_status}\n\n"
            f"🎯 **Spin Result:** `{spin_number} {emoji}`\n\n"
            f"💰 **Payout:** `${total_winnings}`\n"
        )
        embed = discord.Embed(
            title=f"🎰 Roulette | {ctx.author.display_name}",
            description=description,
            color=embed_color
        )

        # embed.add_field(name="Spin Result", value=f"`{spin_number} {emoji}`", inline=False)
        # embed.add_field(name="Payout", value=f"`{total_winnings}`", inline=True)
        # embed.add_field(name="Outcome", value=win_status, inline=True)
        
        embed.set_footer(text="Thanks for playing roulette!")
        return embed
    
    @roulette.error
    async def roulette_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            usage_text = "Usage: !roulette <bet type (\"!roulette options\" for bet choices)> <all | half | bet_amount>"
            await ctx.send(usage_text)
        else:
            print(f"[ERROR in !roulette] {error}")
            await ctx.send("An unexpected error occurred.")

async def setup(bot):
    await bot.add_cog(RouletteCog(bot))