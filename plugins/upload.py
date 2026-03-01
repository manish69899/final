# ═══════════════════════════════════════════════════════════════
# 📤 plugins/upload.py - FILE UPLOAD WIZARD
# ═══════════════════════════════════════════════════════════════
#
# 📌 KYUN USE HOTA HAI?
#    - Admin files upload karta hai
#    - Single ya Bulk (Album) mode
#    - Shortener on/off option
#    - Auto delete timestamp set
#
# 📌 FLOW:
#    1. Admin file bhejta hai
#    2. Queue mein add hoti hai
#    3. Mode select karta hai (Single/Bulk)
#    4. Shortener on/off karta hai
#    5. Links generate hote hain
# ═══════════════════════════════════════════════════════════════

from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, CallbackQuery
from config import Config, is_admin
from database.db import db
from utils.helpers import generate_unique_id, get_file_id, format_size, get_delete_timestamp
from utils.keyboard import (
    admin_upload_keyboard,
    admin_mode_keyboard,
    admin_shortener_keyboard,
    share_keyboard
)
from utils.logger import log_file_upload, log_batch_upload
import asyncio
import urllib.parse


# 💾 TEMPORARY CACHE (RAM mein files store hoti hain)
# Structure: { user_id: { 'files': [msg1, msg2], 'mode': None } }
UPLOAD_CACHE = {}


# ═══════════════════════════════════════════════════════════════
# 📤 FILE RECEIVER
# ═══════════════════════════════════════════════════════════════

@Client.on_message(
    filters.private & 
    (filters.document | filters.video | filters.audio | filters.photo) & 
    filters.user(Config.ADMINS)
)
async def receive_file(client: Client, message: Message):
    """
    Admin jab file bhejta hai, ye function chalta hai
    
    📌 LOGIC:
        1. Cache mein file store karo
        2. Queue count dikhao
        3. Processing buttons dikhao
    """
    user_id = message.from_user.id
    
    # Check admin permission
    if not await db.is_admin(user_id):
        return
    
    # Initialize cache for this user
    if user_id not in UPLOAD_CACHE:
        UPLOAD_CACHE[user_id] = {'files': [], 'mode': None}
    
    # Add file to cache
    UPLOAD_CACHE[user_id]['files'].append(message)
    
    total_files = len(UPLOAD_CACHE[user_id]['files'])
    
    # Send feedback with buttons
    await message.reply_text(
        f"✅ **File Added to Queue!**\n\n"
        f"📂 **Total Files:** `{total_files}`\n\n"
        f"💡 Aur files bhejo ya neeche button dabao.",
        quote=True,
        reply_markup=admin_upload_keyboard()
    )


# ═══════════════════════════════════════════════════════════════
# 🧙 UPLOAD WIZARD - STEP 1: MODE SELECTION
# ═══════════════════════════════════════════════════════════════

@Client.on_callback_query(filters.regex("upload_start"))
async def wizard_step1_mode(client: Client, callback: CallbackQuery):
    """
    Wizard Step 1: Mode select karo
    
    📌 OPTIONS:
        - Single: Har file ka alag link
        - Bulk: Saari files ka ek link (Album)
    """
    user_id = callback.from_user.id
    
    # Check cache
    if user_id not in UPLOAD_CACHE or not UPLOAD_CACHE[user_id]['files']:
        await callback.answer("❌ Queue empty! Pehle files bhejo.", show_alert=True)
        return
    
    total = len(UPLOAD_CACHE[user_id]['files'])
    
    await callback.message.edit_text(
        f"**🔢 STEP 1: Mode Select Karein**\n\n"
        f"📂 **Total Files:** {total}\n\n"
        f"🔹 **Single Links:** Har file ka alag link\n"
        f"🔹 **Bulk / Album:** Saari files ka EK link",
        reply_markup=admin_mode_keyboard()
    )


# ═══════════════════════════════════════════════════════════════
# 🧙 UPLOAD WIZARD - STEP 2: SHORTENER OPTION
# ═══════════════════════════════════════════════════════════════

@Client.on_callback_query(filters.regex(r"mode_(single|bulk)"))
async def wizard_step2_shortener(client: Client, callback: CallbackQuery):
    """
    Wizard Step 2: Shortener on/off
    
    📌 PARAMS:
        mode: "single" or "bulk"
    """
    user_id = callback.from_user.id
    mode = callback.data.split("_")[1]
    
    # Save mode to cache
    UPLOAD_CACHE[user_id]['mode'] = mode
    
    await callback.message.edit_text(
        f"**🔗 STEP 2: Shortener Use Karein?**\n\n"
        f"✅ **YES:** Users ko ad dekhna padega (Revenue 💸)\n"
        f"❌ **NO:** Direct file milegi",
        reply_markup=admin_shortener_keyboard()
    )


# ═══════════════════════════════════════════════════════════════
# 🧙 UPLOAD WIZARD - STEP 3: PROCESS & GENERATE LINKS
# ═══════════════════════════════════════════════════════════════

