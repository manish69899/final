# ═══════════════════════════════════════════════════════════════
# 📜 utils/logger.py - LOGGING UTILITY
# ═══════════════════════════════════════════════════════════════
#
# 📌 KYUN USE HOTA HAI?
#    - Bot activities ko log channel mein bhejta hai
#    - Easy debugging and monitoring
#    - Track new users, uploads, admin actions
# ═══════════════════════════════════════════════════════════════

from config import Config
from pyrogram import Client
from pyrogram.enums import ParseMode
from datetime import datetime


# ───────────────────────────────────────────────────────────────
# 📤 MAIN LOG FUNCTION
# ───────────────────────────────────────────────────────────────

async def send_log(client: Client, text: str):
    """
    Log channel mein message bhejta hai
    
    📌 PARAMS:
        client: Pyrogram client instance
        text: Log message (markdown supported)
    
    📌 RETURNS:
        bool: True if sent, False if failed
    """
    # Check if log channel is set
    if not Config.LOG_CHANNEL_ID:
        print("⚠️ LOG_CHANNEL_ID not set, skipping log")
        return False
    
    try:
        await client.send_message(
            chat_id=Config.LOG_CHANNEL_ID,
            text=text,
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True
        )
        return True
        
    except Exception as e:
        print(f"❌ Logger Error: {e}")
        return False


# ───────────────────────────────────────────────────────────────
# 👤 USER LOGS
# ───────────────────────────────────────────────────────────────

async def log_new_user(client: Client, user_id: int, name: str, username: str = None):
    """
    New user join log
    """
    # Escape special characters in name
    safe_name = escape_markdown(name) if name else "Unknown"
    safe_username = username if username else "None"
    
    text = f"""👤 #NEW_USER

**Name:** {safe_name}
**ID:** `{user_id}`
**Username:** @{safe_username}
**Profile:** [Click Here](tg://user?id={user_id})
**Time:** {datetime.now().strftime("%d-%m-%Y %H:%M")}
"""
    await send_log(client, text)


async def log_user_banned(client: Client, user_id: int, name: str, reason: str, by_admin: int):
    """
    User banned log
    """
    safe_name = escape_markdown(name) if name else "Unknown"
    safe_reason = escape_markdown(reason) if reason else "No reason"
    
    text = f"""🚫 #USER_BANNED

**User:** {safe_name}
**ID:** `{user_id}`
**Reason:** {safe_reason}
**Banned By:** `{by_admin}`
**Time:** {datetime.now().strftime("%d-%m-%Y %H:%M")}
"""
    await send_log(client, text)


async def log_user_unbanned(client: Client, user_id: int, by_admin: int):
    """
    User unbanned log
    """
    text = f"""✅ #USER_UNBANNED

**User ID:** `{user_id}`
**Unbanned By:** `{by_admin}`
**Time:** {datetime.now().strftime("%d-%m-%Y %H:%M")}
"""
    await send_log(client, text)


# ───────────────────────────────────────────────────────────────
# 📂 FILE LOGS
# ───────────────────────────────────────────────────────────────

async def log_file_upload(
    client: Client, 
    file_name: str, 
    file_type: str, 
    file_size: int,
    unique_id: str,
    link: str,
    by_admin: int
):
    """
    File upload log
    """
    from utils.helpers import format_size, get_file_type_emoji
    
    emoji = get_file_type_emoji(file_type)
    size = format_size(file_size)
    safe_name = escape_markdown(file_name) if file_name else "Unknown"
    
    text = f"""{emoji} #NEW_FILE

**File Name:** {safe_name}
**Type:** {file_type}
**Size:** {size}
**ID:** `{unique_id}`
**Link:** {link}
**Uploaded By:** `{by_admin}`
**Time:** {datetime.now().strftime("%d-%m-%Y %H:%M")}
"""
    await send_log(client, text)


