# ═══════════════════════════════════════════════════════════════
# 🛡️ plugins/admin.py - ADMIN COMMANDS
# ═══════════════════════════════════════════════════════════════
#
# 📌 KYUN USE HOTA HAI?
#    - Admin specific commands handle karta hai
#    - Stats, Broadcast, Force Sub management
#
# 📌 COMMANDS:
#    /stats - Bot statistics
#    /broadcast - Message to all users
#    /add_fsub - Add force sub channel
#    /del_fsub - Remove force sub channel
#    /fsub_list - List channels
# ═══════════════════════════════════════════════════════════════

from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from config import Config
from database.db import db
from utils.keyboard import admin_fsub_keyboard, admin_broadcast_keyboard
from utils.logger import log_broadcast, log_fsub_added, log_fsub_removed
from utils.helpers import format_size, time_ago
import asyncio


# ═══════════════════════════════════════════════════════════════
# 📊 STATS COMMAND
# ═══════════════════════════════════════════════════════════════

@Client.on_message(filters.command("stats") & filters.private)
async def stats_handler(client: Client, message: Message):
    """
    /stats - Bot statistics dikhata hai
    
    📌 SHOWS:
        - Total users
        - Total files
        - Active channels
    """
    user_id = message.from_user.id
    
    # Check admin
    if not await db.is_admin(user_id):
        await message.reply_text("❌ This command is for admins only.")
        return
    
    # Get stats
    total_users = await db.total_users()
    total_files = await db.total_files()
    channels = await db.get_fsub_channels()
    
    # 🔴 FIX: HOURS ko MINUTES me change kar diya
    stats_text = f"""
📊 **Bot Statistics**

👥 **Total Users:** `{total_users}`
📂 **Total Files:** `{total_files}`
📢 **Force Sub Channels:** `{len(channels)}`
⏰ **Auto Delete:** `{Config.AUTO_DELETE_HOURS} hours`
"""
    
    await message.reply_text(stats_text)


# ═══════════════════════════════════════════════════════════════
# 📢 BROADCAST COMMAND
# ═══════════════════════════════════════════════════════════════

@Client.on_message(filters.command("broadcast") & filters.private)
async def broadcast_handler(client: Client, message: Message):
    """
    /broadcast - Sabhi users ko message bhejo
    
    📌 USAGE:
        Kisi message ko reply karke /broadcast likho
    """
    user_id = message.from_user.id
    
    # Check admin
    if not await db.is_admin(user_id):
        await message.reply_text("❌ This command is for admins only.")
        return
    
    # Check reply
    if not message.reply_to_message:
        await message.reply_text(
            "❌ **Usage:**\n\n"
            "Kisi message ko reply karke `/broadcast` likhein.\n\n"
            "**Example:**\n"
            "1. Message bhejo\n"
            "2. Us message ko reply karke `/broadcast` likho"
        )
        return
    
    # Get all users
    all_users = await db.get_all_users()
    total = len(all_users)
    
    # 🔴 FIX: Reply to the original message so callback can find it
    confirm = await message.reply_to_message.reply_text(
        f"📢 **Broadcast Confirmation**\n\n"
        f"👥 **Total Users:** {total}\n\n"
        f"Kya aap ye message sabko bhejna chahte hain?",
        reply_markup=admin_broadcast_keyboard(),
        quote=True
    )


async def do_broadcast(client: Client, message: Message, admin_id: int):
    """
    Actual broadcast execution (Fallback / Kept for modularity)
    Callback file handles the main broadcast now.
    """
    all_users = await db.get_all_users()
    broadcast_msg = message.reply_to_message
    
    status = await message.reply_text(f"📢 **Broadcast Started...**\n\n👥 Sending to {len(all_users)} users...")
    success, failed = 0, 0
    
    for user_id in all_users:
        try:
            await broadcast_msg.copy(chat_id=user_id)
            success += 1
        except Exception:
            failed += 1
        
        if (success + failed) % 20 == 0:
            await status.edit_text(f"📢 **Broadcasting...**\n\n✅ Success: {success}\n❌ Failed: {failed}")
        await asyncio.sleep(0.05)
    
    await status.edit_text(f"📢 **Broadcast Complete!**\n\n✅ **Success:** {success}\n❌ **Failed:** {failed}")
    await log_broadcast(client, len(all_users), success, failed, admin_id)


