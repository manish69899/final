# ═══════════════════════════════════════════════════════════════
# 👑 plugins/superadmin.py - SUPER ADMIN COMMANDS
# ═══════════════════════════════════════════════════════════════
#
# 📌 KYUN USE HOTA HAI?
#    - Super admin specific commands
#    - Manage admins, ban users, bot settings
#
# 📌 COMMANDS:
#    /add_admin - Add new admin
#    /remove_admin - Remove admin
#    /admins - List all admins
#    /ban - Ban user
#    /unban - Unban user
#    /settings - Bot settings
# ═══════════════════════════════════════════════════════════════

from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from config import Config
from database.db import db
from utils.keyboard import (
    superadmin_manage_admins_keyboard,
    superadmin_settings_keyboard,
    confirm_keyboard
)
from utils.logger import log_admin_added, log_admin_removed, log_user_banned, log_user_unbanned
from utils.commands import update_user_commands, remove_admin_commands


# ═══════════════════════════════════════════════════════════════
# 🛡️ ADMIN MANAGEMENT
# ═══════════════════════════════════════════════════════════════

@Client.on_message(filters.command("add_admin") & filters.private)
async def add_admin_handler(client: Client, message: Message):
    """
    /add_admin - Naya admin add karo
    
    📌 USAGE:
        /add_admin 123456789
    
    📌 PERMISSION:
        Only SUPER_ADMIN can use this
    """
    user_id = message.from_user.id
    
    # Only super admin
    if user_id != Config.SUPER_ADMIN:
        await message.reply_text("👑 Ye command sirf Super Admin use kar sakta hai.")
        return
    
    if len(message.command) != 2:
        await message.reply_text(
            "❌ **Usage:** `/add_admin USER_ID`\n\n"
            "**How to get User ID:**\n"
            "1. User ko message forward karo\n"
            "2. Ya @userinfobot se ID lo"
        )
        return
    
    try:
        new_admin_id = int(message.command[1])
        
        # Can't add super admin again
        if new_admin_id == Config.SUPER_ADMIN:
            await message.reply_text("⚠️ Ye toh Super Admin hai!")
            return
        
        # Check if already admin
        if await db.is_admin(new_admin_id):
            await message.reply_text("⚠️ Ye user already admin hai.")
            return
        
        # Add to database
        await db.add_admin(new_admin_id, user_id)
        
        # Update commands for new admin
        await update_user_commands(client, new_admin_id, is_admin=True)
        
        # Log
        await log_admin_added(client, new_admin_id, user_id)
        
        await message.reply_text(
            f"✅ **Admin Added!**\n\n"
            f"🆔 **User ID:** `{new_admin_id}`\n\n"
            f"Ab ye user bot ko admin ki tarah use kar sakta hai."
        )
        
    except ValueError:
        await message.reply_text("❌ User ID number hona chahiye.")


@Client.on_message(filters.command("remove_admin") & filters.private)
async def remove_admin_handler(client: Client, message: Message):
    """
    /remove_admin - Admin remove karo
    """
    user_id = message.from_user.id
    
    # Only super admin
    if user_id != Config.SUPER_ADMIN:
        await message.reply_text("👑 Ye command sirf Super Admin use kar sakta hai.")
        return
    
    if len(message.command) != 2:
        await message.reply_text("❌ **Usage:** `/remove_admin USER_ID`")
        return
    
    try:
        admin_id = int(message.command[1])
        
        # Can't remove super admin
        if admin_id == Config.SUPER_ADMIN:
            await message.reply_text("⚠️ Super Admin ko remove nahi kar sakte!")
            return
        
        # Check if admin
        if not await db.is_admin(admin_id):
            await message.reply_text("⚠️ Ye user admin nahi hai.")
            return
        
        # Remove from database
        await db.remove_admin(admin_id)
        
        # Update commands (remove admin commands)
        await remove_admin_commands(client, admin_id)
        
        # Log
        await log_admin_removed(client, admin_id, user_id)
        
        await message.reply_text(
            f"🗑️ **Admin Removed!**\n\n"
            f"🆔 **User ID:** `{admin_id}`\n\n"
            f"Ab ye user normal user hai."
        )
        
    except ValueError:
        await message.reply_text("❌ User ID number hona chahiye.")


@Client.on_message(filters.command("admins") & filters.private)
async def list_admins_handler(client: Client, message: Message):
    """
    /admins - Saare admins ki list
    """
    user_id = message.from_user.id
    
    # Only super admin
    if user_id != Config.SUPER_ADMIN:
        await message.reply_text("👑 Ye command sirf Super Admin use kar sakta hai.")
        return
    
    # Get all admins
    admins = await db.get_all_admins()
    
    if not admins:
        await message.reply_text("📭 No admins found.")
        return
    
    text = "👥 **Admin List**\n\n"
    
    for admin_id in admins:
        if admin_id == Config.SUPER_ADMIN:
            text += f"👑 **SUPER ADMIN:** `{admin_id}`\n"
        else:
            text += f"🛡️ **Admin:** `{admin_id}`\n"
    
    await message.reply_text(text)


