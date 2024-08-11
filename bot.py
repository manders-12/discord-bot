import discord
from discord.ext import commands
import random
import datetime
import mysql.connector
import json
import gamba

auth = json.load(open('auth.json'))
cnx = mysql.connector.connect(user = auth['sql_user'], password = auth['sql_pass'], host = auth['sql_host'], database = 'discord')

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')

@bot.command()
async def knot(ctx):
    roll = random.randint(0, 100)
    if(roll <= 95):
        image = 'knot1.png'
        await ctx.channel.send('Wrong one, try again!')
    elif(roll > 95 < 99):
        image = 'knot2.png'
        await ctx.channel.send('Close, but not quite. Try again!')
    else: 
        image = 'knot3.png'
        await ctx.channel.send(':)')

    with open(f'images/{image}', 'rb') as f:
        picture = discord.File(f)
        await ctx.channel.send(file=picture)

@bot.command()
async def register(ctx):
    await gamba.register(ctx, cnx)

@bot.command()
async def balance(ctx):
    await gamba.balance(ctx, cnx)

@bot.command()
async def claim(ctx):
    await gamba.claim(ctx, cnx)

@bot.command()
async def coinflip(ctx, amount):
    await gamba.coinflip(ctx, cnx, amount)

@bot.command()
async def blackjack(ctx, bet):
    await gamba.blackjack(ctx, cnx, bet)

bot.run(auth['token'])