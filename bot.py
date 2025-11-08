import discord
from discord.ext import tasks
import aiohttp
import asyncio
import os

# --- SETTINGS ---
TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))

# Multiple Roblox game IDs
GAME_IDS = [
    "27022845",          # void
    "135059717391268",   # null
    "100793252348239",   # dawn
    "100626662604142"    # zero
]

# --- DISCORD CLIENT SETUP ---
intents = discord.Intents.default()
client = discord.Client(intents=intents)

# Store the last known update times
last_updates = {}

async def get_games_info():
    """Fetch Roblox game data for all IDs"""
    url = f"https://games.roblox.com/v1/games?universeIds={','.join(GAME_IDS)}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            data = await resp.json()
            return data["data"]

@tasks.loop(minutes=2)
async def check_updates():
    """Check every 2 minutes for updates"""
    global last_updates
    games = await get_games_info()
    channel = client.get_channel(CHANNEL_ID)

    for game in games:
        game_id = str(game["id"])
        updated_time = game["updated"]

        # If first time seeing this game, store timestamp and skip
        if game_id not in last_updates:
            last_updates[game_id] = updated_time
            continue

        # If the game updated since last check, send message
        if updated_time != last_updates[game_id]:
            await channel.send(
                f"🎮 **{game['name']}** just updated!\n"
                f"🔗 https://www.roblox.com/games/{game['rootPlaceId']}"
            )
            last_updates[game_id] = updated_time

@client.event
async def on_ready():
    print(f"✅ Logged in as {client.user}")
    check_updates.start()

client.run(TOKEN)
