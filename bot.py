import discord
import asyncio
import a2s
import os
from discord.ext import tasks

# ── Настройки через переменные окружения ──────────────────────────────
BOT_TOKEN        = os.environ["BOT_TOKEN"]
SERVER_IP        = os.environ["SERVER_IP"]
SERVER_PORT      = int(os.environ.get("SERVER_PORT", "7777"))
UPDATE_INTERVAL  = int(os.environ.get("UPDATE_INTERVAL", "30"))
# ─────────────────────────────────────────────────────────────────────

intents = discord.Intents.default()
client  = discord.Client(intents=intents)

def get_server_info():
    try:
        info = a2s.info((SERVER_IP, SERVER_PORT), timeout=5)
        return info.player_count, info.max_players, True
    except Exception:
        return 0, 0, False

@tasks.loop(seconds=UPDATE_INTERVAL)
async def update_status():
    players, max_players, online = get_server_info()

    if online:
        activity = discord.CustomActivity(name=f"{players} / {max_players} Онлайна")
        status   = discord.Status.online if players > 0 else discord.Status.idle
    else:
        activity = discord.CustomActivity(name="Сервер недоступен 🔴")
        status   = discord.Status.do_not_disturb

    await client.change_presence(status=status, activity=activity)
    print(f"[Статус] {'🟢' if online else '🔴'} {players}/{max_players}")

@update_status.before_loop
async def before_update():
    await client.wait_until_ready()

@client.event
async def on_ready():
    print(f"✅ Бот запущен: {client.user}")
    update_status.start()

client.run(BOT_TOKEN)
