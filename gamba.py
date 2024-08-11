import discord
import datetime
import random
from blackjack import Blackjack

class blackjack_buttons(discord.ui.View):
    def __init__(self, *, game, bet, cnx, embed, ctx, timeout=180):
        super().__init__(timeout=timeout)
        self.game = game
        self.bet = bet
        self.cnx = cnx
        self.ctx = ctx
        self.embed = embed
    
    def winner(self):
        cursor = self.cnx.cursor()

        if (self.game.player['total'] == self.game.dealer['total'] or (self.game.player['total'] >21 and self.game.dealer['total'] > 21)):
            self.embed.add_field(name = 'Draw', value = 'GC returned', inline = False)
        elif(self.game.player['total'] > self.game.dealer['total']):
            cursor.execute('UPDATE gamba SET gamba_coins = gamba_coins + %s WHERE id = %s', [self.bet, self.ctx.author.id])
            self.cnx.commit()
            self.embed.add_field(name = 'PLAYER WINS', value = f'+{self.bet} GC', inline = False)
        else:
            cursor.execute('UPDATE gamba SET gamba_coins = gamba_coins - %s WHERE id = %s', [self.bet, self.ctx.author.id])
            self.cnx.commit()
            self.embed.add_field(name = 'DEALER WINS', value = f'-{self.bet} GC', inline = False)

        cursor.close()

    @discord.ui.button(label="Hit",style=discord.ButtonStyle.green)
    async def hit_button(self, interaction:discord.Interaction, button:discord.ui.Button):
        if (not self.game.state):
            button.disabled = True
            return
        self.game.play('hit')
        self.embed.clear_fields()
        if(self.game.state):
            self.embed.add_field(name = 'Dealer Cards', value = f'X {self.game.dealer['cards'][1]}', inline = False)
        else:
            self.embed.add_field(name = 'Dealer Cards', value = ' '.join([card for card in self.game.dealer['cards']]), inline = False)
        self.embed.add_field(name = 'Your Cards', value = ' '.join([card for card in self.game.player['cards']]), inline = False)
        if(not self.game.state):
            self.winner()
            button.disabled = True
        await interaction.response.edit_message(embed = self.embed, view = self)
    
    @discord.ui.button(label="Stand",style=discord.ButtonStyle.red)
    async def stand_button(self, interaction:discord.Interaction, button:discord.ui.Button):
        if (not self.game.state):
            button.disabled = True
            return
        self.game.play('stand')
        self.embed.clear_fields()
        self.embed.add_field(name = 'Dealer Cards', value = ' '.join([card for card in self.game.dealer['cards']]), inline = False)
        self.embed.add_field(name = 'Your Cards', value = ' '.join([card for card in self.game.player['cards']]), inline = False)
        if(not self.game.state):
            self.winner()
            button.disabled = True
        await interaction.response.edit_message(embed=self.embed, view = self)

async def register(ctx, cnx):
    avatar = ctx.author.display_avatar

    cursor = cnx.cursor()
    cursor.execute("SELECT * FROM gamba WHERE id = %s", [str(ctx.author.id)])
    registration = cursor.fetchone()

    if registration:
        embed = discord.Embed(title = f'User already registered', colour = discord.Colour.blue())
        embed.set_author(name = ctx.author.display_name, icon_url = avatar)
        embed.add_field(name = 'Balance', value = str(registration[1]) + ' GC')
    else:
        cursor.execute("INSERT INTO gamba (id, gamba_coins, last_claimed) VALUES (%s, %s, %s)", (str(ctx.author.id), 50, datetime.datetime.today().strftime('%Y-%m-%d %H:%M:%S')))
        cnx.commit()
        embed = discord.Embed(title = f'User registered', colour = discord.Colour.blue())
        embed.set_author(name = ctx.author.display_name, icon_url = avatar)
        embed.add_field(name = 'Balance', value = '50 GC')
    
    cursor.close()
    await ctx.reply(embed = embed)


async def balance(ctx, cnx):
    registration = await user_exists(ctx, cnx)

    if registration:
        avatar = ctx.author.display_avatar
        embed = discord.Embed(title = f'Balance', colour = discord.Colour.blue())
        embed.set_author(name = ctx.author.display_name, icon_url = avatar)
        embed.add_field(name = '', value = str(registration[1]) + ' GC')
        await ctx.reply(embed = embed)


async def claim(ctx, cnx):
    registration = await user_exists(ctx, cnx)

    if registration:
        avatar = ctx.author.display_avatar
        embed = discord.Embed(title = 'Daily GC Claim', colour = discord.Colour.blue())
        embed.set_author(name = ctx.author.display_name, icon_url = avatar)

        last_claimed = registration[2]
        elapsed = datetime.datetime.now() - last_claimed

        if elapsed > datetime.timedelta(hours = 24):
            cursor = cnx.cursor()
            cursor.execute('UPDATE gamba SET gamba_coins = gamba_coins + 50 WHERE id = %s', [str(ctx.author.id)])
            cnx.commit()
            cursor.close()
            
            embed.add_field(name = '', value = '+50 GC')
        else:
            wait = datetime.timedelta(hours = 24) - elapsed
            embed.add_field(name = '', value = f'Please wait {str(wait)[:-7]}')

        await ctx.reply(embed = embed)


async def coinflip(ctx, cnx, amount):
    registration = await user_exists(ctx, cnx)

    if registration:
        avatar = ctx.author.display_avatar
        embed = discord.Embed(title = 'Coinflip', colour = discord.Colour.blue())
        embed.set_author(name = ctx.author.display_name, icon_url = avatar)

        if (int(amount) > registration[1]):
            embed.add_field(name = '', value = 'Not enough GC')
        else:
            cursor = cnx.cursor()
            if(random.choice([True, False])):
                cursor.execute('UPDATE gamba SET gamba_coins = gamba_coins + %s WHERE id = %s', [amount, ctx.author.id])
                embed.add_field(name = '', value = f'+{amount} GC')
            else: 
                cursor.execute('UPDATE gamba SET gamba_coins = gamba_coins - %s WHERE id = %s', [amount, ctx.author.id])
                embed.add_field(name = '', value = f'-{amount} GC')
            cnx.commit()
            cursor.close()
        await ctx.reply(embed = embed)

async def user_exists(ctx, cnx):
    cursor = cnx.cursor()
    cursor.execute("SELECT * FROM gamba WHERE id = %s", [str(ctx.author.id)])
    registration = cursor.fetchone()
    if not registration:
        avatar = ctx.author.display_avatar
        embed = discord.Embed(title = 'User not registered', colour = discord.Colour.blue())
        embed.set_author(name = ctx.author.display_name, icon_url = avatar)
        embed.add_field(name = '', value = 'Use !register to register for gamba')
        await ctx.reply(embed = embed)
    cursor.close()
    return registration

async def blackjack(ctx, cnx, bet):
    avatar = ctx.author.display_avatar
    game = Blackjack()
    game.deal()
    embed = discord.Embed(title = 'Blackjack', colour = discord.Colour.blue())
    embed.set_author(name = ctx.author.display_name, icon_url = avatar)
    embed.add_field(name = 'Dealer Cards', value = 'X ' + game.dealer['cards'][1], inline = False)
    embed.add_field(name = 'Your Cards', value = ' '.join([card for card in game.player['cards']]))
    await ctx.reply(embed = embed, view = blackjack_buttons(game = game, bet = bet, cnx = cnx, embed = embed, ctx = ctx))

