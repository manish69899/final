# ═══════════════════════════════════════════════════════════════
# ⌨️ utils/keyboard.py - ALL KEYBOARDS & BUTTONS
# ═══════════════════════════════════════════════════════════════
#
# 📌 KYUN USE HOTA HAI?
#    - Saare keyboards (buttons) ek jagah defined hain
#    - Easy to modify and maintain
#    - Role-based keyboards (User, Admin, Super Admin)
#
# 📌 KEYBOARD TYPES:
#    - InlineKeyboard: Buttons below message
#    - ReplyKeyboard: Buttons above text input
# ═══════════════════════════════════════════════════════════════

from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton


# ═══════════════════════════════════════════════════════════════
# 👤 USER KEYBOARDS
# ═══════════════════════════════════════════════════════════════

def user_main_keyboard():
    """
    👤 USER KA MAIN MENU (Reply Keyboard)
    
    📌 KYA DIKHATA HAI:
       - 🏠 Home - Main menu
       - 📂 My Files - User ke downloaded files
       - 👤 Profile - User info
       - ❓ Help - Help message
    
    📌 USAGE:
       await message.reply_text(
           "Main Menu",
           reply_markup=user_main_keyboard()
       )
    """
    return ReplyKeyboardMarkup(
        [
            [KeyboardButton("🏠 Home"), KeyboardButton("📂 My Files")],
            [KeyboardButton("👤 Profile"), KeyboardButton("❓ Help")]
        ],
        resize_keyboard=True,  # Buttons chhote dikhenge
        one_time_keyboard=False  # Keyboard rahega
    )


def user_start_keyboard(bot_username: str):
    """
    👤 START COMMAND KE LIYE INLINE BUTTONS
    
    📌 BUTTONS:
       - 📢 Join Channel
       - ℹ️ About
       - ➕ Add to Group
    """
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("📢 Join Channel", url="https://t.me/jharkhandcollege")
        ],
        [
            InlineKeyboardButton("➕ Add to Group", url=f"https://t.me/{bot_username}?startgroup=true")
        ]
    ])


def user_profile_keyboard():
    """
    👤 PROFILE KE LIYE INLINE BUTTONS
    """
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("📊 My Stats", callback_data="user_stats"),
            InlineKeyboardButton("📜 History", callback_data="user_history")
        ],
        [
            InlineKeyboardButton("🗑️ Clear History", callback_data="clear_history")
        ]
    ])


# ═══════════════════════════════════════════════════════════════
# 🛡️ ADMIN KEYBOARDS
# ═══════════════════════════════════════════════════════════════

def admin_main_keyboard():
    """
    🛡️ ADMIN KA MAIN MENU (Reply Keyboard)
    
    📌 FEATURES:
       - 📤 Upload Files - Files upload kare
       - 📊 Stats - Bot statistics
       - 📢 Broadcast - Message to all users
       - ⚙️ Settings - Bot settings
       - 📋 Files - Manage files
       - 📢 Channels - Force sub channels
    """
    return ReplyKeyboardMarkup(
        [
            [KeyboardButton("📤 Upload File"), KeyboardButton("📊 Stats")],
            [KeyboardButton("📢 Broadcast"), KeyboardButton("⚙️ Settings")],
            [KeyboardButton("📋 My Files"), KeyboardButton("📢 Channels")]
        ],
        resize_keyboard=True
    )


def admin_upload_keyboard():
    """
    🛡️ FILE UPLOAD WIZARD KE LIYE INLINE BUTTONS
    
    📌 FLOW:
       1. Admin file bhejta hai
       2. Ye buttons aate hain
       3. Mode select karta hai
       4. Shortener on/off
    """
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🚀 Start Processing", callback_data="upload_start"),
            InlineKeyboardButton("❌ Cancel", callback_data="upload_cancel")
        ],
        [
            InlineKeyboardButton("🗑️ Clear Queue", callback_data="upload_clear")
        ]
    ])


def admin_mode_keyboard():
    """
    🛡️ UPLOAD MODE SELECT KE LIYE
    """
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("📥 Single Links", callback_data="mode_single"),
            InlineKeyboardButton("📚 Bulk / Album", callback_data="mode_bulk")
        ]
    ])


def admin_shortener_keyboard():
    """
    🛡️ SHORTENER ON/OFF KE LIYE
    """
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ YES (Earn Money)", callback_data="shortener_yes"),
            InlineKeyboardButton("❌ NO (Direct)", callback_data="shortener_no")
        ]
    ])


