import discord 
from discord.ext import commands 
import logging 
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()
token = os.getenv("DISCORD_TOKEN")

handler = logging.FileHandler(filename="discord.log", encoding="utf-8", mode="w")
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f"we are ready to go in, {bot.user}")

@bot.command()
async def hello(ctx):
    await ctx.send(f"Hello {ctx.author.mention}!")

# ✅ Use an async setup function to load cogs
async def main():
    async with bot:
        await bot.load_extension("cogs.economy")
        await bot.load_extension("cogs.blackjack")
        await bot.load_extension("cogs.roulette")
        await bot.start(token)

import asyncio

# Start the bot
if __name__ == "__main__":
    asyncio.run(main())

