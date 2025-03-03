import asyncio, logging, re
from config import Config
from pyrogram import Client as VJ, filters, idle
from pyrogram.errors import FloodWait
from typing import Union, Optional, AsyncGenerator
from logging.handlers import RotatingFileHandler
from plugins.regix import restart_forwards

# Don't Remove Credit Tg - @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01

VJBot = VJ(
    "VJ-Forward-Bot",
    bot_token=Config.BOT_TOKEN,
    api_id=Config.API_ID,
    api_hash=Config.API_HASH,
    sleep_threshold=120,
    plugins=dict(root="plugins")
)

def extract_chat_and_message_id(link):
    pattern = r"t\.me/(?P<chat>[^/]+)/(?P<msg_id>\d+)"
    match = re.search(pattern, link)
    if match:
        return match.group("chat"), int(match.group("msg_id"))
    return None, None

@VJBot.on_message(filters.command("batch_forward"))
async def batch_forward(client, message):
    args = message.text.split()
    if len(args) != 3:
        await message.reply("Usage: /batch_forward <first_msg_link> <last_msg_link>")
        return
    
    first_link, last_link = args[1], args[2]
    chat, first_msg_id = extract_chat_and_message_id(first_link)
    _, last_msg_id = extract_chat_and_message_id(last_link)
    
    if not chat or not first_msg_id or not last_msg_id:
        await message.reply("Invalid message links. Make sure both links are from the same chat.")
        return
    
    await message.reply(f"Starting batch forwarding from {first_msg_id} to {last_msg_id}...")
    
    for msg_id in range(first_msg_id, last_msg_id + 1):
        try:
            await client.forward_messages(message.chat.id, chat, msg_id)
            await asyncio.sleep(2)  # Prevent flood limits
        except FloodWait as e:
            await asyncio.sleep(e.value)
        except Exception as e:
            await message.reply(f"Skipping message {msg_id}: {e}")
    
    await message.reply("Batch forwarding completed! ✅")

async def main():
    await VJBot.start()
    bot_info  = await VJBot.get_me()
    await restart_forwards(VJBot)
    print("Bot Started.")
    await idle()

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
