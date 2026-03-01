# ═══════════════════════════════════════════════════════════════
# 📥 plugins/join_req.py - JOIN REQUEST HANDLER
# ═══════════════════════════════════════════════════════════════
#
# 📌 KYUN USE HOTA HAI?
#    - Private channels ke join requests handle karta hai
#    - Jab user "Request to Join" karta hai
#    - Request ko database mein save karta hai
#
# 📌 FLOW:
#    1. User private channel mein join request bhejta hai
#    2. Ye handler chalta hai
#    3. Request DB mein save hoti hai
#    4. Force sub check karte time request check hoti hai
# ═══════════════════════════════════════════════════════════════

from pyrogram import Client
from pyrogram.types import ChatJoinRequest
from database.db import db


# ═══════════════════════════════════════════════════════════════
# 📥 JOIN REQUEST HANDLER
# ═══════════════════════════════════════════════════════════════

@Client.on_chat_join_request()
async def join_request_handler(client: Client, request: ChatJoinRequest):
    """
    Jab user join request bhejta hai
    
    📌 PARAMS:
        client: Pyrogram client
        request: ChatJoinRequest object
    
    📌 CONTAINS:
        - request.from_user.id - User ID
        - request.chat.id - Channel ID
    
    📌 LOGIC:
        1. User ID aur Channel ID lo
        2. Database mein save karo
        3. Ab force sub check karte time ye request accept hogi
    """
    user = request.from_user
    chat = request.chat
    
    user_id = user.id
    channel_id = chat.id
    
    print(f"📥 Join Request: User {user_id} ({user.first_name}) -> Channel {channel_id} ({chat.title})")
    
    # Save to database
    await db.add_join_request(user_id, channel_id)
    
    # Optional: Send welcome message to user
    # (Uncomment if you want to send message)
    
    try:
        await client.send_message(
            user_id,
            f"👋 **Hello {user.first_name}!**\n\n"
            f"Your join request for **{chat.title}** has been received.\n\n"
            f"Please wait for admin approval. Once approved, you can download files."
        )
    except:
        pass  # User may have blocked bot
    


# ═══════════════════════════════════════════════════════════════
# ✅ JOIN REQUEST PLUGIN READY!
#
# 📌 NOTE:
#    - Ye handler tab chalta hai jab bot admin ho channel mein
#    - Bot ko channel mein admin banana zaroori hai
#    - Force sub check karte time pending request bhi accept hoti hai
# ═══════════════════════════════════════════════════════════════
