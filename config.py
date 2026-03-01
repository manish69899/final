# ═══════════════════════════════════════════════════════════════
# ⚙️ config.py - BOT CONFIGURATION SETTINGS
# ═══════════════════════════════════════════════════════════════
#
# 📌 KYUN USE HOTA HAI?
#    - Saare settings ek jagah centralized rakhne ke liye
#    - .env file se values load karta hai
#    - Dusri files se direct .env access karne ki zaroorat nahi
#
# 📌 KAISE USE HOTA HAI?
#    from config import Config
#    print(Config.BOT_TOKEN)
# ═══════════════════════════════════════════════════════════════

import os
from dotenv import load_dotenv

# .env file load karo
load_dotenv()

class Config:
    """
    ═══════════════════════════════════════════════════════════
    📋 CONFIGURATION CLASS
    ═══════════════════════════════════════════════════════════
    Ye class saare settings hold karti hai.
    .env file se values read karti hai.
    ═══════════════════════════════════════════════════════════
    """
    
    # ───────────────────────────────────────────────────────────
    # 🤖 TELEGRAM API CREDENTIALS
    # ───────────────────────────────────────────────────────────
    # API_ID: Telegram se milta hai (integer format)
    API_ID = int(os.getenv("API_ID", "0"))
    
    # API_HASH: 32 character secret hash
    API_HASH = os.getenv("API_HASH", "")
    
    # BOT_TOKEN: BotFather se milta hai
    BOT_TOKEN = os.getenv("BOT_TOKEN", "")
    
    # ───────────────────────────────────────────────────────────
    # 👑 ADMIN CONFIGURATION
    # ───────────────────────────────────────────────────────────
    # SUPER_ADMIN: Bot owner - Full access to everything
    # Is admin ko koi remove nahi kar sakta
    SUPER_ADMIN = int(os.getenv("SUPER_ADMIN", "0"))
    
    # ADMINS: List of admin IDs (comma separated in .env)
    # Ye admins files upload kar sakte hain, stats dekh sakte hain
    # But ye SUPER_ADMIN ko manage nahi kar sakte
    ADMINS = [int(x.strip()) for x in os.getenv("ADMINS", "").split(",") if x.strip()]
    
    # ───────────────────────────────────────────────────────────
    # 💾 DATABASE
    # ───────────────────────────────────────────────────────────
    # DB_NAME: SQLite database file ka naam
    # Yahan saare users, files, settings store honge
    DB_NAME = "bot_database.db"
    
    # ───────────────────────────────────────────────────────────
    # 📢 CHANNELS
    # ───────────────────────────────────────────────────────────
    # LOG_CHANNEL_ID: Jahan activities log hongi
    # - New user joined
    # - File uploaded
    # - Admin actions
    LOG_CHANNEL_ID = int(os.getenv("LOG_CHANNEL_ID", "0"))
    
    # FORCE_SUB_CHANNEL: Users ko join karna padega
    # 0 = Force sub disabled
    FORCE_SUB_CHANNEL = int(os.getenv("FORCE_SUB_CHANNEL", "0"))
    
    # ───────────────────────────────────────────────────────────
    # ⏰ AUTO DELETE SETTINGS
    # ───────────────────────────────────────────────────────────
    # AUTO_DELETE_HOURS: Kitne hours baad files delete hongi
    # 0 = Auto delete disabled
    # 24 = 24 hours baad delete
    AUTO_DELETE_HOURS = int(os.getenv("AUTO_DELETE_HOURS", "0"))
    
    # ───────────────────────────────────────────────────────────
    # 💸 SHORTENER SETTINGS (Revenue Generation)
    # ───────────────────────────────────────────────────────────
    # SHORTENERS: List of shortener services
    # Har user ko round-robin mein alag shortener milega
    # Isse revenue evenly distribute hoti hai
    SHORTENERS = []
    
    # First shortener
    domain_1 = os.getenv("SHORTENER_DOMAIN_1", "")
    api_1 = os.getenv("SHORTENER_API_1", "")
    if domain_1 and api_1:
        SHORTENERS.append({"domain": domain_1, "api_key": api_1})
    
    # Second shortener
    domain_2 = os.getenv("SHORTENER_DOMAIN_2", "")
    api_2 = os.getenv("SHORTENER_API_2", "")
    if domain_2 and api_2:
        SHORTENERS.append({"domain": domain_2, "api_key": api_2})

    # Third shortener
    domain_3 = os.getenv("SHORTENER_DOMAIN_3", "")
    api_3 = os.getenv("SHORTENER_API_3", "")
    if domain_3 and api_3:
        SHORTENERS.append({"domain": domain_3, "api_key": api_3})

    # Fourth shortener
    domain_4 = os.getenv("SHORTENER_DOMAIN_4", "")
    api_4 = os.getenv("SHORTENER_API_4", "")
    if domain_4 and api_4:
        SHORTENERS.append({"domain": domain_4, "api_key": api_4})

    # Fifth shortener
    domain_5 = os.getenv("SHORTENER_DOMAIN_5", "")
    api_5 = os.getenv("SHORTENER_API_5", "")
    if domain_5 and api_5:
        SHORTENERS.append({"domain": domain_5, "api_key": api_5})
    
    # ───────────────────────────────────────────────────────────
    # 🎨 BOT MESSAGES
    # ───────────────────────────────────────────────────────────
    # WELCOME_MESSAGE: Naye user ko dikhayi dega
    WELCOME_MESSAGE = """
👋 **Welcome {name}!**

Main ek **File Sharing Bot** hoon.

📂 Files download karne ke liye mujhe links bhejo.

✨ Features:
• Fast & Secure Downloads
• 24/7 Available

💡 **Commands:**
/start - Bot start karein
/help - Madad lein
/about - Bot ke baare mein

⚠️ **Note:** Kuch files ke liye aapko channel join karna padega.
"""
    
    # HELP_MESSAGE: /help command ke liye
    HELP_MESSAGE = """
📚 **Help Section**

**🔹 User Commands:**
/start - Bot start karein
/help - Ye help message
/about - Bot info
/profile - Apni profile dekho

**🆘 Need Help?**
Contact: @coolegeyqbot
"""

    # ABOUT_MESSAGE: /about command ke liye
    ABOUT_MESSAGE = """
ℹ️ **About Devloper**

ʟᴏᴄᴀʟʜᴏꜱᴛ.exe
Real Identity: ARYAN

Made by Localhost.
Not hosted. Not owned. Just deployed.
Built in silence.
Tested in chaos.
Deployed with caffeine.

Half lazy. Half genius.
Full power mode when it matters.

This bot isn’t just code.
It’s late night debugging sessions,
random idea explosions,
and that one stubborn bug that refused to die.

Minimal outside.
Savage inside.

If it works smoothly… respect the architecture.
If it breaks… it’s a feature in development 😌

Welcome to the system.
Stay sharp. Stay smart. Stay slightly dangerous. ⚡

"""


# ───────────────────────────────────────────────────────────────
# 🔒 HELPER FUNCTIONS
# ───────────────────────────────────────────────────────────────

def is_super_admin(user_id: int) -> bool:
    """
    Check karta hai ki user SUPER_ADMIN hai ya nahi
    
    📌 PARAMS:
        user_id: Telegram user ID (integer)
    
    📌 RETURNS:
        True: agar super admin hai
        False: agar nahi hai
    
    📌 USAGE:
        if is_super_admin(user.id):
            # Super admin access
    """
    return user_id == Config.SUPER_ADMIN


def is_admin(user_id: int) -> bool:
    """
    Check karta hai ki user ADMIN hai ya nahi
    (Super Admin bhi admin hota hai)
    
    📌 PARAMS:
        user_id: Telegram user ID (integer)
    
    📌 RETURNS:
        True: agar admin hai ya super admin hai
        False: agar nahi hai
    """
    return user_id in Config.ADMINS or user_id == Config.SUPER_ADMIN


# ═══════════════════════════════════════════════════════════════
# ✅ CONFIG READY!
# Ab dusri files se import karo: from config import Config
# ═══════════════════════════════════════════════════════════════