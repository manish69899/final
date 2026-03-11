import asyncio
import os
from dotenv import load_dotenv
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import MessageNotModified

# Initialize and load environment variables
load_dotenv()

# Fetch and parse the Superadmin ID from the .env configuration
SUPER_ADMIN_ID = os.getenv("SUPER_ADMIN_ID")
if SUPER_ADMIN_ID:
    SUPER_ADMIN_ID = int(SUPER_ADMIN_ID)


def format_time_duration(seconds: int) -> str:
    """Converts a raw integer of seconds into a clean, human-readable string."""
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    
    time_parts = []
    if hours > 0: time_parts.append(f"{hours}h")
    if minutes > 0: time_parts.append(f"{minutes}m")
    if secs > 0 or not time_parts: time_parts.append(f"{secs}s")
        
    return " ".join(time_parts)


async def auto_delete_file(client, chat_id: int, message_id: int, delay_seconds: int = 60):
    """
    Executes an advanced background task with Smart Countdowns and UI updates.
    """
    
    # 1. Superadmin Exemption
    if chat_id == SUPER_ADMIN_ID:
        print(f"[INFO] Superadmin detected (ID: {chat_id}). Auto-delete bypassed.")
        return

    formatted_delay = format_time_duration(delay_seconds)
    print(f"[INFO] Advanced Timer initiated for user {chat_id}. Total delay: {formatted_delay}.")

    # 2. Premium UI Button (Aesthetic purpose)
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("⚠️ Forward Fast To Save", callback_data="dummy_btn")]
    ])

    # 3. Dispatch Initial Warning
    warning_text = (
        "⏳ **𝗔𝗧𝗧𝗘𝗡𝗧𝗜𝗢𝗡 𝗣𝗟𝗘𝗔𝗦𝗘** ⏳\n\n"
        f"🔒 This file is highly secured and will self-destruct in **{formatted_delay}**.\n"
        "👉 **Please forward it to your 'Saved Messages' immediately!**\n\n"

    )
    
    warning_msg = None
    try:
        warning_msg = await client.send_message(
            chat_id=chat_id, 
            text=warning_text,
            reply_markup=keyboard
        )
    except Exception as e:
        print(f"[ERROR] Failed to send pre-warning to {chat_id}: {e}")

    # 4. SMART COUNTDOWN LOGIC
    try:
        if delay_seconds > 60:
            # Wait until exactly 1 minute is left
            await asyncio.sleep(delay_seconds - 60)
            
            # Update message to show 1 Minute Warning
            if warning_msg:
                await client.edit_message_text(
                    chat_id=chat_id,
                    message_id=warning_msg.id,
                    text=(
                        "🚨 **𝗙𝗜𝗡𝗔𝗟 𝗪𝗔𝗥𝗡𝗜𝗡𝗚** 🚨\n\n"
                        "⚠️ Only **1 Minute** left before the file is deleted!\n"
                        "👉 Forward it NOW if you haven't already!\n\n"
                        
                    )
                )
            # Wait until 10 seconds are left
            await asyncio.sleep(50)
        elif delay_seconds > 10:
            # If total time was less than a minute, just wait until 10 seconds are left
            await asyncio.sleep(delay_seconds - 10)

        # 5. THE 10-SECOND PANIC MODE
        if warning_msg:
            await client.edit_message_text(
                chat_id=chat_id,
                message_id=warning_msg.id,
                text=(
                    "🔥 **𝗗𝗘𝗟𝗘𝗧𝗜𝗡𝗚 𝗜𝗡 𝟭𝟬 𝗦𝗘𝗖𝗢𝗡𝗗𝗦...** 🔥\n\n"
                    "🛡️ *Action required immediately!*"
                )
            )
        await asyncio.sleep(10)
        
    except MessageNotModified:
        pass # Ignore if API complains about identical message edit
    except Exception as e:
        print(f"[ERROR] Countdown logic failed: {e}")

    # 6. Execute Main Deletion and Dispatch Final Notice
    try:
        # Delete the main file
        await client.delete_messages(chat_id=chat_id, message_ids=message_id)
        
        # Delete the warning message itself (to clean up)
        if warning_msg:
            await client.delete_messages(chat_id=chat_id, message_ids=warning_msg.id)
            
        print(f"[SUCCESS] Target file {message_id} successfully deleted for user {chat_id}.")
        
        # Dispatch Sleek Post-Deletion Notice
        post_warning_text = (
            "🗑️ **𝗙𝗜𝗟𝗘 𝗦𝗘𝗖𝗨𝗥𝗘𝗟𝗬 𝗗𝗘𝗟𝗘𝗧𝗘𝗗**\n\n"
            "✨ *Your chat has been cleared for privacy.*\n"
           
        )
        post_msg = await client.send_message(chat_id=chat_id, text=post_warning_text)
        
        # 7. Ultimate Clean-up (Delete the final notice after 5 seconds)
        await asyncio.sleep(5)
        try:
            await client.delete_messages(chat_id=chat_id, message_ids=post_msg.id)
        except Exception:
            pass

    except Exception as e:
        print(f"[ERROR] An issue occurred during the final deletion phase for {chat_id}: {e}")