def admin_fsub_keyboard(channels: list):
    """
    🛡️ FORCE SUB CHANNELS LIST
    
    📌 PARAMS:
        channels: List of channel dicts from database
    
    📌 SHOWS:
        - Each channel with delete button
        - Add new channel button
    """
    buttons = []
    
    for channel in channels:
        # Har channel ke liye ek row
        buttons.append([
            InlineKeyboardButton(
                f"📢 {channel.get('channel_title', 'Unknown')}", 
                url=channel.get('channel_link', '#')
            ),
            InlineKeyboardButton(
                "🗑️", 
                callback_data=f"del_fsub_{channel['channel_id']}"
            )
        ])
    
    # Add new channel button
    buttons.append([
        InlineKeyboardButton("➕ Add Channel", callback_data="add_fsub")
    ])
    
    # Back button
    buttons.append([
        InlineKeyboardButton("🔙 Back", callback_data="admin_back")
    ])
    
    return InlineKeyboardMarkup(buttons)


def admin_broadcast_keyboard():
    """
    🛡️ BROADCAST CONFIRMATION
    """
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ Send to All", callback_data="broadcast_confirm"),
            InlineKeyboardButton("❌ Cancel", callback_data="broadcast_cancel")
        ]
    ])


def admin_stats_keyboard():
    """
    🛡️ STATS KE LIYE INLINE BUTTONS
    """
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("👥 Users", callback_data="stats_users"),
            InlineKeyboardButton("📂 Files", callback_data="stats_files")
        ],
        [
            InlineKeyboardButton("📊 Full Report", callback_data="stats_full"),
            InlineKeyboardButton("📥 Export", callback_data="stats_export")
        ]
    ])


# ═══════════════════════════════════════════════════════════════
# 👑 SUPER ADMIN KEYBOARDS
# ═══════════════════════════════════════════════════════════════

def superadmin_main_keyboard():
    """
    👑 SUPER ADMIN KA FULL CONTROL MENU
    
    📌 EXTRA FEATURES (vs Admin):
       - 👥 Manage Admins - Add/remove admins
       - 🚫 Ban Users - Ban/unban users
       - ⚙️ Bot Settings - Core settings
       - 🔄 Restart Bot - Restart command
       - 📜 Logs - View logs
    """
    return ReplyKeyboardMarkup(
        [
            [KeyboardButton("📤 Upload File"), KeyboardButton("📊 Stats")],
            [KeyboardButton("📢 Broadcast"), KeyboardButton("⚙️ Bot Settings")],
            [KeyboardButton("👥 Manage Admins"), KeyboardButton("🚫 Ban Users")],
            [KeyboardButton("📢 Channels"), KeyboardButton("📜 View Logs")],
            [KeyboardButton("🔄 Bot Status"), KeyboardButton("🗑️ Clear Database")]
        ],
        resize_keyboard=True
    )


def superadmin_manage_admins_keyboard(admins: list):
    """
    👑 ADMIN MANAGEMENT KEYBOARD
    
    📌 PARAMS:
        admins: List of admin IDs
    
    📌 SHOWS:
        - Current admins with remove button
        - Add new admin button
        - Super admin ko remove nahi kar sakte
    """
    from config import Config
    
    buttons = []
    
    for admin_id in admins:
        if admin_id == Config.SUPER_ADMIN:
            # Super admin - no remove button
            buttons.append([
                InlineKeyboardButton(f"👑 SUPER ADMIN ({admin_id})", callback_data="none")
            ])
        else:
            # Normal admin - can remove
            buttons.append([
                InlineKeyboardButton(f"🛡️ Admin ({admin_id})", callback_data="none"),
                InlineKeyboardButton("🗑️", callback_data=f"remove_admin_{admin_id}")
            ])
    
    # Add admin button
    buttons.append([
        InlineKeyboardButton("➕ Add New Admin", callback_data="add_admin_start")
    ])
    
    # Back button
    buttons.append([
        InlineKeyboardButton("🔙 Back", callback_data="admin_back")
    ])
    
    return InlineKeyboardMarkup(buttons)


def superadmin_ban_keyboard(banned_users: list):
    """
    👑 BAN MANAGEMENT KEYBOARD
    
    📌 PARAMS:
        banned_users: List of banned user dicts
    """
    buttons = []
    
    for user in banned_users[:10]:  # Show max 10
        buttons.append([
            InlineKeyboardButton(
                f"🚫 {user.get('name', 'Unknown')} ({user['id']})", 
                callback_data=f"unban_{user['id']}"
            )
        ])
    
    buttons.append([
        InlineKeyboardButton("🚫 Ban User (by ID)", callback_data="ban_user_start")
    ])
    
    buttons.append([
        InlineKeyboardButton("🔙 Back", callback_data="admin_back")
    ])
    
    return InlineKeyboardMarkup(buttons)


