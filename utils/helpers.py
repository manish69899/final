# ═══════════════════════════════════════════════════════════════
# 🔧 utils/helpers.py - HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════
#
# 📌 KYUN USE HOTA HAI?
#    - Common functions jo multiple files mein use hote hain
#    - Code reuse ke liye
#    - Clean code maintenance
#
# 📌 FUNCTIONS:
#    - generate_unique_id() - Short unique IDs
#    - get_file_id() - File info from message
#    - format_size() - Bytes to human readable
#    - time_ago() - Timestamp to readable time
# ═══════════════════════════════════════════════════════════════

from hashids import Hashids
import time
from datetime import datetime


# ───────────────────────────────────────────────────────────────
# 🔑 UNIQUE ID GENERATOR
# ───────────────────────────────────────────────────────────────

# Hashids instance for generating short unique IDs
# Salt change karke apni custom IDs bana sakte ho
_hashids = Hashids(salt="FileBotSecretSalt2024", min_length=6)


def generate_unique_id() -> str:
    """
    Short unique ID generate karta hai
    
    📌 KYA KARTA HAI:
        - Current timestamp use karke unique ID banata hai
        - 6+ characters ka short code
        - Example: "aB3xY9"
    
    📌 USE CASE:
        - File links ke liye unique codes
        - Batch IDs ke liye
    
    📌 RETURNS:
        str: Unique ID like "aB3xY9"
    
    📌 EXAMPLE:
        >>> generate_unique_id()
        'aB3xY9'
        >>> generate_unique_id()
        'kL7mN2'
    """
    # Current time in milliseconds
    timestamp = int(time.time() * 1000)
    return _hashids.encode(timestamp)


def generate_batch_id() -> str:
    """
    Batch/Album ke liye unique ID
    
    📌 DIFFERENCE from generate_unique_id:
        - "batch_" prefix add hota hai
        - Easy identification
    
    📌 RETURNS:
        str: "batch_aB3xY9"
    """
    return f"batch_{generate_unique_id()}"


# ───────────────────────────────────────────────────────────────
# 📂 FILE HELPERS
# ───────────────────────────────────────────────────────────────

def get_file_id(message):
    """
    Message se file info extract karta hai
    
    📌 PARAMS:
        message: Pyrogram message object
    
    📌 RETURNS:
        tuple: (file_id, file_unique_id, file_name, file_size, file_type)
        None: agar file nahi hai
    
    📌 SUPPORTED TYPES:
        - document (PDF, ZIP, etc.)
        - video (MP4, etc.)
        - audio (MP3, etc.)
        - photo (images)
    
    📌 EXAMPLE:
        >>> file_id, unique_id, name, size, type = get_file_id(msg)
        >>> print(name, size, type)
        'document.pdf' 1024000 'document'
    """
    # Document (PDF, ZIP, APK, etc.)
    if message.document:
        return (
            message.document.file_id,
            message.document.file_unique_id,
            message.document.file_name or "document",
            message.document.file_size,
            "document"
        )
    
    # Video (MP4, MKV, etc.)
    elif message.video:
        return (
            message.video.file_id,
            message.video.file_unique_id,
            message.video.file_name or "video.mp4",
            message.video.file_size,
            "video"
        )
    
    # Audio (MP3, WAV, etc.)
    elif message.audio:
        return (
            message.audio.file_id,
            message.audio.file_unique_id,
            message.audio.file_name or "audio.mp3",
            message.audio.file_size,
            "audio"
        )
    
    # Photo (JPEG, PNG, etc.)
    elif message.photo:
        # Photo ka best quality version (last in array)
        photo = message.photo
        return (
            photo.file_id,
            photo.file_unique_id,
            "photo.jpg",
            photo.file_size,
            "photo"
        )
    
    # No file found
    return None, None, None, None, None


def get_file_type_emoji(file_type: str) -> str:
    """
    File type ke hisaab se emoji return karta hai
    
    📌 PARAMS:
        file_type: "document", "video", "audio", "photo"
    
    📌 RETURNS:
        str: Emoji like "📄", "🎬", "🎵", "🖼️"
    """
    emojis = {
        "document": "📄",
        "video": "🎬",
        "audio": "🎵",
        "photo": "🖼️"
    }
    return emojis.get(file_type, "📎")


# ───────────────────────────────────────────────────────────────
# 📏 SIZE FORMATTER
# ───────────────────────────────────────────────────────────────

