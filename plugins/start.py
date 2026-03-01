# ═══════════════════════════════════════════════════════════════
# 🚀 plugins/start.py - START COMMAND HANDLER
# ═══════════════════════════════════════════════════════════════

from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from pyrogram.enums import ParseMode
from config import Config, is_admin
from database.db import db
from utils.forcesub import check_force_sub
from utils.shortener import get_short_link
from utils.helpers import generate_unique_id, format_size, time_ago
from utils.logger import log_new_user
import asyncio


# ═══════════════════════════════════════════════════════════════
# 🚀 START COMMAND HANDLER
# ═══════════════════════════════════════════════════════════════

@Client.on_message(filters.command("start") & filters.private)
async def start_handler(client: Client, message: Message):
    """
    /start command ka main handler
    """
    
    user = message.from_user
    user_id = user.id
    name = user.first_name
    username = user.username
    
    # Add User to Database
    is_new_user = await db.add_user(user_id, name, username)
    
    if is_new_user:
        await log_new_user(client, user_id, name, username)
    
    # Check if Banned
    if await db.is_banned(user_id):
        await message.reply_text(
            "🚫 **Access Denied!**\n\n"
            "Aapko is bot se ban kiya gaya hai.\n"
            "Admin se contact karein."
        )
        return
    
    # Get Payload
    payload = message.command[1] if len(message.command) > 1 else None
    
    # Force Sub Check (Skip for admins)
    if not is_admin(user_id):
        is_joined, join_keyboard = await check_force_sub(client, message)
        
        if not is_joined:
            await message.reply_text(
                "⚠️ **Access Denied!**\n\n"
                "First join channels",
                reply_markup=join_keyboard
            )
            return
    
    # Handle Scenarios
    if not payload or payload == "refresh":
        await handle_welcome(client, message, user_id)
        return
    
    if "_verified" in payload:
        clean_payload = payload.replace("_verified", "")
        await deliver_file(client, message, clean_payload)
        return
    
    await handle_file_request(client, message, payload)


# ═══════════════════════════════════════════════════════════════
# 👋 WELCOME MESSAGE
# ═══════════════════════════════════════════════════════════════

async def handle_welcome(client: Client, message: Message, user_id: int):
    """Welcome message dikhata hai"""
    user = message.from_user
    me = await client.get_me()
    
    welcome_text = Config.WELCOME_MESSAGE.format(name=user.first_name)
    
    await message.reply_text(
        welcome_text,
        reply_markup=InlineKeyboardMarkup([
            [
                InlineKeyboardButton("📢 Join Channel", url="https://t.me/jharkhandcollege"),
                InlineKeyboardButton("ℹ️ About", callback_data="about")
            ]
        ]),
        disable_web_page_preview=True
    )


# ═══════════════════════════════════════════════════════════════
# 📂 FILE REQUEST (With Shortener)
# ═══════════════════════════════════════════════════════════════

async def handle_file_request(client: Client, message: Message, payload: str):
    """
    File request handle karta hai
    
    📌 CHECK: File ke saath shortener flag check karo aur database match karo
    """
    user_id = message.from_user.id
    
    status = await message.reply_text("🔄 **Processing...**")
    
    # Check Batch or Single
    if payload.startswith("batch_"):
        # 🔥 BUG FIX: Payload se batch_ replace nahi karenge kyunki ID exact match karni hai
        batch_id = payload
        files = await db.get_files_by_batch(batch_id)
        
        if not files:
            await status.edit_text("❌ **Link Expired or Album Deleted!**")
            return
        
        file_info = f"📚 **Album Found!**\n📂 Files: {len(files)}"
        
        # 🔥 BUG FIX: DB se integer check karega (1 = Yes, 0 = No)
        use_shortener = (files[0].get('use_shortener') == 1)
    else:
        file = await db.get_file(payload)
        
        if not file:
            await status.edit_text("❌ **File Not Found or Expired!**")
            return
        
        file_info = f"📄 **File Found!**\n📂 Name: {file.get('file_name', 'Unknown')}"
        
        # 🔥 BUG FIX: DB se integer check karega (1 = Yes, 0 = No)
        use_shortener = (file.get('use_shortener') == 1)
    
    me = await client.get_me()
    bot_username = me.username
    destination = f"https://t.me/{bot_username}?start={payload}_verified"
    
    # ───────────────────────────────────────────────────────────
    # IMPORTANT: Shortener check logic
    # Agar shortener YES hai toh link denge, warna sidha file deliver karenge
    # ───────────────────────────────────────────────────────────
    if use_shortener and Config.SHORTENERS:
        await status.edit_text(f"{file_info}\n\n🔗 **Generating link...**")
        
        try:
            # Generate short link
            short_url = await get_short_link(destination, user_id=user_id)
            
            await status.edit_text(
                f"{file_info}\n\n"
                "Click and Open Link below\n"
                "How To Open link Tutorial @tutoriallink575",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("Open Link to get file", url=short_url)]
                ])
            )
        except Exception as e:
            # 🔥 FALLBACK: Agar API Down hai, toh crash hone ki bajaye sidha file de dega
            print(f"Shortener Error: {e}")
            await status.delete()
            await deliver_file(client, message, payload)
    else:
        # 🔥 Direct File Delivery: Shortener NO hone par automatically file bheje dega
        await status.delete()
        await deliver_file(client, message, payload)


