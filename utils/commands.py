# ═══════════════════════════════════════════════════════════════
# 📋 utils/commands.py - BOT MENU COMMANDS
# ═══════════════════════════════════════════════════════════════
#
# 📌 KYUN USE HOTA HAI?
#    - Bot ke menu mein commands set karta hai
#    - Different roles ke liye different commands
#    - User / tap kare toh commands dikhte hain
#
# 📌 ROLES:
#    - USER: Basic commands (start, help, about)
#    - ADMIN: Extra commands (stats, broadcast, fsub)
#    - SUPER_ADMIN: All commands + manage admins
# ═══════════════════════════════════════════════════════════════

from pyrogram.types import BotCommand, BotCommandScopeChat, BotCommandScopeDefault
from config import Config
from database.db import db


# ───────────────────────────────────────────────────────────────
# 📋 COMMAND DEFINITIONS
# ───────────────────────────────────────────────────────────────

# 👤 USER COMMANDS - Sabke liye common
USER_COMMANDS = [
    BotCommand("start", "🚀 Start the bot"),
    BotCommand("help", "❓ How to use"),
    BotCommand("about", "ℹ️ About this bot"),
    BotCommand("profile", "👤 View your profile"),
]

# 🛡️ ADMIN COMMANDS - Admins ke liye extra
ADMIN_COMMANDS = USER_COMMANDS + [
    BotCommand("stats", "📊 Bot statistics"),
    BotCommand("broadcast", "📢 Send message to all users"),
    BotCommand("add_fsub", "➕ Add force sub channel"),
    BotCommand("del_fsub", "➖ Remove force sub channel"),
    BotCommand("fsub_list", "📋 List force sub channels"),
    BotCommand("files", "📂 View uploaded files"),
]

# 👑 SUPER ADMIN COMMANDS - Full control
SUPER_ADMIN_COMMANDS = ADMIN_COMMANDS + [
    BotCommand("add_admin", "🛡️ Add new admin"),
    BotCommand("remove_admin", "🛡️ Remove admin"),
    BotCommand("admins", "👥 List all admins"),
    BotCommand("ban", "🚫 Ban a user"),
    BotCommand("unban", "✅ Unban a user"),
    BotCommand("settings", "⚙️ Bot settings"),
    BotCommand("logs", "📜 View recent logs"),
]


# ───────────────────────────────────────────────────────────────
# 🚀 SET BOT COMMANDS
# ───────────────────────────────────────────────────────────────

async def set_bot_commands(client):
    """
    Bot ke menu commands set karta hai
    
    📌 PARAMS:
        client: Pyrogram client instance
    
    📌 LOGIC:
        1. Default commands for all users
        2. Specific commands for each admin
        3. Super admin gets all commands
    
    📌 CALL FROM:
        main.py mein bot start hone par
    """
    try:
        # ───────────────────────────────────────────────────────────
        # STEP 1: Default commands for all users
        # ───────────────────────────────────────────────────────────
        await client.set_bot_commands(
            USER_COMMANDS,
            scope=BotCommandScopeDefault()
        )
        print("✅ Default user commands set")
        
        # ───────────────────────────────────────────────────────────
        # STEP 2: Get all admins from database
        # ───────────────────────────────────────────────────────────
        all_admins = await db.get_all_admins()
        
        # ───────────────────────────────────────────────────────────
        # STEP 3: Set commands for each admin
        # ───────────────────────────────────────────────────────────
        for admin_id in all_admins:
            try:
                if admin_id == Config.SUPER_ADMIN:
                    # Super admin - All commands
                    commands_to_set = SUPER_ADMIN_COMMANDS
                else:
                    # Normal admin - Admin commands
                    commands_to_set = ADMIN_COMMANDS
                
                await client.set_bot_commands(
                    commands_to_set,
                    scope=BotCommandScopeChat(chat_id=admin_id)
                )
                
            except Exception as e:
                print(f"⚠️ Could not set commands for admin {admin_id}: {e}")
        
        print(f"✅ Commands set for {len(all_admins)} admins")
        
    except Exception as e:
        print(f"❌ Error setting bot commands: {e}")


# ───────────────────────────────────────────────────────────────
# 🔄 UPDATE COMMANDS FOR USER
# ───────────────────────────────────────────────────────────────

async def update_user_commands(client, user_id: int, is_admin: bool = False, is_super: bool = False):
    """
    Single user ke commands update karo
    
    📌 PARAMS:
        client: Pyrogram client
        user_id: Telegram user ID
        is_admin: User is admin?
        is_super: User is super admin?
    
    📌 USE CASE:
        - Jab naya admin add ho
        - Jab admin remove ho
    """
    try:
        if is_super:
            commands = SUPER_ADMIN_COMMANDS
        elif is_admin:
            commands = ADMIN_COMMANDS
        else:
            commands = USER_COMMANDS
        
        await client.set_bot_commands(
            commands,
            scope=BotCommandScopeChat(chat_id=user_id)
        )
        print(f"✅ Commands updated for user {user_id}")
        
    except Exception as e:
        print(f"⚠️ Could not update commands for {user_id}: {e}")


# ───────────────────────────────────────────────────────────────
# 🗑️ REMOVE COMMANDS FOR USER
# ───────────────────────────────────────────────────────────────

async def remove_admin_commands(client, user_id: int):
    """
    Admin se admin commands hata do (when demoted)
    
    📌 PARAMS:
        client: Pyrogram client
        user_id: Admin ID to demote
    """
    try:
        # Set user commands (basic)
        await client.set_bot_commands(
            USER_COMMANDS,
            scope=BotCommandScopeChat(chat_id=user_id)
        )
        print(f"✅ Admin commands removed from {user_id}")
        
    except Exception as e:
        print(f"⚠️ Could not remove commands from {user_id}: {e}")


# ───────────────────────────────────────────────────────────────
# 📊 GET COMMANDS INFO
# ───────────────────────────────────────────────────────────────

def get_commands_help() -> str:
    """
    Commands ki help text return karta hai
    
    📌 RETURNS:
        str: Formatted help text
    """
    text = """📋 **Available Commands**

👤 **User Commands:**
• /start - Start the bot
• /help - Get help
• /about - About bot
• /profile - Your profile

"""
    
    text += """🛡️ **Admin Commands:**
• /stats - Bot statistics
• /broadcast - Message all users
• /add_fsub - Add promo channel
• /del_fsub - Remove channel
• /fsub_list - List channels

"""
    
    text += """👑 **Super Admin Commands:**
• /add_admin - Add new admin
• /remove_admin - Remove admin
• /admins - List admins
• /ban - Ban user
• /unban - Unban user
• /settings - Bot settings
• /logs - View logs
"""
    
    return text


# ═══════════════════════════════════════════════════════════════
# ✅ COMMANDS MODULE READY!
#
# 📌 USAGE:
#    from utils.commands import set_bot_commands
#    await set_bot_commands(client)  # Call in main.py
# ═══════════════════════════════════════════════════════════════
