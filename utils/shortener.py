# ═══════════════════════════════════════════════════════════════
# 💸 utils/shortener.py - URL SHORTENER API
# ═══════════════════════════════════════════════════════════════
#
# 📌 KYUN USE HOTA HAI?
#    - Long links ko short links mein convert karta hai
#    - Revenue generation (short links pay karte hain)
#    - Round-robin rotation for multiple shorteners
#
# 📌 SUPPORTED SHORTENERS:
#    - LinkShortify
#    - GPLinks
#    - Any shortener with API support
# ═══════════════════════════════════════════════════════════════

import aiohttp
import urllib.parse
from config import Config
from database.db import db


# ───────────────────────────────────────────────────────────────
# 🔗 SHORTENER API CALL
# ───────────────────────────────────────────────────────────────

async def shorten_url(domain: str, api_key: str, original_url: str) -> str:
    """
    Single shortener API call karta hai
    
    📌 PARAMS:
        domain: Shortener website domain (e.g., "linkshortify.com")
        api_key: API key from shortener account
        original_url: URL to shorten
    
    📌 RETURNS:
        str: Short URL if success
        None: If failed
    
    📌 API FORMAT:
        https://{domain}/api?api={api_key}&url={url}&format=text
    
    📌 EXAMPLE:
        >>> await shorten_url("linkshortify.com", "abc123", "https://google.com")
        'https://linkshortify.com/xyz123'
    """
    try:
        # URL encode karo
        encoded_url = urllib.parse.quote(original_url, safe='')
        
        # API URL banao
        api_url = f"https://{domain}/api?api={api_key}&url={encoded_url}&format=text"
        
        # Timeout set karo (5 seconds max)
        timeout = aiohttp.ClientTimeout(total=5)
        
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(api_url, ssl=False) as response:
                if response.status == 200:
                    data = await response.text()
                    
                    # Check if response is a valid URL
                    data = data.strip()
                    if data.startswith("http"):
                        print(f"✅ Shortened: {domain} -> {data[:30]}...")
                        return data
                    else:
                        print(f"⚠️ Invalid response from {domain}: {data[:50]}")
                else:
                    print(f"❌ HTTP {response.status} from {domain}")
                    
    except aiohttp.ClientError as e:
        print(f"❌ Network error {domain}: {e}")
    except Exception as e:
        print(f"❌ Error {domain}: {e}")
    
    return None


# ───────────────────────────────────────────────────────────────
# 🎯 MAIN SHORTENER FUNCTION
# ───────────────────────────────────────────────────────────────

async def get_short_link(original_url: str, user_id: int = None) -> str:
    """
    Main function - Short link generate karta hai with rotation
    
    📌 PARAMS:
        original_url: URL to shorten
        user_id: User ID for rotation tracking (optional)
    
    📌 RETURNS:
        str: Short URL or original URL if all fail
    
    📌 ROTATION LOGIC:
        - Agar user_id diya hai, database se rotation track hoga
        - Har user ko different shortener milega (Round-Robin)
        - Agar ek shortener fail ho, next try karega
    
    📌 EXAMPLE:
        >>> await get_short_link("https://t.me/bot?start=abc123", user_id=12345)
        'https://linkshortify.com/xyz'
    """
    
    # Shorteners check karo
    if not Config.SHORTENERS:
        print("⚠️ No shorteners configured, returning original URL")
        return original_url
    
    total_shorteners = len(Config.SHORTENERS)
    
    # ───────────────────────────────────────────────────────────
    # CASE 1: User ID hai (Rotation enabled)
    # ───────────────────────────────────────────────────────────
    if user_id:
        try:
            # Database se next shortener index patao
            index = await db.get_next_shortener_index(user_id, total_shorteners)
            shortener = Config.SHORTENERS[index]
            
            print(f"🎯 User {user_id} -> Shortener {index}: {shortener['domain']}")
            
            # Try shorten
            short_url = await shorten_url(
                shortener['domain'],
                shortener['api_key'],
                original_url
            )
            
            if short_url:
                return short_url
            
            # Primary fail, try backup
            print(f"⚠️ Primary failed, trying backup...")
            
        except Exception as e:
            print(f"❌ Rotation error: {e}")
    
    # ───────────────────────────────────────────────────────────
    # CASE 2: No user_id OR rotation failed
    # ───────────────────────────────────────────────────────────
    # Try all shorteners one by one
    for i, shortener in enumerate(Config.SHORTENERS):
        print(f"🔄 Trying shortener {i+1}/{total_shorteners}: {shortener['domain']}")
        
        short_url = await shorten_url(
            shortener['domain'],
            shortener['api_key'],
            original_url
        )
        
        if short_url:
            return short_url
    
    # ───────────────────────────────────────────────────────────
    # ALL FAILED - Return original URL
    # ───────────────────────────────────────────────────────────
    print(f"❌ All shorteners failed, returning original URL")
    return original_url


# ───────────────────────────────────────────────────────────────
# 🧪 TEST FUNCTION
# ───────────────────────────────────────────────────────────────

async def test_shorteners():
    """
    Saare shorteners test karta hai
    
    📌 USE CASE:
        Bot start hone par test karo
        Ya admin command se test karo
    
    📌 RETURNS:
        dict: {"domain": "status"} for each shortener
    """
    results = {}
    test_url = "https://google.com"
    
    for shortener in Config.SHORTENERS:
        domain = shortener['domain']
        print(f"🧪 Testing {domain}...")
        
        result = await shorten_url(domain, shortener['api_key'], test_url)
        results[domain] = "✅ Working" if result else "❌ Failed"
    
    return results


# ═══════════════════════════════════════════════════════════════
# ✅ SHORTENER MODULE READY!
# 
# 📌 USAGE:
#    from utils.shortener import get_short_link
#    short_url = await get_short_link(long_url, user_id=123)
# ═══════════════════════════════════════════════════════════════
