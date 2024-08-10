import discord
from discord.ext import commands
import random
import datetime
import mysql.connector
import json

auth = json.load(open('auth.json'))
cnx = mysql.connector.connect(user = auth['sql_user'], password = auth['sql_pass'], host = auth['sql_host'], database = 'discord')
cursor = cnx.cursor()

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')

@bot.command()
async def knot(ctx):
    print('check')
    roll = random.randint(0, 100)
    print(roll)
    if(roll <= 95):
        image = 'knot1.png'
        await ctx.channel.send('Wrong one, try again!')
    elif(roll > 95 < 99):
        image = 'knot2.png'
        await ctx.channel.send('Close, but not quite. Try again!')
    else: 
        image = 'knot3.png'
        await ctx.channel.send('This is punishment for your hubris, fool')

    with open(f'images/{image}', 'rb') as f:
        picture = discord.File(f)
        await ctx.channel.send(file=picture)

@bot.command()
async def coinflip(ctx, amount: int):
    pass

@bot.command()
async def register(ctx):
    avatar = ctx.author.display_avatar
    print(avatar)
    embed = discord.Embed(title = f'Register', colour = discord.Colour.blue())
    embed.set_author(name = ctx.author.display_name, icon_url = avatar)
    cursor.execute("SELECT * FROM gamba WHERE id = %s", [str(ctx.author.id)])
    registration = cursor.fetchone()
    if registration:
        embed.add_field(name = 'Result', value = 'User already registered')
        embed.add_field(name = 'Balance', value = registration[1])
    else:
        cursor.execute("INSERT INTO gamba (id, gamba_coins, last_claimed) VALUES (%s, %s, %s)", (str(ctx.author.id), 50, datetime.datetime.today().strftime('%Y-%m-%d %H:%M:%S')))
        cnx.commit()
        embed.add_field(name = 'Result', value = 'User registered!')
        embed.add_field(name = 'Balance', value = '50')
    await ctx.channel.send(embed = embed)


bot.run(auth['token'])