async def log_batch_upload(
    client: Client,
    batch_id: str,
    file_count: int,
    link: str,
    by_admin: int
):
    """
    Batch/Album upload log
    """
    text = f"""📚 #NEW_BATCH

**Batch ID:** `{batch_id}`
**Files Count:** {file_count}
**Link:** {link}
**Uploaded By:** `{by_admin}`
**Time:** {datetime.now().strftime("%d-%m-%Y %H:%M")}
"""
    await send_log(client, text)


async def log_file_deleted(client: Client, file_id: str, reason: str = "Auto Delete"):
    """
    File deleted log
    """
    text = f"""🗑️ #FILE_DELETED

**File ID:** `{file_id}`
**Reason:** {reason}
**Time:** {datetime.now().strftime("%d-%m-%Y %H:%M")}
"""
    await send_log(client, text)


# ───────────────────────────────────────────────────────────────
# 🛡️ ADMIN LOGS
# ───────────────────────────────────────────────────────────────

async def log_admin_added(client: Client, new_admin_id: int, by_super_admin: int):
    """
    Admin added log
    """
    text = f"""🛡️ #ADMIN_ADDED

**New Admin ID:** `{new_admin_id}`
**Added By:** `{by_super_admin}`
**Time:** {datetime.now().strftime("%d-%m-%Y %H:%M")}
"""
    await send_log(client, text)


async def log_admin_removed(client: Client, admin_id: int, by_super_admin: int):
    """
    Admin removed log
    """
    text = f"""🛡️ #ADMIN_REMOVED

**Admin ID:** `{admin_id}`
**Removed By:** `{by_super_admin}`
**Time:** {datetime.now().strftime("%d-%m-%Y %H:%M")}
"""
    await send_log(client, text)


async def log_broadcast(client: Client, total: int, success: int, failed: int, by_admin: int):
    """
    Broadcast completed log
    """
    text = f"""📢 #BROADCAST

**Total Users:** {total}
**Success:** {success}
**Failed:** {failed}
**Sent By:** `{by_admin}`
**Time:** {datetime.now().strftime("%d-%m-%Y %H:%M")}
"""
    await send_log(client, text)


# ───────────────────────────────────────────────────────────────
# 📢 CHANNEL LOGS
# ───────────────────────────────────────────────────────────────

async def log_fsub_added(client: Client, channel_id: int, channel_title: str, by_admin: int):
    """
    Force sub channel added log
    """
    safe_title = escape_markdown(channel_title) if channel_title else "Unknown"
    
    text = f"""📢 #FSUB_ADDED

**Channel:** {safe_title}
**ID:** `{channel_id}`
**Added By:** `{by_admin}`
**Time:** {datetime.now().strftime("%d-%m-%Y %H:%M")}
"""
    await send_log(client, text)


async def log_fsub_removed(client: Client, channel_id: int, by_admin: int):
    """
    Force sub channel removed log
    """
    text = f"""📢 #FSUB_REMOVED

**Channel ID:** `{channel_id}`
**Removed By:** `{by_admin}`
**Time:** {datetime.now().strftime("%d-%m-%Y %H:%M")}
"""
    await send_log(client, text)


# ───────────────────────────────────────────────────────────────
# ⚠️ ERROR LOG
# ───────────────────────────────────────────────────────────────

async def log_error(client: Client, error_type: str, error_message: str, details: str = ""):
    """
    Error log
    """
    text = f"""⚠️ #ERROR

**Type:** {error_type}
**Message:** {error_message}
**Details:** {details}
**Time:** {datetime.now().strftime("%d-%m-%Y %H:%M")}
"""
    await send_log(client, text)


# ───────────────────────────────────────────────────────────────
# 🔧 HELPER FUNCTIONS
# ───────────────────────────────────────────────────────────────

def escape_markdown(text: str) -> str:
    """
    Markdown special characters escape karta hai
    
    📌 Pyrogram Markdown mein ye characters escape karne padte hain:
        _ * [ ] ( ) ~ ` > # + - = | { } . !
    """
    if not text:
        return ""
    
    special_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
    
    for char in special_chars:
        text = text.replace(char, f"\\{char}")
    
    return text


# ═══════════════════════════════════════════════════════════════
# ✅ LOGGER MODULE READY!
# ═══════════════════════════════════════════════════════════════