# ═══════════════════════════════════════════════════════════════
# 📥 FILE DELIVERY
# ═══════════════════════════════════════════════════════════════

async def deliver_file(client: Client, message: Message, payload: str):
    """File directly deliver karta hai"""
    status = await message.reply_text("📂 **Fetching file...**")
    
    try:
        if payload.startswith("batch_"):
            # 🔥 Yahan se bhi replace hata diya hai taki ID mismatch na ho
            batch_id = payload
            files = await db.get_files_by_batch(batch_id)
            
            if not files:
                await status.edit_text("❌ **Album Not Found!**")
                return
            
            await status.edit_text(f"✅ **Album Found!**\n\n📤 Sending {len(files)} files...")
            
            for file in files:
                try:
                    await client.send_cached_media(
                        chat_id=message.chat.id,
                        file_id=file['file_id'],
                        caption=file.get('caption', '')
                    )
                    await asyncio.sleep(0.5)
                except Exception as e:
                    print(f"❌ Error sending file: {e}")
            
            await status.delete()
            
            for file in files:
                await db.increment_file_views(file['file_unique_id'])
        
        else:
            file = await db.get_file(payload)
            
            if not file:
                await status.edit_text("❌ **File Not Found!**")
                return
            
            await client.send_cached_media(
                chat_id=message.chat.id,
                file_id=file['file_id'],
                caption=file.get('caption', '')
            )
            
            await status.delete()
            await db.increment_file_views(payload)
            
    except Exception as e:
        print(f"❌ Error: {e}")
        await status.edit_text("⚠️ **Something went wrong!**")


# ═══════════════════════════════════════════════════════════════
# ❓ HELP COMMAND
# ═══════════════════════════════════════════════════════════════

@Client.on_message(filters.command("help") & filters.private)
async def help_handler(client: Client, message: Message):
    """Help command"""
    await message.reply_text(
        Config.HELP_MESSAGE,
        disable_web_page_preview=True
    )


# ═══════════════════════════════════════════════════════════════
# ℹ️ ABOUT COMMAND
# ═══════════════════════════════════════════════════════════════

@Client.on_message(filters.command("about") & filters.private)
async def about_handler(client: Client, message: Message):
    """About command"""
    total_users = await db.total_users()
    total_files = await db.total_files()
    
    about_text = Config.ABOUT_MESSAGE.format(
        total_users=total_users,
        total_files=total_files
    )
    
    await message.reply_text(about_text, disable_web_page_preview=True)


# ═══════════════════════════════════════════════════════════════
# 👤 PROFILE COMMAND - FIXED
# ═══════════════════════════════════════════════════════════════

@Client.on_message(filters.command("profile") & filters.private)
async def profile_handler(client: Client, message: Message):
    """
    Profile command - Shows user profile
    
    📌 FIX: Proper database check and formatting
    """
    user = message.from_user
    
    # Get user from database
    db_user = await db.get_user(user.id)
    
    if not db_user:
        # User not in DB, add them
        await db.add_user(user.id, user.first_name, user.username)
        db_user = await db.get_user(user.id)
    
    if not db_user:
        await message.reply_text("❌ Profile error. Try /start first.")
        return
    
    # Format profile
    join_date = time_ago(db_user.get('joined_date', 0))
    files_downloaded = db_user.get('files_downloaded', 0)
    is_banned = db_user.get('is_banned', 0)
    
    # Escape name for markdown
    name = user.first_name.replace('_', '\\_').replace('*', '\\*') if user.first_name else "Unknown"
    username = user.username if user.username else "None"
    
    profile_text = f"""
👤 **Your Profile**

**Name:** {name}
**ID:** `{user.id}`
**Username:** @{username}

**Joined:** {join_date}
**Files Downloaded:** {files_downloaded}

**Status:** {"🚫 Banned" if is_banned else "✅ Active"}
"""
    
    await message.reply_text(profile_text)


# ═══════════════════════════════════════════════════════════════
# ✅ START PLUGIN READY!
# ═══════════════════════════════════════════════════════════════