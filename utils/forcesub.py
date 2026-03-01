# ═══════════════════════════════════════════════════════════════
# 📢 utils/forcesub.py - FORCE SUBSCRIPTION CHECK
# ═══════════════════════════════════════════════════════════════
#
# 📌 KYUN USE HOTA HAI?
#    - Check karta hai ki user ne channels join kiye hain ya nahi
#    - Private channels ke join requests handle karta hai
#    - Force sub bypass for admins
#
# 📌 HOW IT WORKS:
#    1. User /start command bhejta hai
#    2. Check hota hai ki user ne required channels join kiye hain
#    3. Agar nahi, toh join buttons dikhate hain
#    4. Agar haan, toh file milti hai
# ═══════════════════════════════════════════════════════════════

from pyrogram.errors import UserNotParticipant
from pyrogram.enums import ChatMemberStatus
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import Config
from database.db import db


# ───────────────────────────────────────────────────────────────
# 🔍 MAIN FORCE SUB CHECK
# ───────────────────────────────────────────────────────────────

async def check_force_sub(client, message) -> tuple:
    """
    Check karta hai ki user ne force sub channels join kiye hain ya nahi
    
    📌 PARAMS:
        client: Pyrogram client instance
        message: Pyrogram message object
    
    📌 RETURNS:
        tuple: (is_joined: bool, keyboard: InlineKeyboardMarkup or None)
        
        - (True, None) -> User joined all channels, proceed
        - (False, keyboard) -> User needs to join, show keyboard
    
    📌 EXAMPLE:
        >>> is_joined, keyboard = await check_force_sub(client, message)
        >>> if not is_joined:
        >>>     await message.reply("Join channels first!", reply_markup=keyboard)
    """
    user_id = message.from_user.id
    
    # ───────────────────────────────────────────────────────────
    # STEP 1: Admin Bypass
    # ───────────────────────────────────────────────────────────
    # Admins ko force sub se exempt karo
    if user_id == Config.SUPER_ADMIN or user_id in Config.ADMINS:
        return True, None
    
    # ───────────────────────────────────────────────────────────
    # STEP 2: Get Force Sub Channels from Database
    # ───────────────────────────────────────────────────────────
    channels = await db.get_fsub_channels()
    
    # Agar koi channel set nahi hai
    if not channels:
        return True, None
    
    # ───────────────────────────────────────────────────────────
    # STEP 3: Check Each Channel
    # ───────────────────────────────────────────────────────────
    missing_channels = []  # Channels that user hasn't joined
    
    for channel in channels:
        channel_id = channel['channel_id']
        channel_title = channel.get('channel_title', 'Channel')
        channel_link = channel.get('channel_link')
        
        try:
            # ───────────────────────────────────────────────────
            # CHECK: User ka membership status
            # ───────────────────────────────────────────────────
            member = await client.get_chat_member(channel_id, user_id)
            
            # User status check
            if member.status == ChatMemberStatus.BANNED:
                # User is banned in this channel
                await message.reply_text(
                    f"🚫 **Access Denied!**\n\n"
                    f"Aap {channel_title} channel se banned hain.\n"
                    f"File download karne ke liye admin se contact karein."
                )
                return False, None
            
            # Valid statuses: MEMBER, ADMINISTRATOR, OWNER
            if member.status in [
                ChatMemberStatus.MEMBER,
                ChatMemberStatus.ADMINISTRATOR,
                ChatMemberStatus.OWNER
            ]:
                # User has joined this channel ✅
                continue
                
        except UserNotParticipant:
            # User hasn't joined this channel
            pass
            
        except Exception as e:
            # Error handling (channel deleted, bot removed, etc.)
            print(f"⚠️ Force Sub Error for channel {channel_id}: {e}")
            
            # Skip this channel if error
            # User ko pareshan mat karo
            continue
        
        # ───────────────────────────────────────────────────────
        # CHECK: Pending Join Request (for private channels)
        # ───────────────────────────────────────────────────────
        is_pending = await db.is_join_request_pending(user_id, channel_id)
        
        if is_pending:
            # User has sent join request, let them pass
            print(f"✅ User {user_id} has pending request for {channel_title}")
            continue
        
        # ───────────────────────────────────────────────────────
        # CHANNEL NOT JOINED: Add to missing list
        # ───────────────────────────────────────────────────────
        if channel_link:
            missing_channels.append({
                'channel_id': channel_id,
                'channel_title': channel_title,
                'channel_link': channel_link
            })
    
    # ───────────────────────────────────────────────────────────
    # STEP 4: Result
    # ───────────────────────────────────────────────────────────
    
    # Agar saare channels joined hain
    if not missing_channels:
        return True, None
    
    # Agar kuch channels missing hain -> Keyboard banao
    keyboard = await create_force_sub_keyboard(
        missing_channels, 
        client.me.username,
        message.command[1] if len(message.command) > 1 else ""
    )
    
    return False, keyboard


