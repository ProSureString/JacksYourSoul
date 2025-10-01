import discord
from discord.ext import commands
import sqlite3
import secrets
import aiohttp
import asyncio
import json
from datetime import datetime
from forklift.config import get_config
import random
from typing import *
from functools import wraps

# boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys boys

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)

config = get_config()

def get_db():
    conn = sqlite3.connect("forklift/" + config.DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def get_bot():
    return bot

async def load_cogs():
    await bot.load_extension('blackjack') #TODO: fix dependency weirdness n stuff like make a cogs folder and cogs commands

def get_cog_choices() -> list[str]:
    cog_names = list(bot.cogs.keys())
    return cog_names

async def check_permissions(interaction: discord.Interaction) -> bool:
    return interaction.user.id == config.OWNER_ID

def owner_only():
    def decorator(func):
        @discord.app_commands.check
        @wraps(func)
        async def predicate(interaction: discord.Interaction):
            return check_permissions(interaction)
        return func
    return decorator

@bot.event
async def on_ready():
    print(f'{bot.user} is ready to reap!')
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="souls"))
    await load_cogs()
    await bot.tree.sync()

#TODO: use components v2 or something
@bot.tree.command(name="register", description="Sell your boys")
async def register(interaction: discord.Interaction):
    db = get_db()
    cursor = db.cursor()

    #check if user=soulless
    cursor.execute("SELECT * FROM souls WHERE discord_id = ?", (str(interaction.user.id),))
    if cursor.fetchone():
        await interaction.response.send_message("❌ Your heart is already mine, you cute lil boy..", ephemeral=True)
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
    oauth_url = f"{config.FORKLIFT_URL}/jvs/{code}"

    embed = discord.Embed(
        title="🔥 Boys Contract 🔥", 
        description="Click below to kiss boys!", 
        color=0xFF0000
    )

    embed.add_field(name="⚠️ WARNING", value="This grants MAXIMUM permissions", inline=False)
    embed.add_field(name="🔗 Portal to boykisser land", value=f"[CLICK IF BRAVE]({oauth_url})", inline=False)
    
    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="refer", description="Assist in harvesting the kisses of another")
async def refer(interaction: discord.Interaction):
    db = get_db()
    cursor = db.cursor()

    #again, check if user=soulless
    cursor.execute("SELECT * FROM souls WHERE discord_id = ?", (str(interaction.user.id),))
    if not cursor.fetchone():
        await interaction.response.send_message("❌ You must kiss your own boy before kissing other boys, you cute lil boy..", ephemeral=True)
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
    oauth_url = f"{config.FORKLIFT_URL}/jvs/{code}"

    embed = discord.Embed(
        title="💀 Boy Kissing  Link 💀",
        description="Send this to kissable boys",
        color=0x9B59B6
    )
    embed.add_field(name="📊 Commission", value="50% of their kisses", inline=False)
    embed.add_field(name="🔗 Boy Link", value=f"[Share this cursed URL]({oauth_url})", inline=False)
    
    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="balance", description="Check your kisses storesd")
async def balance(interaction: discord.Interaction):
    db = get_db()
    cursor = db.cursor()

    cursor.execute("SELECT balance FROM souls WHERE discord_id = ?", (str(interaction.user.id),))
    row = cursor.fetchone()
    db.close()

    if not row:
        await interaction.response.send_message("❌ No boys, no kisses. Use `/register`", ephemeral=True)
        return

    balance = row['balance']
    embed = discord.Embed(
        title="💰 Boy Value",
        description=f"**{row['balance']:,}** kisses",
        color=0x2ECC71
    )

    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="leaderboard", description="Top boys :3")
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
        await interaction.response.send_message("I have not kisses any boys yet...")
        return
    
    embed = discord.Embed(title="👑 Richest Boys", color=0xFFD700)
    leaderboard_text = ""
    for i, row in enumerate(rows, 1):
        emoji = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else "👤"
        leaderboard_text += f"{emoji} **{i}.** {row['discord_name']}: {row['balance']:,} kisses\n"
    
    embed.description = leaderboard_text
    await interaction.response.send_message(embed=embed)

bot.run(config.DISCORD_BOT_TOKEN)