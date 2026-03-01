# ═══════════════════════════════════════════════════════════════
# 🗄️ database/db.py - DATABASE MANAGEMENT
# ═══════════════════════════════════════════════════════════════
#
# 📌 KYUN USE HOTA HAI?
#    - Saare data ko store karne ke liye (users, files, settings)
#    - SQLite use kar rahe hain (file-based, no server needed)
#    - Async operations for better performance
#
# 📌 TABLES:
#    1. users - User data (ID, name, join date)
#    2. admins - Additional admins (besides super admin)
#    3. files - Uploaded files info
#    4. fsub_channels - Force sub channels
#    5. pending_requests - Join requests
# ═══════════════════════════════════════════════════════════════

import aiosqlite
import json
import time
from config import Config


class Database:
    """
    ═══════════════════════════════════════════════════════════
    🗄️ DATABASE CLASS
    ═══════════════════════════════════════════════════════════
    Ye class saare database operations handle karti hai.
    Async methods hain, non-blocking operations.
    ═══════════════════════════════════════════════════════════
    """
    
    def __init__(self):
        """
        Constructor: Database file ka naam set karta hai
        
        📌 DB_NAME: SQLite file ka naam (config.py se aata hai)
        """
        self.db_name = Config.DB_NAME

    # ══════════════════════════════════════════════════════════
    # 🏗️ INITIALIZATION
    # ══════════════════════════════════════════════════════════
    
    async def init(self):
        """
        Database ko initialize karta hai
        
        📌 KYA KARTA HAI?
           - SQLite database file create karta hai (agar nahi hai)
           - Saari tables create karta hai
           - WAL mode enable karta hai (better performance)
           - timeout set karta hai (lock prevent)
        
        📌 RETURNS: None
        📌 RAISES: Exception agar kuch galat ho
        """
        # timeout=20: Agar database locked hai, 20 seconds wait karega
        async with aiosqlite.connect(self.db_name, timeout=20) as db:
            
            # WAL MODE: Write-Ahead Logging
            # Better performance, less locking issues
            await db.execute("PRAGMA journal_mode=WAL;")
            
            # ───────────────────────────────────────────────────
            # TABLE 1: USERS
            # ───────────────────────────────────────────────────
            # User ki basic info store karta hai
            await db.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY,
                    name TEXT,
                    username TEXT,
                    joined_date REAL,
                    is_banned INTEGER DEFAULT 0,
                    ban_reason TEXT,
                    shortener_history TEXT,
                    files_downloaded INTEGER DEFAULT 0
                )
            """)
            
            # ───────────────────────────────────────────────────
            # TABLE 2: ADMINS (Multi-Admin Support)
            # ───────────────────────────────────────────────────
            # Additional admins (Super admin config.py mein hai)
            await db.execute("""
                CREATE TABLE IF NOT EXISTS admins (
                    user_id INTEGER PRIMARY KEY,
                    added_by INTEGER,
                    added_date REAL,
                    permissions TEXT
                )
            """)
            
            # ───────────────────────────────────────────────────
            # TABLE 3: FILES
            # ───────────────────────────────────────────────────
            # Uploaded files ka data (ADDED: use_shortener)
            await db.execute("""
                CREATE TABLE IF NOT EXISTS files (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    file_unique_id TEXT UNIQUE,
                    file_id TEXT,
                    file_name TEXT,
                    file_size INTEGER,
                    file_type TEXT,
                    caption TEXT,
                    batch_id TEXT,
                    upload_date REAL,
                    delete_at REAL,
                    views INTEGER DEFAULT 0,
                    uploaded_by INTEGER,
                    use_shortener INTEGER DEFAULT 0
                )
            """)
            
            # 🔥 MIGRATION SCRIPT 🔥
            # Agar DB purana hai, toh use_shortener column add kar dega automatically
            try:
                await db.execute("ALTER TABLE files ADD COLUMN use_shortener INTEGER DEFAULT 0")
            except Exception:
                pass # Agar column pehle se hai toh error ignore karega
            
            # ───────────────────────────────────────────────────
            # TABLE 4: FORCE SUB CHANNELS
            # ───────────────────────────────────────────────────
            # Multiple channels support
            await db.execute("""
                CREATE TABLE IF NOT EXISTS fsub_channels (
                    channel_id INTEGER PRIMARY KEY,
                    channel_title TEXT,
                    channel_link TEXT,
                    added_by INTEGER,
                    added_date REAL
                )
            """)
            
            # ───────────────────────────────────────────────────
            # TABLE 5: PENDING JOIN REQUESTS
            # ───────────────────────────────────────────────────
            # Private channel join requests
            await db.execute("""
                CREATE TABLE IF NOT EXISTS pending_requests (
                    user_id INTEGER,
                    channel_id INTEGER,
                    request_date REAL,
                    PRIMARY KEY (user_id, channel_id)
                )
            """)
            
            # ───────────────────────────────────────────────────
            # TABLE 6: BOT SETTINGS
            # ───────────────────────────────────────────────────
            # Dynamic bot settings
            await db.execute("""
                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT,
                    updated_by INTEGER,
                    updated_date REAL
                )
            """)

            await db.commit()
            print("✅ Database Tables Created/Updated successfully!")

    # ══════════════════════════════════════════════════════════
    # 👤 USER MANAGEMENT
    # ══════════════════════════════════════════════════════════
    
    async def add_user(self, user_id: int, name: str, username: str = None):
        """
        Naya user add karta hai (agar already nahi hai)
        
        📌 PARAMS:
            user_id: Telegram user ID
            name: User ka first name
            username: User ka @username (optional)
        
        📌 RETURNS:
            True: agar new user added
            False: agar already exists
        """
        async with aiosqlite.connect(self.db_name, timeout=20) as db:
            try:
                # Check if user exists
                cursor = await db.execute("SELECT id FROM users WHERE id = ?", (user_id,))
                if await cursor.fetchone():
                    return False
                
                # Add new user
                default_history = json.dumps({"last_shortener_index": -1})
                
                await db.execute(
                    """INSERT INTO users 
                       (id, name, username, joined_date, shortener_history) 
                       VALUES (?, ?, ?, ?, ?)""",
                    (user_id, name, username, time.time(), default_history)
                )
                await db.commit()
                return True
                
            except Exception as e:
                print(f"❌ Error adding user: {e}")
                return False

    async def get_user(self, user_id: int):
        """
        User ka data laata hai
        
        📌 PARAMS:
            user_id: Telegram user ID
        
        📌 RETURNS:
            dict: user data agar mila
            None: agar nahi mila
        """
        async with aiosqlite.connect(self.db_name, timeout=20) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute("SELECT * FROM users WHERE id = ?", (user_id,))
            row = await cursor.fetchone()
            return dict(row) if row else None

    async def total_users(self) -> int:
        """
        Total users count karta hai
        """
        async with aiosqlite.connect(self.db_name, timeout=20) as db:
            cursor = await db.execute("SELECT COUNT(*) FROM users")
            row = await cursor.fetchone()
            return row[0] if row else 0

    async def get_all_users(self) -> list:
        """
        Saare user IDs ki list laata hai
        Broadcast ke liye use hota hai
        """
        async with aiosqlite.connect(self.db_name, timeout=20) as db:
            cursor = await db.execute("SELECT id FROM users WHERE is_banned = 0")
            rows = await cursor.fetchall()
            return [row[0] for row in rows]

    async def ban_user(self, user_id: int, reason: str = ""):
        """
        User ko ban karta hai
        """
        async with aiosqlite.connect(self.db_name, timeout=20) as db:
            await db.execute(
                "UPDATE users SET is_banned = 1, ban_reason = ? WHERE id = ?",
                (reason, user_id)
            )
            await db.commit()

    async def unban_user(self, user_id: int):
        """
        User ka ban hataata hai
        """
        async with aiosqlite.connect(self.db_name, timeout=20) as db:
            await db.execute(
                "UPDATE users SET is_banned = 0, ban_reason = NULL WHERE id = ?",
                (user_id,)
            )
            await db.commit()

    async def is_banned(self, user_id: int) -> bool:
        """
        Check karta hai user banned hai ya nahi
        """
        async with aiosqlite.connect(self.db_name, timeout=20) as db:
            cursor = await db.execute(
                "SELECT is_banned FROM users WHERE id = ?", (user_id,)
            )
            row = await cursor.fetchone()
            return bool(row and row[0])

    # ══════════════════════════════════════════════════════════
    # 🛡️ ADMIN MANAGEMENT
    # ══════════════════════════════════════════════════════════
    
    async def add_admin(self, user_id: int, added_by: int, permissions: list = None):
        """
        Naya admin add karta hai
        
        📌 PARAMS:
            user_id: New admin ka ID
            added_by: Kisne add kiya (super admin)
            permissions: List of permissions (optional)
        """
        async with aiosqlite.connect(self.db_name, timeout=20) as db:
            perms = json.dumps(permissions or ["upload", "stats", "fsub"])
            await db.execute(
                """INSERT OR REPLACE INTO admins 
                   (user_id, added_by, added_date, permissions) 
                   VALUES (?, ?, ?, ?)""",
                (user_id, added_by, time.time(), perms)
            )
            await db.commit()

    async def remove_admin(self, user_id: int):
        """
        Admin remove karta hai
        Note: Super admin ko remove nahi kar sakte
        """
        async with aiosqlite.connect(self.db_name, timeout=20) as db:
            await db.execute("DELETE FROM admins WHERE user_id = ?", (user_id,))
            await db.commit()

    async def is_admin(self, user_id: int) -> bool:
        """
        Check karta hai user admin hai ya nahi
        (Super admin bhi admin hota hai)
        """
        # Super admin check
        if user_id == Config.SUPER_ADMIN:
            return True
        
        # Database check
        async with aiosqlite.connect(self.db_name, timeout=20) as db:
            cursor = await db.execute("SELECT user_id FROM admins WHERE user_id = ?", (user_id,))
            return bool(await cursor.fetchone())

    async def get_all_admins(self) -> list:
        """
        Saare admins ki list laata hai (including super admin)
        """
        admins = [Config.SUPER_ADMIN]  # Super admin add karo
        
        async with aiosqlite.connect(self.db_name, timeout=20) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute("SELECT * FROM admins")
            rows = await cursor.fetchall()
            for row in rows:
                if row["user_id"] not in admins:
                    admins.append(row["user_id"])
        
        return admins

    # ══════════════════════════════════════════════════════════
    # 📂 FILE MANAGEMENT
    # ══════════════════════════════════════════════════════════
    
    async def add_file(self, file_info: dict):
        """
        File ka data save karta hai
        
        📌 PARAMS (file_info dict):
            file_unique_id: Telegram unique ID
            file_id: Telegram file ID (for sending)
            file_name: File ka naam
            file_size: Size in bytes
            file_type: document/video/audio/photo
            caption: File caption
            batch_id: Album ke liye common ID
            uploaded_by: Admin ID
            delete_at: Delete timestamp (auto delete)
            use_shortener: Boolean if shortener is needed or not
        
        📌 RETURNS: file_info dict
        """
        async with aiosqlite.connect(self.db_name, timeout=20) as db:
            try:
                # Shortener ki value properly 1 (Yes) ya 0 (No) save karna
                is_shortener = 1 if file_info.get('use_shortener') else 0
                
                await db.execute(
                    """INSERT INTO files 
                       (file_unique_id, file_id, file_name, file_size, file_type, 
                        caption, batch_id, upload_date, delete_at, views, uploaded_by, use_shortener) 
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (
                        file_info['file_unique_id'],
                        file_info['file_id'],
                        file_info.get('file_name', 'Unknown'),
                        file_info.get('file_size', 0),
                        file_info.get('file_type', 'document'),
                        file_info.get('caption', ''),
                        file_info.get('batch_id'),
                        time.time(),
                        file_info.get('delete_at'),
                        0,
                        file_info.get('uploaded_by'),
                        is_shortener
                    )
                )
                await db.commit()
                return file_info
            except Exception as e:
                print(f"❌ Error adding file: {e}")
                return None

    async def get_file(self, file_unique_id: str):
        """
        File ka data laata hai
        """
        async with aiosqlite.connect(self.db_name, timeout=20) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                "SELECT * FROM files WHERE file_unique_id = ?", 
                (file_unique_id,)
            )
            row = await cursor.fetchone()
            return dict(row) if row else None

    async def get_files_by_batch(self, batch_id: str):
        """
        Batch/Album ki saari files laata hai
        """
        async with aiosqlite.connect(self.db_name, timeout=20) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                "SELECT * FROM files WHERE batch_id = ? ORDER BY id", 
                (batch_id,)
            )
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

    async def delete_file(self, file_unique_id: str):
        """
        File delete karta hai (DB se)
        """
        async with aiosqlite.connect(self.db_name, timeout=20) as db:
            await db.execute("DELETE FROM files WHERE file_unique_id = ?", (file_unique_id,))
            await db.commit()

    async def delete_batch(self, batch_id: str):
        """
        Poori batch delete karta hai
        """
        async with aiosqlite.connect(self.db_name, timeout=20) as db:
            await db.execute("DELETE FROM files WHERE batch_id = ?", (batch_id,))
            await db.commit()

    async def get_files_to_delete(self):
        """
        Files jo delete honi chahiye (auto delete ke liye)
        """
        async with aiosqlite.connect(self.db_name, timeout=20) as db:
            db.row_factory = aiosqlite.Row
            current_time = time.time()
            cursor = await db.execute(
                "SELECT * FROM files WHERE delete_at IS NOT NULL AND delete_at <= ?",
                (current_time,)
            )
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

    async def total_files(self) -> int:
        """
        Total files count
        """
        async with aiosqlite.connect(self.db_name, timeout=20) as db:
            cursor = await db.execute("SELECT COUNT(*) FROM files")
            row = await cursor.fetchone()
            return row[0] if row else 0

    async def increment_file_views(self, file_unique_id: str):
        """
        File views badhata hai
        """
        async with aiosqlite.connect(self.db_name, timeout=20) as db:
            await db.execute(
                "UPDATE files SET views = views + 1 WHERE file_unique_id = ?",
                (file_unique_id,)
            )
            await db.commit()

    # ══════════════════════════════════════════════════════════
    # 📢 FORCE SUB CHANNELS
    # ══════════════════════════════════════════════════════════
    
    async def add_fsub_channel(self, channel_id: int, title: str, link: str, added_by: int):
        """
        Force sub channel add karta hai
        """
        async with aiosqlite.connect(self.db_name, timeout=20) as db:
            await db.execute(
                """INSERT OR REPLACE INTO fsub_channels 
                   (channel_id, channel_title, channel_link, added_by, added_date) 
                   VALUES (?, ?, ?, ?, ?)""",
                (channel_id, title, link, added_by, time.time())
            )
            await db.commit()

    async def remove_fsub_channel(self, channel_id: int):
        """
        Force sub channel remove karta hai
        """
        async with aiosqlite.connect(self.db_name, timeout=20) as db:
            await db.execute("DELETE FROM fsub_channels WHERE channel_id = ?", (channel_id,))
            await db.commit()

    async def get_fsub_channels(self) -> list:
        """
        Saari force sub channels laata hai
        """
        async with aiosqlite.connect(self.db_name, timeout=20) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute("SELECT * FROM fsub_channels")
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

    # ══════════════════════════════════════════════════════════
    # ⏳ PENDING JOIN REQUESTS
    # ══════════════════════════════════════════════════════════
    
    async def add_join_request(self, user_id: int, channel_id: int):
        """
        Join request save karta hai
        """
        async with aiosqlite.connect(self.db_name, timeout=20) as db:
            await db.execute(
                """INSERT OR IGNORE INTO pending_requests 
                   (user_id, channel_id, request_date) 
                   VALUES (?, ?, ?)""",
                (user_id, channel_id, time.time())
            )
            await db.commit()

    async def is_join_request_pending(self, user_id: int, channel_id: int) -> bool:
        """
        Check karta hai ki join request pending hai ya nahi
        """
        async with aiosqlite.connect(self.db_name, timeout=20) as db:
            cursor = await db.execute(
                "SELECT * FROM pending_requests WHERE user_id = ? AND channel_id = ?",
                (user_id, channel_id)
            )
            return bool(await cursor.fetchone())

    async def remove_join_request(self, user_id: int, channel_id: int):
        """
        Join request remove karta hai (jab user join kare)
        """
        async with aiosqlite.connect(self.db_name, timeout=20) as db:
            await db.execute(
                "DELETE FROM pending_requests WHERE user_id = ? AND channel_id = ?",
                (user_id, channel_id)
            )
            await db.commit()

    # ══════════════════════════════════════════════════════════
    # 🔄 SHORTENER ROTATION
    # ══════════════════════════════════════════════════════════
    
    async def get_next_shortener_index(self, user_id: int, total_shorteners: int) -> int:
        """
        Round-robin shortener rotation
        
        📌 LOGIC:
           Har user ko alag shortener milta hai sequence mein
           User 1 -> Shortener 1
           User 2 -> Shortener 2
           User 3 -> Shortener 1 (wapas)
        
        📌 RETURNS: Index (0, 1, 2...)
        """
        async with aiosqlite.connect(self.db_name, timeout=20) as db:
            try:
                cursor = await db.execute(
                    "SELECT shortener_history FROM users WHERE id = ?", 
                    (user_id,)
                )
                row = await cursor.fetchone()
                
                history = {}
                if row and row[0]:
                    try:
                        history = json.loads(row[0])
                    except:
                        pass
                
                last_index = history.get("last_shortener_index", -1)
                next_index = (last_index + 1) % total_shorteners
                
                # Update
                history["last_shortener_index"] = next_index
                await db.execute(
                    "UPDATE users SET shortener_history = ? WHERE id = ?",
                    (json.dumps(history), user_id)
                )
                await db.commit()
                
                return next_index
                
            except Exception as e:
                print(f"❌ Rotation Error: {e}")
                return 0


# ───────────────────────────────────────────────────────────────
# 🎯 DATABASE INSTANCE
# ───────────────────────────────────────────────────────────────
# Ye instance dusri files mein import hoga
# Usage: from database.db import db

db = Database()