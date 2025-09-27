import random
import discord
from discord import app_commands
from discord.ext import commands
from discord.ui import View, Button, Modal, TextInput
import asyncio

from bot import get_db

SUITS = {
    'Hearts': '❤️',
    'Diamonds': '♦️',
    'Clubs': '♣️',
    'Spades': '♠️'
}

RANKS = {
    '2': 2, '3': 3, '4': 4, '5': 5, '6': 6,
    '7': 7, '8': 8, '9': 9, '10': 10,
    'J': 10, 'Q': 10, 'K': 10, 'A': 11
}


class BlackjackCog(commands.Cog, name="Blackjack"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.active_games = dict[int, BlackjackSession] = {}

    def get_bot(self):
        return self.bot

    @get_bot.tree.command(name="blackjack", description="Gamble with Jack")
    async def blackjack(self, interaction: discord.Interaction):
        if interaction.user.id in self.active_games:
            await interaction.response.send_message("You're already in a game, mortal...", ephemeral=True)
            return
        
        await interaction.response.send_modal(BetModal(self))

    async def cog_unload(self):
        self.active_games.clear()
        return await super().cog_unload()
    
class BlackjackSession:
    """state store, per blackjack game, per user"""
    def __init__(self, user_id: int, bet: int):
        self.user_id = user_id
        self.bet = bet
        self.deck = self._make_deck()
        random.shuffle(self.deck)

        self.player_hand = []
        self.dealer_hand = []

        self.player_hand.append(self.deck.pop())
        self.player_hand.append(self.deck.pop())
        self.dealer_hand.append(self.deck.pop())
        self.dealer_hand.append(self.deck.pop())

        self.finished = False

    def _make_deck(self):
        deck = []
        for suit in SUITS:
            for rank in RANKS:
                deck.append((rank, suit))
        return deck
    
    def hand_value(self, hand):
        total = sum(RANKS[rank] for (rank, _) in hand)
        aces = sum(1 for (rank, _) in hand if rank == 'A')

        while total > 21 and aces > 0:
            total -= 10
            aces -= 1
        return total
    
    def player_value(self):
        return self.hand_value(self.player_hand)
    
    def dealer_value(self):
        return self.hand_value(self.dealer_hand)
    
    def format_hand(self, hand):
        return " ".join(f"{rank}{SUITS[suit]}" for rank, suit in hand)
    
    def dealer_play(self):
        while self.dealer_value < 17:
            self.dealer_hand.append(self.deck.pop())

    def is_player_bust(self):
        return self.player_value() > 21
    
    def is_dealer_bust(self):
        return self.dealer_value() > 21
    
    def outcome(self):
        pv = self.player_value()
        dv = self.dealer_value()
        if pv > 21:
            return ("Bust - you lose.", -self.bet)
        if dv > 21:
            return ("Dealer busts - you win!", self.bet)
        if pv > dv:
            return ("You win!", self.bet)
        if dv > pv:
            return ("Dealer wins!", -self.bet)
        return ("Push ( tie )", 0)
    
class BetModal(Modal, title="Place your bet"):
    def __init__(self, cog: BlackjackCog):
        super().__init__()
        self.cog = cog

    bet = TextInput(
        label="How many coins will you bet?",
        placeholder="e.x. 100",
        required=True,
        max_length=12
    )

    async def on_submit(self, interaction: discord.Interaction):
        try:
            bet_amt = int(self.bet.value)
        except ValueError:
            await interaction.response.send_message("bet must be an integer :3", ephemeral=True)
            return
        
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM souls WHERE discord_id = ?", (str(interaction.user.id)))
        user = cursor.fetchone()
        db.close()

        if not user:
            await interaction.response.send_message("You need to sell your soul to me first, mortal..")
            return
        
        balance = user['balance']
        if bet_amt <= 0:
            await interaction.response.send_message(f"The bet must be positive, mortal..", ephemeral=True)
            return
        if bet_amt > balance:
            await interaction.response.send_message(f"You only posses {balance:,} coins, mortal..", ephemeral=True)
            return


        session = BlackjackSession(interaction.user.id, bet_amt)
        self.cog.active_games[interaction.user.id] = session
        embed = discord.Embed(title="🃏 Blackjack", color=0xE74C3C)
        embed.add_field(
            name="Your Hand",
            value=f"{session.format_hand(session.player_hand)} = **{session.player_value()}**",
            inline=False
        )
        d0 = session.dealer_hand[0]
        embed.add_field(
            name="Dealer Shows",
            value=f"{d0[0[{SUITS[d0[1]]}]]}"
        )
        embed.add_field(name="Bet", value=f"{bet_amt:,} coins", inline=False)

        view = BlackjackView(self.cog) #~~view,modal,session,button~~ done, imrportaed 
        await interaction.response.send_message(embed=embed, view=view)

class BlackjackView(View):
    def __init__(self, cog: BlackjackCog, timeout: float = 180):
        super().__init__(timeout=timeout)
        self.cog = cog

    @Button(label="Hit", style=discord.ButtonStyle.primary, custom_id="bj_hit")
    async def hit(self, interaction: discord.Interaction, button: Button):
        session = self.cog.active_games.get(interaction.user.id)
        if not session or session.finished:
            await interaction.response.send_message("These(?) games reais inactive, mortal...")
            return
        
        session.player_hand.append(session.deck.pop())

        if session.is_player_bust():
            session.finished = True
            session.dealer_play()
            result, net = session.outcome()
        else:
            result, net = None, None 

        #redo update mebed
        embed = discord.Embed(title="🃏 Blackjack", color=0xE74C3C)
        embed.add_field(
            name="Your Hand",
            value=f"{session.format_hand(session.player_hand)} = **{session.player_value()}**",
            inline=False
        )
        d0 = session.dealer_hand[0]
        embed.add_field(
            name="Dealer Shows",
            value=f"{d0[0[{SUITS[d0[1]]}]]}"
        )
        embed.add_field(name="Bet", value=f"{session.bet:,} coins", inline=False)

        if result is not None:
            #finalize
            session.finished = True
            session.dealer_play()
            result, net = session.outcome()

            db = get_db()
            cursor = db.cursor()
            cursor.execute("SELECT * FROM souls WHERE discord_id = ?", (str(interaction.user.id),)) 
            user = cursor.fetchone() 
            new_bal = user['balance'] + net #:3
            cursor.execute("UPDATE souls SET balance = ? WHERE discord_id = ?", (new_bal, str(interaction.user.id)))
            db.commit()
            db.close()

            embed.add_field(
                name="Dealer Hand",
                value=f"{session.format_hand(session.dealer_hand)} = **{session.dealer_value}**",
                inline=False
            )
            embed.add_field(name="Result", value=f"{result} coins", inline=False)
            embed.add_field(name="New Balance", value=f"{new_bal:,} coins", inline=False)
            

            if net > 0:
                embed.color = 0x2ECC71
            elif net < 0:
                embed.color = 0xE74C3C
            else:
                embed.color = 0xF39C12

            for child in self.children:
                child.disabled = True

            await interaction.response.edit_message(embed=embed, view=self)

            #clean up like a good boy after finishing :3
            self.cog.active_games.pop(interaction.user.id, None) #no, kat, this function is cleaning up the gane by removing it from the list of active games and reducing ram usage 
        else:
            await interaction.response.edit_message(embed=embed, view=self)

    @Button(label="Stand", style=discord.ButtonStyle.secondary, custom_id="bj_stand")
    async def stand(self, interaction: discord.Interaction, button: Button):
        cog: BlackjackCog =interaction.client.get_cog("BlackjackCog")
        session = cog.active_games.get(interaction.user.id)
        if not session or session.finished:
            await interaction.response.send_message("These(?) games reais inactive, mortal...")
            return
        
        session.finshed = True
        session.dealer_play()
        result, net = session.outcome()

        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM souls WHERE discord_id = ?", (str(interaction.user.id),))
        user = cursor.fetchone()
        new_bal = user['balance'] + net
        cursor.execute("UPDATE * FROM souls WHERE discord_id = ?", (str(interaction.user.id),))
        db.commit()
        db.close()

        embed = discord.Embed(title="🃏 Blackjack", color=0xE74C3C)
        embed.add_field(
            name="Your Hand",
            value=f"{session.format_hand(session.player_hand)} = **{session.player.value()}**",
            inline=False
        )
        embed.add_field(
            name="Dealer Hand",
            value=f"{session.format_hand(session.dealer_hand)} = **{session.dealer_value()}**",
            inline=False
        )
        embed.add_field(name="Bet", value=f"{session.bet:,} coins", inline=False)
        embed.add_field(name="Result", value=f"{result} coins", inline=False)
        embed.add_field(name="New Balance", value=f"{new_bal:,} coins", inline=False)

        if net > 0:
            embed.color = 0x2ECC71
        elif net < 0:
            embed.color = 0xE74C3C
        else:
            embed.color = 0xF39C12
        
        for child in self.children:
            child.disabled = True

        await interaction.response.edit_message(embed=embed, view=self)
        cog.active_games.pop(interaction.user.id, None)

    async def on_timeout(self):
        return await super().on_timeout()# do mroe later im too lazy rn i need to finish this and sleep, autocomplete says this should work


    
async def setup(bot: commands.Bot):
    await bot.add_cog(BlackjackCog(bot))