# ═══════════════════════════════════════════════════════════════
# 📢 FORCE SUB MANAGEMENT
# ═══════════════════════════════════════════════════════════════
@Client.on_message(filters.command("add_fsub") & filters.private)
async def add_fsub_handler(client: Client, message: Message):
    """
    /add_fsub - Force sub channel add karo (Optimized for Paid Promotions)
    """
    user_id = message.from_user.id
    
    # Check admin
    if not await db.is_admin(user_id):
        await message.reply_text("❌ This command is for admins only.")
        return
    
    # Check arguments
    if len(message.command) != 2:
        await message.reply_text(
            "❌ **Usage:** `/add_fsub -100123456789` ya `/add_fsub @channelusername`\n\n"
            "**PRO TIP:** Private channel ki ID hamesha -100 se shuru hoti hai."
        )
        return
    
    status_msg = await message.reply_text("⏳ Channel check kar raha hoon...")
    
    try:
        channel_input = message.command[1]
        
        # Agar ID hai toh integer me convert karo, warna string (username) rehne do
        if channel_input.startswith("-100") or channel_input.isdigit():
            channel_input = int(channel_input)
        elif not channel_input.startswith("@") and not channel_input.startswith("http"):
            channel_input = "@" + channel_input
        
        # ───────────────────────────────────────────────────────────
        # STEP 1: Chat/Channel ko fetch karo
        # ───────────────────────────────────────────────────────────
        try:
            chat = await client.get_chat(channel_input)
            real_channel_id = chat.id
        except Exception as e:
            return await status_msg.edit_text(
                f"⚠️ **Error:** Bot is channel ko dhundh nahi paaya.\n\n"
                f"`{e}`\n\n"
                f"**Fix:** Pehle bot ko us channel mein zarur Admin banayein!"
            )
        
        # ───────────────────────────────────────────────────────────
        # STEP 2: Invite Link Check (Asli Admin Test)
        # ───────────────────────────────────────────────────────────
        try:
            invite_link = chat.invite_link
            # Agar link nahi hai, toh bot naya link generate karega
            if not invite_link:
                invite_link = await client.export_chat_invite_link(real_channel_id)
        except Exception as e:
            return await status_msg.edit_text(
                f"⚠️ **Permission Error!**\n\n"
                f"Bot '{chat.title}' mein add toh hai, par usko link nikalne ki power nahi mili hai.\n\n"
                f"**Fix:** Channel owner ko boliye ki bot ki admin permissions me **'Invite Users via Link'** ko ON kare.\n\n`Error: {e}`"
            )
        
        # ───────────────────────────────────────────────────────────
        # STEP 3: Database me save karo
        # ───────────────────────────────────────────────────────────
        await db.add_fsub_channel(real_channel_id, chat.title, invite_link, user_id)
        
        # Log entry for security
        await log_fsub_added(client, real_channel_id, chat.title, user_id)
        
        await status_msg.edit_text(
            f"✅ **Promo Channel Successfully Added!**\n\n"
            f"📢 **Title:** {chat.title}\n"
            f"🆔 **ID:** `{real_channel_id}`\n\n"
            f"Ab users ko ye channel automatically join karna padega."
        )
        
    except Exception as e:
        await status_msg.edit_text(f"❌ Kuch galat ho gaya: {e}")

@Client.on_message(filters.command("del_fsub") & filters.private)
async def del_fsub_handler(client: Client, message: Message):
    """
    /del_fsub - Force sub channel remove karo
    """
    user_id = message.from_user.id
    
    # Check admin
    if not await db.is_admin(user_id):
        await message.reply_text("❌ This command is for admins only.")
        return
    
    if len(message.command) != 2:
        await message.reply_text("❌ **Usage:** `/del_fsub -100123456789`")
        return
    
    try:
        channel_id = int(message.command[1])
        
        # Remove from database
        await db.remove_fsub_channel(channel_id)
        
        # Log
        await log_fsub_removed(client, channel_id, user_id)
        
        await message.reply_text(
            f"🗑️ **Channel Removed!**\n\n"
            f"🆔 **ID:** `{channel_id}`\n\n"
            f"Ab users ko ye channel join karne ki zaroorat nahi."
        )
        
    except ValueError:
        await message.reply_text("❌ Channel ID number hona chahiye.")


@Client.on_message(filters.command("fsub_list") & filters.private)
async def fsub_list_handler(client: Client, message: Message):
    """
    /fsub_list - Force sub channels ki list
    """
    user_id = message.from_user.id
    
    # Check admin
    if not await db.is_admin(user_id):
        await message.reply_text("❌ This command is for admins only.")
        return
    
    # Get channels
    channels = await db.get_fsub_channels()
    
    if not channels:
        await message.reply_text("📭 **No Force Sub Channels Set.**\n\n`/add_fsub` se channel add karein.")
        return
    
    # Build list
    text = "📋 **Active Force Sub Channels:**\n\n"
    
    for channel in channels:
        title = channel.get('channel_title', 'Unknown')
        cid = channel['channel_id']
        text += f"📢 {title}\n   🆔 `{cid}`\n\n"
    
    # Send with keyboard
    await message.reply_text(
        text,
        reply_markup=admin_fsub_keyboard(channels)
    )


# ═══════════════════════════════════════════════════════════════
# ✅ ADMIN PLUGIN READY!
# ═══════════════════════════════════════════════════════════════