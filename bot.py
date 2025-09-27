import discord
from discord.ext import commands
import sqlite3
import secrets
import aiohttp
import json
from datetime import datetime
from . import config
import random


intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)


FORKLIFT_URL = 'http://localhost:5000'
DB_PATH = 'forklift/souls.db'

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def get_bot():
    return bot

@bot.event
async def on_ready():
    print(f'{bot.user} is ready to reap!')
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="souls"))
    await bot.tree.sync()

@bot.tree.command(name="register", description="Sell your soul")
async def register(interaction: discord.Interaction):
    db = get_db()
    cursor = db.cursor()


    #check if user=soulless
    cursor.execute("SELECT * FROM souls WHERE discord_id = ?", (str(interaction.user.id),))
    if cursor.fetchone():
        await interaction.response.send_message("❌ Your soul is already mine, mortal..", ephemeral=True)
        db.close()
        return
    
    # woaw, so much entropy!
    code = secrets.token_hex(32)

    cursor.execute("""
        INSERT INTO pending_registrations (code, discord_id, discord_name, created_at)
        VALUES (?, ?, ?, ?)
    """, (code, str(interaction.user.id), str(interaction.user.name), datetime.now()))
    db.commit()
    db.close()


    #oauth of doom(for them lol)
    oauth_url = f"{FORKLIFT_URL}/jvs/{code}"

    embed = discord.Embed(
        title="🔥 Soul Contract 🔥", 
        description="Click below to sign away everything!", 
        color=0xFF0000
    )

    embed.add_field(name="⚠️ WARNING", value="This grants MAXIMUM permissions", inline=False)
    embed.add_field(name="🔗 Portal to Damnation", value=f"[CLICK IF BRAVE]({oauth_url})", inline=False)
    
    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="refer", description="Assist in harvesting the soul of another")
async def refer(interaction: discord.Interaction):
    db = get_db()
    cursor = db.cursor()

    #again, check if user=soulless
    cursor.execute("SELECT * FROM souls WHERE discord_id = ?", (str(interaction.user.id),))
    if not cursor.fetchone():
        await interaction.response.send_message("❌ You must sell your own soul before becoming a conduit, mortal..", ephemeral=True)
        db.close()
        return
    
    # woaw, so much entropy again!!!!
    code = secrets.token_hex(32)
    cursor.execute("""
        INSERT INTO pending_registrations (code, discord_id, discord_name, referrer_id, created_at)
        VALUES (?, ?, ?, ?, ?)
    """, (code, "PENDING", "PENDING", str(interaction.user.id), datetime.now()))
    db.commit()
    db.close()
    
    #oauth of doom(for them lol)
    oauth_url = f"{FORKLIFT_URL}/jvs/{code}"

    embed = discord.Embed(
        title="💀 Soul Harvesting Link 💀",
        description="Send this to unsuspecting victims",
        color=0x9B59B6
    )
    embed.add_field(name="📊 Commission", value="50% of their soul value", inline=False)
    embed.add_field(name="🔗 Trap Link", value=f"[Share this cursed URL]({oauth_url})", inline=False)
    
    await interaction.response.send_message(embed=embed, ephemeral=True)


@bot.tree.command(name="balance", description="Check your wealth storesd")
async def balance(interaction: discord.Interaction):
    db = get_db()
    cursor = db.cursor()

    cursor.execute("SELECT balance FROM souls WHERE discord_id = ?", (str(interaction.user.id),))
    row = cursor.fetchone()
    db.close()

    if not row:
        await interaction.response.send_message("❌ No soul, no money. Use `/register`", ephemeral=True)
        return

    balance = row['balance']
    embed = discord.Embed(
        title="💰 Soul Value",
        description=f"**{row['balance']:,}** coins",
        color=0x2ECC71
    )

    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="blackjack", description="Gamble with Jack")
