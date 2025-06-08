import discord 
from discord.ext import commands 
import logging 

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
    print(f"we are ready to go in, {bot.username}")

@bot.event
async def on_message(message):
    if message == bot.user:
        return
    
    if "secret word" in message.content.lower():
        await message.delete()
        await message.channel.send(f"{message.author.mention} - Hush! Don't say that")
    
    await bot.process_commands(message)

@bot.command()
async def hello(ctx):
    await ctx.send(f"Hello {ctx.author.mention}!")

@bot.command()
async def blackjack(ctx):
    await ctx.send(f"Time to play blackjack, {ctx.author.mention}!")

@bot.command()
async def stay(ctx):
    result = game.


bot.run(token, log_handler=handler, log_level=logging.DEBUG)