# ───────────────────────────────────────────────────────────────
# ⌨️ FORCE SUB KEYBOARD CREATOR
# ───────────────────────────────────────────────────────────────

async def create_force_sub_keyboard(
    channels: list, 
    bot_username: str, 
    start_arg: str = ""
) -> InlineKeyboardMarkup:
    """
    Force sub ke liye keyboard banaata hai
    
    📌 PARAMS:
        channels: List of channels user needs to join
        bot_username: Bot's username
        start_arg: Original start argument (to preserve file link)
    
    📌 RETURNS:
        InlineKeyboardMarkup with join buttons
    """
    buttons = []
    
    # Each channel ke liye join button
    for channel in channels:
        title = channel.get('channel_title', 'Channel')
        link = channel.get('channel_link', '#')
        
        buttons.append([
            InlineKeyboardButton(f"📢 Join {title}", url=link)
        ])
    
    # Refresh button - user can try again after joining
    if start_arg:
        refresh_url = f"https://t.me/{bot_username}?start={start_arg}"
    else:
        refresh_url = f"https://t.me/{bot_username}?start=refresh"
    
    buttons.append([
        InlineKeyboardButton("🔄 I've Joined - Refresh", url=refresh_url)
    ])
    
    return InlineKeyboardMarkup(buttons)


# ───────────────────────────────────────────────────────────────
# 📝 FORCE SUB INFO
# ───────────────────────────────────────────────────────────────

async def get_force_sub_message(channels: list) -> str:
    """
    Force sub message generate karta hai
    
    📌 PARAMS:
        channels: List of channels
    
    📌 RETURNS:
        str: Formatted message
    """
    if not channels:
        return "✅ No force sub required!"
    
    message = "⚠️ **Access Denied!**\n\n"
    message += "📁 File download karne ke liye neeche diye gaye channels ko join karein:\n\n"
    
    for i, channel in enumerate(channels, 1):
        title = channel.get('channel_title', 'Channel')
        message += f"**{i}.** {title}\n"
    
    message += "\n⏳ Join karne ke baad 'Refresh' button dabayein."
    
    return message


# ───────────────────────────────────────────────────────────────
# 🔧 SINGLE CHANNEL CHECK
# ───────────────────────────────────────────────────────────────

async def check_single_channel(client, user_id: int, channel_id: int) -> bool:
    """
    Single channel check karta hai
    
    📌 PARAMS:
        client: Pyrogram client
        user_id: User ID to check
        channel_id: Channel ID to check
    
    📌 RETURNS:
        bool: True if joined, False if not
    """
    try:
        member = await client.get_chat_member(channel_id, user_id)
        
        if member.status in [
            ChatMemberStatus.MEMBER,
            ChatMemberStatus.ADMINISTRATOR,
            ChatMemberStatus.OWNER
        ]:
            return True
            
    except UserNotParticipant:
        pass
    except Exception as e:
        print(f"⚠️ Single channel check error: {e}")
    
    # Check pending request
    return await db.is_join_request_pending(user_id, channel_id)


# ═══════════════════════════════════════════════════════════════
# ✅ FORCE SUB MODULE READY!
#
# 📌 USAGE:
#    from utils.forcesub import check_force_sub
#    is_joined, keyboard = await check_force_sub(client, message)
# ═══════════════════════════════════════════════════════════════
