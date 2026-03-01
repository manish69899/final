import os
import sys
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
from config import Config

# Tumhara database file ka naam
DB_FILE = "bot_database.db"

# Yeh variable check karega ki auto-backup start hua ya nahi
AUTO_BACKUP_STARTED = True


# ───────────────────────────────────────────────────────────────
# ⏰ AUTO BACKUP SYSTEM (HAR 10 DIN MEIN)
# ───────────────────────────────────────────────────────────────
async def auto_backup_job(client: Client):
    """Background task jo har 10 din mein DB backup bhejega."""
    while True:
        # 10 Din = 10 * 24 * 60 * 60 = 864000 seconds
        await asyncio.sleep(864000) 
        
        if os.path.exists(DB_FILE):
            try:
                # Config.ADMINS me se pehle admin ko backup bhej do
                main_admin = Config.ADMINS[0] if isinstance(Config.ADMINS, list) else Config.ADMINS
                await client.send_document(
                    chat_id=main_admin,
                    document=DB_FILE,
                    caption="⏰ **Auto Backup (10 Days)**\n\nYe aapka automatic database backup hai. Ise safe rakhein."
                )
            except Exception as e:
                print(f"Auto-backup bhejne mein error aaya: {e}")

# Yeh dummy handler bot ke start hote hi auto-backup loop ko background me chalu kar dega
@Client.on_message(filters.all, group=-999)
async def trigger_auto_backup(client: Client, message: Message):
    global AUTO_BACKUP_STARTED
    if not AUTO_BACKUP_STARTED:
        AUTO_BACKUP_STARTED = True
        asyncio.create_task(auto_backup_job(client))


# ───────────────────────────────────────────────────────────────
# 📥 MANUAL BACKUP COMMAND
# ───────────────────────────────────────────────────────────────
@Client.on_message(filters.command("backup") & filters.user(Config.ADMINS))
async def backup_db(client: Client, message: Message):
    status_msg = await message.reply_text("⏳ Backup ban raha hai...")
    
    if os.path.exists(DB_FILE):
        try:
            # Database file Telegram par send karo
            await client.send_document(
                chat_id=message.chat.id,
                document=DB_FILE,
                caption="🗄️ **Ye lijiye aapka Database Backup**\n\nIs file ko safe rakhein. Restore karne ke liye is file par reply karke `/restore` bhejein."
            )
            await status_msg.delete()
        except Exception as e:
            await status_msg.edit_text(f"❌ Backup fail ho gaya: {e}")
    else:
        await status_msg.edit_text("❌ Database file abhi tak nahi bani hai.")


# ───────────────────────────────────────────────────────────────
# 📤 RESTORE COMMAND (WITH AUTO-RESTART)
# ───────────────────────────────────────────────────────────────
@Client.on_message(filters.command("restore") & filters.user(Config.ADMINS))
async def restore_db(client: Client, message: Message):
    # Check karo ki message kisi file ka reply hai ya nahi
    if not message.reply_to_message or not message.reply_to_message.document:
        return await message.reply_text("❌ Kripya us `.db` file par reply karein jise restore karna hai.")

    doc = message.reply_to_message.document
    
    # Security check: Sirf .db files allow karo
    if not doc.file_name.endswith(".db"):
        return await message.reply_text("❌ Ye invalid file hai. Sirf `.db` file restore ho sakti hai.")

    status_msg = await message.reply_text("⏳ Database restore ho raha hai. Please wait...")

    try:
        # Safety ke liye purani DB file ka ek temporary backup bana lo
        if os.path.exists(DB_FILE):
            os.rename(DB_FILE, f"{DB_FILE}.bak")

        # Nayi file ko DB_FILE ke naam se download karo
        await client.download_media(message.reply_to_message, file_name=DB_FILE)
        
        await status_msg.edit_text(
            "✅ **Database Successfully Restored!**\n\n"
            "🔄 Naya data load karne ke liye bot apne aap restart ho raha hai..."
        )
        
        # ⚠️ Yahan magic hoga: Ye script ko khud-ba-khud force restart kar dega
        os.execl(sys.executable, sys.executable, *sys.argv)
        
    except Exception as e:
        # Agar error aayi, to purani file wapas restore kar do
        if os.path.exists(f"{DB_FILE}.bak"):
            os.rename(f"{DB_FILE}.bak", DB_FILE)
        await status_msg.edit_text(f"❌ Restore fail ho gaya: {e}")