# ═══════════════════════════════════════════════════════════════
# ⏰ utils/auto_delete.py - AUTO DELETE SCHEDULER
# ═══════════════════════════════════════════════════════════════
#
# 📌 KYUN USE HOTA HAI?
#    - Files ko automatically delete karta hai X hours baad
#    - Database space bachata hai
#    - Security: Files permanent nahi rehti
#
# 📌 HOW IT WORKS:
#    1. Scheduler har 1 hour check karta hai
#    2. Files jo delete_at time se guzar chuki hain
#    3. Database se delete karta hai
# ═══════════════════════════════════════════════════════════════

import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime
from config import Config
from database.db import db


# Scheduler instance
scheduler = AsyncIOScheduler()


# ───────────────────────────────────────────────────────────────
# 🗑️ AUTO DELETE FUNCTION
# ───────────────────────────────────────────────────────────────

async def delete_expired_files():
    """
    Expired files ko delete karta hai
    
    📌 LOGIC:
        1. Database se files nikal jinka delete_at time expire ho chuka
        2. Har file ko delete karo
        3. Count print karo
    
    📌 SCHEDULE:
        Har 1 hour mein ye function run hota hai
    """
    print("⏰ Checking for expired files...")
    
    try:
        # Get expired files from database
        expired_files = await db.get_files_to_delete()
        
        if not expired_files:
            print("✅ No expired files found")
            return
        
        print(f"🗑️ Found {len(expired_files)} expired files")
        
        # Delete each file
        deleted_count = 0
        for file in expired_files:
            try:
                await db.delete_file(file['file_unique_id'])
                deleted_count += 1
                print(f"   🗑️ Deleted: {file.get('file_name', 'Unknown')}")
            except Exception as e:
                print(f"   ❌ Error deleting {file['file_unique_id']}: {e}")
        
        print(f"✅ Auto delete complete: {deleted_count} files removed")
        
    except Exception as e:
        print(f"❌ Auto delete error: {e}")


# ───────────────────────────────────────────────────────────────
# 🚀 START SCHEDULER
# ───────────────────────────────────────────────────────────────

async def start_auto_delete_scheduler():
    """
    Scheduler ko start karta hai
    
    📌 WHEN TO CALL:
        Bot start hone par (main.py mein)
    
    📌 SCHEDULE:
        - Check every 1 hour (3600 seconds)
        - Can be changed via IntervalTrigger
    """
    # Check if auto delete is enabled
    if Config.AUTO_DELETE_HOURS <= 0:
        print("⏰ Auto delete is disabled (AUTO_DELETE_HOURS = 0)")
        return
    
    # Add job to scheduler
    scheduler.add_job(
        delete_expired_files,
        trigger=IntervalTrigger(hours=1),  # Check every 1 hour
        id="auto_delete_files",
        name="Delete expired files",
        replace_existing=True
    )
    
    # Start scheduler
    scheduler.start()
    
    print(f"⏰ Auto Delete Scheduler Started (Files deleted after {Config.AUTO_DELETE_HOURS} hours)")
    
    # Run first check immediately
    await delete_expired_files()


# ───────────────────────────────────────────────────────────────
# 🛑 STOP SCHEDULER
# ───────────────────────────────────────────────────────────────

async def stop_auto_delete_scheduler():
    """
    Scheduler ko stop karta hai
    
    📌 WHEN TO CALL:
        Bot stop hone par (optional)
    """
    if scheduler.running:
        scheduler.shutdown()
        print("⏰ Auto Delete Scheduler Stopped")


# ───────────────────────────────────────────────────────────────
# 📊 SCHEDULER STATUS
# ───────────────────────────────────────────────────────────────

def get_scheduler_status() -> dict:
    """
    Scheduler ka status return karta hai
    
    📌 RETURNS:
        dict: {
            "running": bool,
            "next_run": str,
            "auto_delete_hours": int
        }
    """
    status = {
        "running": scheduler.running,
        "next_run": "Not scheduled",
        "auto_delete_hours": Config.AUTO_DELETE_HOURS
    }
    
    if scheduler.running:
        job = scheduler.get_job("auto_delete_files")
        if job:
            status["next_run"] = str(job.next_run_time)
    
    return status


# ───────────────────────────────────────────────────────────────
# 🔧 MANUAL TRIGGER
# ───────────────────────────────────────────────────────────────

async def trigger_manual_delete():
    """
    Manually trigger file deletion
    
    📌 USE CASE:
        Admin command se manually files delete karo
    """
    print("🔧 Manual delete triggered")
    await delete_expired_files()


# ───────────────────────────────────────────────────────────────
# 📋 GET EXPIRING FILES
# ───────────────────────────────────────────────────────────────

async def get_expiring_files_count() -> int:
    """
    Kitni files delete honi hain count karta hai
    
    📌 RETURNS:
        int: Number of files to be deleted
    """
    files = await db.get_files_to_delete()
    return len(files)


async def get_expiring_files_list(limit: int = 10) -> list:
    """
    Delete hone wali files ki list deta hai
    
    📌 PARAMS:
        limit: Maximum files to return
    
    📌 RETURNS:
        list: List of file dicts
    """
    files = await db.get_files_to_delete()
    return files[:limit]


# ═══════════════════════════════════════════════════════════════
# ✅ AUTO DELETE MODULE READY!
#
# 📌 USAGE:
#    from utils.auto_delete import start_auto_delete_scheduler
#    await start_auto_delete_scheduler()  # Call in main.py
#
# 📌 CONFIG:
#    Set AUTO_DELETE_HOURS in .env file
#    0 = disabled
#    24 = delete after 24 hours
# ═══════════════════════════════════════════════════════════════