def format_size(size_bytes: int) -> str:
    """
    Bytes ko human-readable format mein convert karta hai
    
    📌 PARAMS:
        size_bytes: Size in bytes (integer)
    
    📌 RETURNS:
        str: Human readable size like "10.5 MB"
    
    📌 EXAMPLE:
        >>> format_size(1024)
        '1.0 KB'
        >>> format_size(1048576)
        '1.0 MB'
        >>> format_size(1073741824)
        '1.0 GB'
    """
    if size_bytes == 0:
        return "0 B"
    
    # Size units
    units = ["B", "KB", "MB", "GB", "TB"]
    unit_index = 0
    
    size = float(size_bytes)
    
    # Convert to appropriate unit
    while size >= 1024 and unit_index < len(units) - 1:
        size /= 1024
        unit_index += 1
    
    return f"{size:.1f} {units[unit_index]}"


# ───────────────────────────────────────────────────────────────
# ⏰ TIME HELPERS
# ───────────────────────────────────────────────────────────────

def time_ago(timestamp: float) -> str:
    """
    Timestamp ko "X time ago" format mein convert karta hai
    
    📌 PARAMS:
        timestamp: Unix timestamp (float)
    
    📌 RETURNS:
        str: "5 minutes ago", "2 hours ago", "3 days ago"
    
    📌 EXAMPLE:
        >>> time_ago(time.time() - 300)
        '5 minutes ago'
    """
    if not timestamp:
        return "Unknown"
    
    now = time.time()
    diff = now - timestamp
    
    # Time units in seconds
    intervals = [
        (31536000, "year"),
        (2592000, "month"),
        (86400, "day"),
        (3600, "hour"),
        (60, "minute"),
        (1, "second")
    ]
    
    for seconds, unit in intervals:
        value = int(diff / seconds)
        if value >= 1:
            plural = "s" if value > 1 else ""
            return f"{value} {unit}{plural} ago"
    
    return "just now"


def timestamp_to_date(timestamp: float, format_str: str = "%d-%m-%Y %H:%M") -> str:
    """
    Timestamp ko date string mein convert karta hai
    
    📌 PARAMS:
        timestamp: Unix timestamp
        format_str: Date format (default: DD-MM-YYYY HH:MM)
    
    📌 RETURNS:
        str: "25-12-2024 15:30"
    """
    if not timestamp:
        return "Unknown"
    
    try:
        dt = datetime.fromtimestamp(timestamp)
        return dt.strftime(format_str)
    except:
        return "Invalid Date"


def get_delete_timestamp(hours: int) -> float:
    """
    Current time se X hours aage ka timestamp return karta hai
    
    📌 PARAMS:
        hours: Number of hours (integer)
    
    📌 RETURNS:
        float: Unix timestamp for deletion time
    
    📌 USE CASE:
        Auto delete ke liye delete_at field
    """
    if hours <= 0:
        return None
    return time.time() + (hours * 3600)


# ───────────────────────────────────────────────────────────────
# 📝 TEXT HELPERS
# ───────────────────────────────────────────────────────────────

def truncate_text(text: str, max_length: int = 50) -> str:
    """
    Long text ko short karta hai with "..." suffix
    
    📌 PARAMS:
        text: Input text
        max_length: Maximum length (default 50)
    
    📌 RETURNS:
        str: Truncated text with "..."
    """
    if not text:
        return ""
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."


def escape_markdown(text: str) -> str:
    """
    Markdown special characters escape karta hai
    
    📌 PARAMS:
        text: Input text
    
    📌 RETURNS:
        str: Text with escaped characters
    
    📌 USE CASE:
        Telegram markdown messages mein use karo
    """
    if not text:
        return ""
    
    # Characters to escape in Telegram markdown
    special_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
    
    for char in special_chars:
        text = text.replace(char, f"\\{char}")
    
    return text


# ───────────────────────────────────────────────────────────────
# 🔍 VALIDATION HELPERS
# ───────────────────────────────────────────────────────────────

def is_valid_channel_id(channel_id: str) -> bool:
    """
    Check karta hai ki channel ID valid hai ya nahi
    
    📌 PARAMS:
        channel_id: String to check
    
    📌 RETURNS:
        bool: True if valid, False otherwise
    
    📌 VALID FORMAT:
        - "-100123456789" (with -100 prefix)
        - "-100" + 9-12 digits
    """
    try:
        cid = int(channel_id)
        # Channel IDs start with -100
        return str(cid).startswith("-100")
    except:
        return False


def is_valid_user_id(user_id: str) -> bool:
    """
    Check karta hai ki user ID valid hai ya nahi
    
    📌 PARAMS:
        user_id: String to check
    
    📌 RETURNS:
        bool: True if valid
    """
    try:
        uid = int(user_id)
        # User IDs are positive and typically 8-10 digits
        return uid > 0
    except:
        return False


# ═══════════════════════════════════════════════════════════════
# ✅ ALL HELPERS READY!
# ═══════════════════════════════════════════════════════════════
