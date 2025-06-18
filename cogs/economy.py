import discord
from discord.ext import commands
from db.database import SessionLocal
from db.models import UserEconomy

class EconomyCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="leaderboard")
    async def show_top_balances(self, ctx):
        with SessionLocal() as session:
            top_users = (
                session.query(UserEconomy)
                .order_by(UserEconomy.balance.desc())
                .limit(10)
                .all()
            )

            if not top_users:
                await ctx.send("No users found in the economy database.")
                return

            embed = discord.Embed(
                title="🏆 Richest Players",
                color=discord.Color.gold()
            )

            for i, user in enumerate(top_users, start=1):
                member = ctx.guild.get_member(int(user.user_id))
                name = member.display_name if member else f"User ID {user.user_id}"
                embed.add_field(name=f"{i}. {name}", value=f"💰 {user.balance}", inline=False)

            await ctx.send(embed=embed)
    @commands.command(name="bal")
    async def check_balance(self, ctx):
        user_id = str(ctx.author.id)
        with SessionLocal() as session:
            user = session.query(UserEconomy).filter_by(user_id=user_id).first()
            if not user:
                # Create new user with default balance
                user = UserEconomy(user_id=user_id, balance=1000)
                session.add(user)
                session.commit()
            
            await ctx.send(f"{ctx.author.mention}, your balance is 💰 {user.balance}.")
async def setup(bot):
    await bot.add_cog(EconomyCog(bot))
