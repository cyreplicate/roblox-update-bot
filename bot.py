import discord
from discord.ext import tasks
import aiohttp
import os

TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))

# These are your place IDs
GAME_IDS = [
    "27022845",          # void
    "135059717391268",   # null
    "100793252348239",   # dawn
    "100626662604142",   # zero
    "14430516363"        # test
]

intents = discord.Intents.default()
client = discord.Client(intents=intents)

last_updates = {}

async def get_games_info():
    url = "https://games.roblox.com/v1/games/multiget-place-details?placeIds=" + ",".join(GAME_IDS)
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            return await resp.json()

@tasks.loop(minutes=2)
async def check_updates():
    global last_updates
    channel = client.get_channel(CHANNEL_ID)
    games = await get_games_info()

    # Ensure response is a list
    if not isinstance(games, list):
        print("Roblox API returned unexpected:", games)
        return

    for game in games:
        try:
            place_id = str(game["placeId"])
            updated_time = game["updated"]
            name = game["name"]
        except KeyError:
            continue

        if place_id not in last_updates:
            last_updates[place_id] = updated_time
            continue

        if updated_time != last_updates[place_id]:
            await channel.send(
                f"🎮 **{name}** just updated!\n"
                f"🔗 https://www.roblox.com/games/{place_id}"
            )
            last_updates[place_id] = updated_time

@client.event
async def on_ready():
    print(f"✅ Logged in as {client.user}")
    check_updates.start()

client.run(TOKEN)