@Client.on_callback_query(filters.regex(r"shortener_(yes|no)"))
async def wizard_step3_process(client: Client, callback: CallbackQuery):
    """
    Wizard Step 3: Final processing
    
    📌 PARAMS:
        shortener: "yes" or "no"
    
    📌 LOGIC:
        - Get files from cache
        - Generate unique IDs
        - Save to database
        - Generate share links
    """
    user_id = callback.from_user.id
    # YAHAN DEFAULT FALSE HOGA, SIRF YES TAP KARNE PAR TRUE HOGA
    use_shortener = callback.data == "shortener_yes"
    
    # Get cache data
    cache = UPLOAD_CACHE.get(user_id)
    if not cache or not cache['files']:
        await callback.answer("❌ Session expired!", show_alert=True)
        return
    
    files = cache['files']
    mode = cache['mode']
    
    # Status message
    status = await callback.message.edit_text("⏳ **Processing files...**")
    
    # Get bot username
    me = await client.get_me()
    bot_username = me.username
    
    # Auto delete timestamp
    delete_at = get_delete_timestamp(Config.AUTO_DELETE_HOURS) if Config.AUTO_DELETE_HOURS > 0 else None
    
    # ───────────────────────────────────────────────────────────
    # PROCESS: BULK / ALBUM MODE
    # ───────────────────────────────────────────────────────────
    if mode == "bulk":
        batch_id = f"batch_{generate_unique_id()}"
        batch_link = f"https://t.me/{bot_username}?start={batch_id}"
        
        processed = 0
        for msg in files:
            file_id, telegram_unique_id, file_name, file_size, file_type = get_file_id(msg)
            
            if file_id:
                # 🔥 FIX: Har album file ke liye ekdum NAYA unique code banayenge
                # Taaki ek hi image ko album me baar-baar daalne par database restrict na kare!
                db_unique_code = f"b_{generate_unique_id()}_{processed}"
                
                await db.add_file({
                    'file_unique_id': db_unique_code,
                    'file_id': file_id,
                    'file_name': file_name,
                    'file_size': file_size,
                    'file_type': file_type,
                    'caption': msg.caption or "",
                    'batch_id': batch_id,
                    'uploaded_by': user_id,
                    'delete_at': delete_at,
                    'use_shortener': use_shortener
                })
                processed += 1
        
        # Log
        await log_batch_upload(client, batch_id, processed, batch_link, user_id)
        
        result_text = (
            f"✅ **Bulk Upload Complete!**\n\n"
            f"📂 **Files:** {processed}\n"
            f"🔗 **Link:** `{batch_link}`\n"
            f"💸 **Shortener:** {'ON 💰' if use_shortener else 'OFF'}"
        )
    
    # ───────────────────────────────────────────────────────────
    # PROCESS: SINGLE FILE MODE
    # ───────────────────────────────────────────────────────────
    else:
        result_text = "✅ **Upload Complete!**\n\n"
        
        for msg in files:
            file_id, telegram_unique_id, file_name, file_size, file_type = get_file_id(msg)
            
            if file_id:
                # Generate unique code for this file
                code = generate_unique_id()
                link = f"https://t.me/{bot_username}?start={code}"
                
                # FIX: use_shortener ko database me save kar rahe hain
                await db.add_file({
                    'file_unique_id': code,
                    'file_id': file_id,
                    'file_name': file_name,
                    'file_size': file_size,
                    'file_type': file_type,
                    'caption': msg.caption or "",
                    'batch_id': None,
                    'uploaded_by': user_id,
                    'delete_at': delete_at,
                    'use_shortener': use_shortener
                })
                
                # Log
                await log_file_upload(
                    client, file_name, file_type, file_size, code, link, user_id
                )
                
                size = format_size(file_size)
                result_text += f"📄 `{file_name}` ({size})\n🔗 `{link}`\n\n"
    
    # Clear cache
    if user_id in UPLOAD_CACHE:
        del UPLOAD_CACHE[user_id]
    
    # Send result with share button
    await status.edit_text(
        result_text,
        disable_web_page_preview=True,
        reply_markup=share_keyboard(result_text)
    )


# ═══════════════════════════════════════════════════════════════
# ❌ CANCEL & CLEAR QUEUE
# ═══════════════════════════════════════════════════════════════

@Client.on_callback_query(filters.regex("upload_cancel"))
async def cancel_upload(client: Client, callback: CallbackQuery):
    """
    Upload cancel karo
    """
    user_id = callback.from_user.id
    
    if user_id in UPLOAD_CACHE:
        del UPLOAD_CACHE[user_id]
    
    await callback.message.edit_text("❌ **Upload Cancelled!**\n\nQueue cleared.")


@Client.on_callback_query(filters.regex("upload_clear"))
async def clear_queue(client: Client, callback: CallbackQuery):
    """
    Queue clear karo
    """
    user_id = callback.from_user.id
    
    if user_id in UPLOAD_CACHE:
        del UPLOAD_CACHE[user_id]
    
    await callback.message.edit_text("🗑️ **Queue Cleared!**\n\nNayi files bhejo.")


# ═══════════════════════════════════════════════════════════════
# 📋 FILES LIST COMMAND
# ═══════════════════════════════════════════════════════════════

@Client.on_message(filters.command("files") & filters.private)
async def list_files(client: Client, message: Message):
    """
    Admin ke uploaded files ki list dikhata hai
    """
    user_id = message.from_user.id
    
    if not await db.is_admin(user_id):
        await message.reply_text("❌ This command is for admins only.")
        return
    
    # Get total files count
    total = await db.total_files()
    
    await message.reply_text(
        f"📂 **Files Statistics**\n\n"
        f"📊 **Total Files:** {total}\n"
        f"⏰ **Auto Delete:** {Config.AUTO_DELETE_HOURS} hours"
    )