def superadmin_settings_keyboard():
    """
    👑 BOT SETTINGS KEYBOARD
    """
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("⏰ Auto Delete", callback_data="setting_auto_delete"),
            InlineKeyboardButton("📢 Force Sub", callback_data="setting_fsub")
        ],
        [
            InlineKeyboardButton("💸 Shortener", callback_data="setting_shortener"),
            InlineKeyboardButton("📝 Welcome Msg", callback_data="setting_welcome")
        ],
        [
            InlineKeyboardButton("🔧 Maintenance Mode", callback_data="setting_maintenance")
        ],
        [
            InlineKeyboardButton("🔙 Back", callback_data="admin_back")
        ]
    ])


def superadmin_bot_status_keyboard(is_running: bool = True):
    """
    👑 BOT STATUS & CONTROL
    """
    status_text = "🟢 Running" if is_running else "🔴 Stopped"
    
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(f"Status: {status_text}", callback_data="none")
        ],
        [
            InlineKeyboardButton("🔄 Restart Bot", callback_data="bot_restart"),
            InlineKeyboardButton("⚠️ Stop Bot", callback_data="bot_stop")
        ],
        [
            InlineKeyboardButton("📊 Live Stats", callback_data="bot_live_stats")
        ],
        [
            InlineKeyboardButton("🔙 Back", callback_data="admin_back")
        ]
    ])


# ═══════════════════════════════════════════════════════════════
# 🔗 SHARED KEYBOARDS
# ═══════════════════════════════════════════════════════════════

def force_sub_keyboard(channels: list, bot_username: str, start_arg: str = ""):
    """
    📢 FORCE SUB REQUIRED KEYBOARD
    
    📌 PARAMS:
        channels: List of channels to join
        bot_username: Bot's username
        start_arg: Original start argument
    
    📌 SHOWS:
        - Join buttons for each channel
        - Refresh button to check again
    """
    buttons = []
    
    for channel in channels:
        buttons.append([
            InlineKeyboardButton(
                f"📢 Join {channel.get('channel_title', 'Channel')}",
                url=channel.get('channel_link', '#')
            )
        ])
    
    # Refresh button
    refresh_url = f"https://t.me/{bot_username}?start={start_arg}" if start_arg else f"https://t.me/{bot_username}?start=refresh"
    buttons.append([
        InlineKeyboardButton("🔄 I've Joined - Refresh", url=refresh_url)
    ])
    
    return InlineKeyboardMarkup(buttons)


def file_delivery_keyboard(file_id: str, short_url: str = None):
    """
    📂 FILE DOWNLOAD KEYBOARD
    
    📌 PARAMS:
        file_id: Unique file identifier
        short_url: Shortener URL (if enabled)
    """
    buttons = []
    
    if short_url:
        buttons.append([
            InlineKeyboardButton("🔓 CLICK TO UNLOCK FILE", url=short_url)
        ])
    else:
        buttons.append([
            InlineKeyboardButton("📥 Download File", callback_data=f"download_{file_id}")
        ])
    
    return InlineKeyboardMarkup(buttons)


def share_keyboard(text: str):
    """
    📤 SHARE BUTTON KEYBOARD
    
    📌 USAGE:
        After file upload, share link with this button
    """
    import urllib.parse
    encoded_text = urllib.parse.quote(text)
    
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("📤 Share", url=f"https://t.me/share/url?url={encoded_text}")
        ],
        [
            InlineKeyboardButton("📋 Copy Link", callback_data="copy_link")
        ]
    ])


def back_keyboard(callback_data: str = "admin_back"):
    """
    🔙 SIMPLE BACK BUTTON
    """
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 Back", callback_data=callback_data)]
    ])


def confirm_keyboard(action: str, item_id: str = ""):
    """
    ✅ CONFIRMATION KEYBOARD
    
    📌 PARAMS:
        action: Action to confirm (delete, ban, etc.)
        item_id: Item ID for action
    """
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ Confirm", callback_data=f"confirm_{action}_{item_id}"),
            InlineKeyboardButton("❌ Cancel", callback_data="cancel")
        ]
    ])


# ═══════════════════════════════════════════════════════════════
# 🎯 KEYBOARD HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════

def get_role_keyboard(user_id: int):
    """
    User ke role ke hisaab se keyboard return karta hai
    
    📌 PARAMS:
        user_id: Telegram user ID
    
    📌 RETURNS:
        Appropriate keyboard for user's role
    """
    from config import Config, is_super_admin, is_admin
    
    if is_super_admin(user_id):
        return superadmin_main_keyboard()
    elif is_admin(user_id):
        return admin_main_keyboard()
    else:
        return user_main_keyboard()


# ═══════════════════════════════════════════════════════════════
# ✅ ALL KEYBOARDS DEFINED!
# ═══════════════════════════════════════════════════════════════
