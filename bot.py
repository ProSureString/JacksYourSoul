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


intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)


config = get_config()


def get_db():
    conn = sqlite3.connect("forklift/" + config.DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def get_bot():
    return bot

async def load_cog(cog):
    await bot.add_cog(cog(bot))

async def load_cogs():
    bot.load_extension('blackjack')
    await bot.tree.sync()

def get_cog_choices(self) -> list[str]:
    """
    Returns a list of all cog names currently loaded into the bot
    """
    cog_names = list(self.bot.cogs.keys())
    return cog_names

# @decorator for checking permissions on bot.tree.command
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
    oauth_url = f"{config.FORKLIFT_URL}/jvs/{code}"

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
    oauth_url = f"{config.FORKLIFT_URL}/jvs/{code}"

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
        await interaction.response.send_message("I have not harnessed anyone's souls yet...")
        return
    
    embed = discord.Embed(title="👑 Richest Souls", color=0xFFD700)
    leaderboard_text = ""
    for i, row in enumerate(rows, 1):
        emoji = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else "👤"
        leaderboard_text += f"{emoji} **{i}.** {row['discord_name']}: {row['balance']:,} coins\n"
    
    embed.description = leaderboard_text
    await interaction.response.send_message(embed=embed)



asyncio.run(load_cogs())
bot.run(config.DISCORD_BOT_TOKEN)