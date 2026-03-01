# ═══════════════════════════════════════════════════════════════
# 🚀 main.py - BOT STARTING POINT
# ═══════════════════════════════════════════════════════════════
#
# 📌 KYUN USE HOTA HAI?
#    - Ye file BOT ko start karti hai
#    - Database initialize karti hai
#    - Scheduler start karti hai (auto delete ke liye)
#    - Bot ko online state mein rakhti hai
#
# 📌 KAISE CHALAYE?
#    python main.py
# ═══════════════════════════════════════════════════════════════

import asyncio
from pyrogram import Client, idle
from config import Config
from database.db import db
from utils.commands import set_bot_commands
from utils.auto_delete import start_auto_delete_scheduler
from utils.keep_alive import keep_alive

# ───────────────────────────────────────────────────────────────
# 🤖 BOT CLIENT CREATE
# ───────────────────────────────────────────────────────────────
# Client: Ye main bot instance hai
# plugins dict: Batata hai ki plugins folder kahan hai

app = Client(
    "FileBot",  # Session file ka naam (FileBot.session banega)
    api_id=Config.API_ID,
    api_hash=Config.API_HASH,
    bot_token=Config.BOT_TOKEN,
    plugins=dict(root="plugins")  # Plugins folder auto-load hoga
)


async def main():
    """
    ═══════════════════════════════════════════════════════════
    🎯 MAIN FUNCTION - YE SABSE PEHLE CHALTA HAI
    ═══════════════════════════════════════════════════════════
    
    Flow:
    1. Database initialize (tables create)
    2. Bot start (Telegram se connect)
    3. Bot commands set (menu buttons)
    4. Auto delete scheduler start
    5. Idle state (bot chalta rahe)
    ═══════════════════════════════════════════════════════════
    """
    
    print("=" * 50)
    print("🚀 BOT STARTING...")
    print("=" * 50)
    
    # ───────────────────────────────────────────────────────────
    # STEP 1: DATABASE INITIALIZE
    # ───────────────────────────────────────────────────────────
    # Tables create karega agar exist nahi karti
    print("🗄️ Initializing Database...")
    await db.init()
    print("✅ Database Ready!")

    # ───────────────────────────────────────────────────────────
    # STEP 1.5: START WEB SERVER FOR RENDER (KEEP ALIVE)
    # ───────────────────────────────────────────────────────────
    print("🌐 Starting Keep-Alive Web Server...")
    keep_alive()
    print("✅ Web Server Running!")
    
    # ───────────────────────────────────────────────────────────
    # STEP 2: BOT START
    # ───────────────────────────────────────────────────────────
    # Telegram servers se connect karega
    print("🤖 Connecting to Telegram...")
    await app.start()
    print("✅ Bot Connected!")
    
    # ───────────────────────────────────────────────────────────
    # STEP 3: SET BOT COMMANDS (MENU)
    # ───────────────────────────────────────────────────────────
    # Users jab bot open karenge, menu mein commands dikhenge
    print("📋 Setting Bot Menu...")
    await set_bot_commands(app)
    print("✅ Menu Ready!")
    
    # ───────────────────────────────────────────────────────────
    # STEP 4: START AUTO DELETE SCHEDULER
    # ───────────────────────────────────────────────────────────
    # Agar auto delete enabled hai toh scheduler start karo
    if Config.AUTO_DELETE_HOURS > 0:
        print(f"⏰ Starting Auto Delete Scheduler ({Config.AUTO_DELETE_HOURS} hours)...")
        await start_auto_delete_scheduler()
        print("✅ Scheduler Started!")
    
    # ───────────────────────────────────────────────────────────
    # STEP 5: BOT INFO PRINT
    # ───────────────────────────────────────────────────────────
    me = await app.get_me()
    print("=" * 50)
    print(f"🤖 BOT ONLINE!")
    print(f"   Username: @{me.username}")
    print(f"   Name: {me.first_name}")
    print(f"   ID: {me.id}")
    print("=" * 50)
    print("🔔 Waiting for messages...")
    print("=" * 50)
    
    # ───────────────────────────────────────────────────────────
    # STEP 6: IDLE STATE
    # ───────────────────────────────────────────────────────────
    # Bot ko chalta rahega jab tak manually stop na karo
    # Ctrl+C se stop kar sakte ho
    await idle()
    
    # ───────────────────────────────────────────────────────────
    # CLEANUP (Jab bot stop ho)
    # ───────────────────────────────────────────────────────────
    print("🛑 Bot Stopping...")
    await app.stop()
    print("👋 Bot Stopped!")


# ───────────────────────────────────────────────────────────────
# 🏃 RUN KARO!
# ───────────────────────────────────────────────────────────────
# Ye line script ko run karti hai
if __name__ == "__main__":
    # Event loop create karo aur main function run karo
    loop = asyncio.get_event_loop_policy().get_event_loop()
    loop.run_until_complete(main())


# ═══════════════════════════════════════════════════════════════
# 📌 IMPORTANT NOTES:
#
# 1. BOT KO STOP KARNE KE LIYE: Ctrl+C dabao
# 2. BOT KO RESTART KARNE KE LIYE: python main.py dobara chalao
# 3. SESSION FILE: FileBot.session naam ki file banegi
#    - Ye file delete mat karo, warna bot dobara login karega
# ═══════════════════════════════════════════════════════════════