# ═══════════════════════════════════════════════════════════════
# 🚫 USER BAN MANAGEMENT
# ═══════════════════════════════════════════════════════════════

@Client.on_message(filters.command("ban") & filters.private)
async def ban_user_handler(client: Client, message: Message):
    """
    /ban - User ko ban karo
    
    📌 USAGE:
        /ban USER_ID Reason
    """
    user_id = message.from_user.id
    
    # Only super admin
    if user_id != Config.SUPER_ADMIN:
        await message.reply_text("👑 Ye command sirf Super Admin use kar sakta hai.")
        return
    
    if len(message.command) < 2:
        await message.reply_text("❌ **Usage:** `/ban USER_ID Reason`")
        return
    
    try:
        ban_user_id = int(message.command[1])
        reason = " ".join(message.command[2:]) or "No reason provided"
        
        # Can't ban super admin
        if ban_user_id == Config.SUPER_ADMIN:
            await message.reply_text("⚠️ Super Admin ko ban nahi kar sakte!")
            return
        
        # Ban user
        await db.ban_user(ban_user_id, reason)
        
        # Log
        await log_user_banned(client, ban_user_id, "User", reason, user_id)
        
        await message.reply_text(
            f"🚫 **User Banned!**\n\n"
            f"🆔 **User ID:** `{ban_user_id}`\n"
            f"📝 **Reason:** {reason}"
        )
        
    except ValueError:
        await message.reply_text("❌ User ID number hona chahiye.")


@Client.on_message(filters.command("unban") & filters.private)
async def unban_user_handler(client: Client, message: Message):
    """
    /unban - User ka ban hatao
    """
    user_id = message.from_user.id
    
    # Only super admin
    if user_id != Config.SUPER_ADMIN:
        await message.reply_text("👑 Ye command sirf Super Admin use kar sakta hai.")
        return
    
    if len(message.command) != 2:
        await message.reply_text("❌ **Usage:** `/unban USER_ID`")
        return
    
    try:
        unban_user_id = int(message.command[1])
        
        # Unban user
        await db.unban_user(unban_user_id)
        
        # Log
        await log_user_unbanned(client, unban_user_id, user_id)
        
        await message.reply_text(
            f"✅ **User Unbanned!**\n\n"
            f"🆔 **User ID:** `{unban_user_id}`"
        )
        
    except ValueError:
        await message.reply_text("❌ User ID number hona chahiye.")


# ═══════════════════════════════════════════════════════════════
# ⚙️ SETTINGS
# ═══════════════════════════════════════════════════════════════

@Client.on_message(filters.command("settings") & filters.private)
async def settings_handler(client: Client, message: Message):
    """
    /settings - Bot settings menu
    """
    user_id = message.from_user.id
    
    # Only super admin
    if user_id != Config.SUPER_ADMIN:
        await message.reply_text("👑 Ye command sirf Super Admin use kar sakta hai.")
        return
    
    settings_text = f"""
⚙️ **Bot Settings**

**Current Configuration:**

⏰ **Auto Delete:** {Config.AUTO_DELETE_HOURS} hours
📢 **Force Sub:** {'Enabled' if Config.FORCE_SUB_CHANNEL else 'Disabled'}
💸 **Shortener:** {'Enabled' if Config.SHORTENERS else 'Disabled'}
"""
    
    await message.reply_text(
        settings_text,
        reply_markup=superadmin_settings_keyboard()
    )


# ═══════════════════════════════════════════════════════════════
# 📜 LOGS
# ═══════════════════════════════════════════════════════════════

@Client.on_message(filters.command("logs") & filters.private)
async def logs_handler(client: Client, message: Message):
    """
    /logs - View recent logs
    """
    user_id = message.from_user.id
    
    # Only super admin
    if user_id != Config.SUPER_ADMIN:
        await message.reply_text("👑 Ye command sirf Super Admin use kar sakta hai.")
        return
    
    # Get stats
    total_users = await db.total_users()
    total_files = await db.total_files()
    admins = await db.get_all_admins()
    
    log_text = f"""
📜 **Bot Logs & Status**

📊 **Statistics:**
👥 Users: {total_users}
📂 Files: {total_files}
🛡️ Admins: {len(admins)}

💡 **Recent Activity:**
Check your LOG_CHANNEL for detailed logs.
"""
    
    await message.reply_text(log_text)


# ═══════════════════════════════════════════════════════════════
# ✅ SUPER ADMIN PLUGIN READY!
# ═══════════════════════════════════════════════════════════════
