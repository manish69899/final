# ═══════════════════════════════════════════════════════════════
# 👆 plugins/callback.py - CALLBACK QUERY HANDLER
# ═══════════════════════════════════════════════════════════════
#
# 📌 KYUN USE HOTA HAI?
#    - Saare button clicks handle karta hai
#    - Inline keyboard callbacks
#
# 📌 CALLBACKS:
#    - about - About info
#    - admin_back - Back to admin menu
#    - broadcast_confirm - Confirm broadcast
#    - del_fsub_* - Delete force sub channel
#    - remove_admin_* - Remove admin
# ═══════════════════════════════════════════════════════════════

from pyrogram import Client, filters
from pyrogram.types import CallbackQuery
from config import Config
from database.db import db
from utils.keyboard import back_keyboard
from utils.commands import update_user_commands, remove_admin_commands
from utils.logger import log_fsub_removed, log_admin_removed
import asyncio


# ═══════════════════════════════════════════════════════════════
# ℹ️ ABOUT CALLBACK
# ═══════════════════════════════════════════════════════════════

@Client.on_callback_query(filters.regex("about"))
async def about_callback(client: Client, callback: CallbackQuery):
    """
    About button callback
    """
    total_users = await db.total_users()
    total_files = await db.total_files()
    
    about_text = f"""
ℹ️ **About This Bot**

ʟᴏᴄᴀʟʜᴏꜱᴛ.exe
Real Identity: ARYAN

Made by Localhost.
Not hosted. Not owned. Just deployed.
Built in silence.
Tested in chaos.
Deployed with caffeine.

Half lazy. Half genius.
Full power mode when it matters.

This bot isn’t just code.
It’s late night debugging sessions,
random idea explosions,
and that one stubborn bug that refused to die.

Minimal outside.
Savage inside.

If it works smoothly… respect the architecture.
If it breaks… it’s a feature in development 😌

Welcome to the system.
Stay sharp. Stay smart. Stay slightly dangerous. ⚡

"""
    
    await callback.message.edit_text(
        about_text,
        reply_markup=back_keyboard("main_menu")
    )


# ═══════════════════════════════════════════════════════════════
# 🔙 BACK CALLBACKS
# ═══════════════════════════════════════════════════════════════

@Client.on_callback_query(filters.regex("admin_back"))
async def admin_back_callback(client: Client, callback: CallbackQuery):
    """
    Back to admin menu
    """
    await callback.message.delete()


@Client.on_callback_query(filters.regex("main_menu"))
async def main_menu_callback(client: Client, callback: CallbackQuery):
    """
    Back to main menu
    """
    await callback.message.delete()


# ═══════════════════════════════════════════════════════════════
# 📢 BROADCAST CALLBACKS
# ═══════════════════════════════════════════════════════════════

@Client.on_callback_query(filters.regex("broadcast_confirm"))
async def broadcast_confirm_callback(client: Client, callback: CallbackQuery):
    """
    Confirm broadcast
    """
    user_id = callback.from_user.id
    
    # Check admin
    if not await db.is_admin(user_id):
        await callback.answer("❌ Admins only!", show_alert=True)
        return
    
    # Get users
    all_users = await db.get_all_users()
    
    if not all_users:
        await callback.answer("❌ No users to broadcast!", show_alert=True)
        return
    
    # Update message
    await callback.message.edit_text(
        f"📢 **Broadcast Started...**\n\n👥 Sending to {len(all_users)} users..."
    )
    
    # Get original message (the one admin wants to broadcast)
    # This is stored in the replied message
    original_msg = callback.message.reply_to_message
    
    if not original_msg:
        await callback.message.edit_text("❌ Original message not found!")
        return
    
    # Broadcast
    success = 0
    failed = 0
    
    for uid in all_users:
        try:
            await original_msg.copy(chat_id=uid)
            success += 1
        except:
            failed += 1
        
        if (success + failed) % 20 == 0:
            try:
                await callback.message.edit_text(
                    f"📢 **Broadcasting...**\n\n✅ {success}\n❌ {failed}"
                )
            except:
                pass
        
        await asyncio.sleep(0.05)
    
    # Final
    await callback.message.edit_text(
        f"📢 **Broadcast Complete!**\n\n✅ Success: {success}\n❌ Failed: {failed}"
    )


@Client.on_callback_query(filters.regex("broadcast_cancel"))
async def broadcast_cancel_callback(client: Client, callback: CallbackQuery):
    """
    Cancel broadcast
    """
    await callback.message.edit_text("❌ **Broadcast Cancelled!**")


# ═══════════════════════════════════════════════════════════════
# 📢 FORCE SUB CALLBACKS
# ═══════════════════════════════════════════════════════════════