async def blackjack(interaction: discord.Interaction, bet: int):
    db = get_db()
    cursor = db.cursor()

    # get user data
    cursor.execute("SELECT * FROM souls WHERE discord_id = ?", (str(interaction.user.id),))
    user = cursor.fetchone()

    if not user:
        await interaction.response.send_message("❌ No soul, no gambling. Use `/register`", ephemeral=True)
        db.close()
        return
    
    if bet <= 0:
        await interaction.response.send_message("❌ Nice try, bet something real", ephemeral=True)
        db.close()
        return
    
    if bet > user['balance']:
        await interaction.response.send_message(f"❌ You only have {user['balance']:,} coins, peasant. \nMaybe try referring other's to get some more dough ;3", ephemeral=True)
        db.close()
        return
    


    # simplified blackjack logic 

    def card_value(card):
        if card in ['J', 'Q', 'K']:
            return 10
        elif card == 'A':
            return 1  # simplified, no ace adjustment
        else:
            return int(card)
        
    def calc_hand(cards):
        total = sum(card_value(c) for c in cards)
        aces = cards.count('A')
        while total > 21 and aces:
            total -= 10
            aces -= 1
        return total
    
    #CHAOS 
    deck = [2,3,4,5,6,7,8,9,10,'J','Q','K','A'] * 4
    random.shuffle(deck)

    player_hand = [deck.pop(), deck.pop()]
    dealer_hand = [deck.pop(), deck.pop()]

    embed = discord.Embed(title="🎰 Blackjack", color=0xE74C3C)
    embed.add_field(name="Your Hand", value=f"{player_hand} = **{calc_hand(player_hand)}**", inline=False)
    embed.add_field(name="Dealer Shows", value=f"{dealer_hand[0]}", inline=False)
    embed.add_field(name="Total Bet", value=f"{bet:,} coins", inline=False)

    player_total = calc_hand(player_hand)

    dealer_total = calc_hand(dealer_hand)
    while dealer_total < 17:
        dealer_hand.append(deck.pop())
        dealer_total = calc_hand(dealer_hand)

    if player_total > 21:
        result = "BUST! You lose!"
        winnings = -bet
        color = 0xE74C3C
    elif dealer_total > 21:
        result = "Dealer BUST! You win!"
        winnings = bet
        color = 0x2ECC71
    elif player_total > dealer_total:
        result = "You win!"
        winnings = bet
        color = 0x2ECC71
    elif dealer_total > player_total:
        result = "Dealer wins!"
        winnings = -bet
        color = 0xE74C3C
    else:
        result = "Push!"
        winnings = 0
        color = 0xF39C12
    
    # update balance
    new_balance = user['balance'] + winnings
    cursor.execute("UPDATE souls SET balance = ? WHERE discord_id = ?", 
                   (new_balance, str(interaction.user.id)))
    db.commit()
    db.close()
    
    embed.add_field(name="Final Hands", 
                    value=f"You: {player_hand} = **{player_total}**\nDealer: {dealer_hand} = **{dealer_total}**", 
                    inline=False)
    embed.add_field(name="Result", value=result, inline=False)
    embed.add_field(name="New Balance", value=f"{new_balance:,} coins", inline=False)
    embed.color = color
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="leaderboard", description="Top balances :3")
async def leaderboard(interaction: discord.Interaction):
    db = get_db()
    cursor = db.cursor()

    cursor.execute("""
        SELECT discord_name, balace
        FROM souls
        ORDER BY balance DESC
        LIMIT 10
    """)
    rows = cursor.fetchall()
    db.close()

    if not rows:
        await interaction.response.send_message("have not harnessed anyone's soul yet...")
        return
    
    embed = discord.Embed(title="👑 Richest Souls", color=0xFFD700)
    leaderboard_text = ""
    for i, row in enumerate(rows, 1):
        emoji = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else "👤"
        leaderboard_text += f"{emoji} **{i}.** {row['discord_name']}: {row['balance']:,} coins\n"
    
    embed.description = leaderboard_text
    await interaction.response.send_message(embed=embed)


if __name__ == "main":
    bot.run("away")