@Client.on_callback_query(filters.regex(r"del_fsub_(-?\d+)"))
async def delete_fsub_callback(client: Client, callback: CallbackQuery):
    """
    Delete force sub channel
    """
    user_id = callback.from_user.id
    
    # Check admin
    if not await db.is_admin(user_id):
        await callback.answer("❌ Admins only!", show_alert=True)
        return
    
    # Extract channel ID
    channel_id = int(callback.data.split("_")[-1])
    
    # Delete
    await db.remove_fsub_channel(channel_id)
    
    # Log
    await log_fsub_removed(client, channel_id, user_id)
    
    await callback.answer("✅ Channel removed!", show_alert=True)
    
    # Update list
    channels = await db.get_fsub_channels()
    
    if not channels:
        await callback.message.edit_text("📭 No force sub channels.")
    else:
        from utils.keyboard import admin_fsub_keyboard
        await callback.message.edit_text(
            "📋 **Updated Channel List:**",
            reply_markup=admin_fsub_keyboard(channels)
        )


# ═══════════════════════════════════════════════════════════════
# 🛡️ ADMIN MANAGEMENT CALLBACKS
# ═══════════════════════════════════════════════════════════════

@Client.on_callback_query(filters.regex(r"remove_admin_(\d+)"))
async def remove_admin_callback(client: Client, callback: CallbackQuery):
    """
    Remove admin callback
    """
    user_id = callback.from_user.id
    
    # Only super admin
    if user_id != Config.SUPER_ADMIN:
        await callback.answer("👑 Super Admin only!", show_alert=True)
        return
    
    # Extract admin ID
    admin_id = int(callback.data.split("_")[-1])
    
    # Can't remove super admin
    if admin_id == Config.SUPER_ADMIN:
        await callback.answer("⚠️ Can't remove Super Admin!", show_alert=True)
        return
    
    # Remove
    await db.remove_admin(admin_id)
    
    # Update commands
    await remove_admin_commands(client, admin_id)
    
    # Log
    await log_admin_removed(client, admin_id, user_id)
    
    await callback.answer("✅ Admin removed!", show_alert=True)
    
    # Update list
    from utils.keyboard import superadmin_manage_admins_keyboard
    admins = await db.get_all_admins()
    await callback.message.edit_text(
        "👥 **Updated Admin List:**",
        reply_markup=superadmin_manage_admins_keyboard(admins)
    )


# ═══════════════════════════════════════════════════════════════
# 🚫 BAN CALLBACKS
# ═══════════════════════════════════════════════════════════════

@Client.on_callback_query(filters.regex(r"unban_(\d+)"))
async def unban_callback(client: Client, callback: CallbackQuery):
    """
    Unban user callback
    """
    user_id = callback.from_user.id
    
    # Only super admin
    if user_id != Config.SUPER_ADMIN:
        await callback.answer("👑 Super Admin only!", show_alert=True)
        return
    
    # Extract user ID
    unban_id = int(callback.data.split("_")[-1])
    
    # Unban
    await db.unban_user(unban_id)
    
    await callback.answer("✅ User unbanned!", show_alert=True)
    await callback.message.delete()


# ═══════════════════════════════════════════════════════════════
# ⚙️ SETTINGS CALLBACKS
# ═══════════════════════════════════════════════════════════════

@Client.on_callback_query(filters.regex("setting_auto_delete"))
async def setting_auto_delete_callback(client: Client, callback: CallbackQuery):
    """
    Auto delete settings
    """
    await callback.answer(
        f"Auto Delete: {Config.AUTO_DELETE_HOURS} hours\nChange in .env file",
        show_alert=True
    )


@Client.on_callback_query(filters.regex("setting_fsub"))
async def setting_fsub_callback(client: Client, callback: CallbackQuery):
    """
    Force sub settings
    """
    channels = await db.get_fsub_channels()
    await callback.answer(
        f"Force Sub Channels: {len(channels)}\nUse /fsub_list to manage",
        show_alert=True
    )


@Client.on_callback_query(filters.regex("setting_shortener"))
async def setting_shortener_callback(client: Client, callback: CallbackQuery):
    """
    Shortener settings
    """
    count = len(Config.SHORTENERS)
    await callback.answer(
        f"Shorteners: {count}\nChange in .env file",
        show_alert=True
    )


# ═══════════════════════════════════════════════════════════════
# 📊 STATS CALLBACKS
# ═══════════════════════════════════════════════════════════════

@Client.on_callback_query(filters.regex("stats_users"))
async def stats_users_callback(client: Client, callback: CallbackQuery):
    """
    User stats
    """
    total = await db.total_users()
    await callback.answer(f"👥 Total Users: {total}", show_alert=True)


@Client.on_callback_query(filters.regex("stats_files"))
async def stats_files_callback(client: Client, callback: CallbackQuery):
    """
    File stats
    """
    total = await db.total_files()
    await callback.answer(f"📂 Total Files: {total}", show_alert=True)


# ═══════════════════════════════════════════════════════════════
# ❌ CANCEL CALLBACK
# ═══════════════════════════════════════════════════════════════

@Client.on_callback_query(filters.regex("cancel"))
async def cancel_callback(client: Client, callback: CallbackQuery):
    """
    Generic cancel callback
    """
    await callback.message.delete()


@Client.on_callback_query(filters.regex("none"))
async def none_callback(client: Client, callback: CallbackQuery):
    """
    Do nothing callback (for non-clickable buttons)
    """
    await callback.answer()


# ═══════════════════════════════════════════════════════════════
# ✅ CALLBACK PLUGIN READY!
# ═══════════════════════════════════════════════════════════════
