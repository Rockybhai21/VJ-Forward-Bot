# Don't Remove Credit Tg - @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01

import os
import sys
import asyncio 
from database import Db, db
from config import Config, temp
from script import Script
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, InputMediaDocument
import psutil
import time as time
from os import environ, execle, system
from batch_forward import batch_forward  # Adjust path if needed
from pyrogram.types import CallbackQuery

START_TIME = time.time()

# Dictionary to store user selections temporarily
user_data = {}

@Client.on_message(filters.command("batch_forward"))
async def batch_forward(client, message):
    user_id = message.from_user.id
    user_data[user_id] = {"batch_link": None, "source_channels": [], "dest_channel": None}
    
    if len(message.command) < 2:
        await message.reply_text("Please provide a batch link to start forwarding.")
        return
    
    batch_link = message.command[1]
    user_data[user_id]["batch_link"] = batch_link
    
    # Ask the user to select the destination channel
    buttons = [
        [InlineKeyboardButton("Channel 1", callback_data=f"dest_channel_@Channel1")],
        [InlineKeyboardButton("Channel 2", callback_data=f"dest_channel_@Channel2")],
        [InlineKeyboardButton("Cancel ❌", callback_data="cancel_batch")]
    ]
    await message.reply_text("Select the **destination channel**:", reply_markup=InlineKeyboardMarkup(buttons))

@Client.on_callback_query(filters.regex(r"^dest_channel_"))
async def set_dest_channel(client, query: CallbackQuery):
    user_id = query.from_user.id
    dest_channel = query.data.split("_")[1]
    
    user_data[user_id]["dest_channel"] = dest_channel
    
    # Ask the user to select source channels
    buttons = [
        [InlineKeyboardButton("Source 1", callback_data=f"source_channel_@Source1")],
        [InlineKeyboardButton("Source 2", callback_data=f"source_channel_@Source2")],
        [InlineKeyboardButton("Confirm ✅", callback_data="confirm_sources")],
        [InlineKeyboardButton("Cancel ❌", callback_data="cancel_batch")]
    ]
    await query.message.edit_text(f"Selected Destination: **{dest_channel}**\nNow, select **source channels**:", reply_markup=InlineKeyboardMarkup(buttons))

@Client.on_callback_query(filters.regex(r"^source_channel_"))
async def add_source_channel(client, query: CallbackQuery):
    user_id = query.from_user.id
    source_channel = query.data.split("_")[1]
    
    if source_channel not in user_data[user_id]["source_channels"]:
        user_data[user_id]["source_channels"].append(source_channel)
    
    await query.answer(f"Added {source_channel} ✅")

@Client.on_callback_query(filters.regex(r"^confirm_sources"))
async def confirm_forwarding(client, query: CallbackQuery):
    user_id = query.from_user.id
    batch_link = user_data[user_id]["batch_link"]
    source_channels = user_data[user_id]["source_channels"]
    dest_channel = user_data[user_id]["dest_channel"]

    if not source_channels:
        await query.answer("Please select at least one source channel!", show_alert=True)
        return
    
    buttons = [[InlineKeyboardButton("Start Forwarding 🚀", callback_data="start_forwarding")],
               [InlineKeyboardButton("Cancel ❌", callback_data="cancel_batch")]]
    
    await query.message.edit_text(f"✅ **Batch Forwarding Setup Complete!**\n\n"
                                  f"📌 **Batch Link:** {batch_link}\n"
                                  f"📥 **Source Channels:** {', '.join(source_channels)}\n"
                                  f"📤 **Destination Channel:** {dest_channel}\n\n"
                                  "Click **Start Forwarding** to begin!", reply_markup=InlineKeyboardMarkup(buttons))

@Client.on_callback_query(filters.regex(r"^start_forwarding"))
async def start_forwarding(client, query: CallbackQuery):
    user_id = query.from_user.id
    batch_link = user_data[user_id]["batch_link"]
    source_channels = user_data[user_id]["source_channels"]
    dest_channel = user_data[user_id]["dest_channel"]

    await query.message.edit_text("🚀 **Starting Forwarding...** Please wait.")

    chat_id = extract_chat_id(batch_link)
    if not chat_id:
        await query.message.edit_text("❌ Invalid batch link.")
        return
    
    try:
        # Fetch messages from the batch link and forward
        async for msg in client.get_chat_history(chat_id, limit=10):  # Adjust limit as needed
            await msg.forward(dest_channel)
        await query.message.edit_text("✅ Forwarding Completed!")
    except Exception as e:
        await query.message.edit_text(f"❌ Error: {str(e)}")

@Client.on_callback_query(filters.regex(r"^cancel_batch"))
async def cancel_batch(client, query: CallbackQuery):
    await query.message.edit_text("❌ **Batch Forwarding Cancelled.**")
    user_id = query.from_user.id
    user_data.pop(user_id, None)

def extract_chat_id(link):
    """Extract chat ID from the provided Telegram link."""
    match = re.search(r"(https?://t\.me/|@)([\w\d_]+)", link)
    if match:
        return match.group(2)  # Return username or ID
    return None

# Don't Remove Credit Tg - @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01

main_buttons = [[
    InlineKeyboardButton('❣️ ᴅᴇᴠᴇʟᴏᴘᴇʀ ❣️', url='https://t.me/Real_Pirates')
],[
    InlineKeyboardButton('🔍 sᴜᴘᴘᴏʀᴛ ɢʀᴏᴜᴘ', url='https://t.me/Movie_Pirates_x'),
    InlineKeyboardButton('🤖 ᴜᴘᴅᴀᴛᴇ ᴄʜᴀɴɴᴇʟ', url='https://t.me/Real_PirateX')
],[
    InlineKeyboardButton('💝 Movie Channel', url='https://t.me/+4N56hD8S2tgwYmRl')
],[
    InlineKeyboardButton('👨‍💻 ʜᴇʟᴘ', callback_data='help'),
    InlineKeyboardButton('💁 ᴀʙᴏᴜᴛ', callback_data='about')
],[
    InlineKeyboardButton('⚙ sᴇᴛᴛɪɴɢs', callback_data='settings#main')
]]

# Don't Remove Credit Tg - @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01

@Client.on_message(filters.private & filters.command(['start']))
async def start(client, message):
    user = message.from_user
    if not await db.is_user_exist(user.id):
        await db.add_user(user.id, user.first_name)
    reply_markup = InlineKeyboardMarkup(main_buttons)
    await client.send_message(
        chat_id=message.chat.id,
        reply_markup=reply_markup,
        text=Script.START_TXT.format(message.from_user.first_name))

# Don't Remove Credit Tg - @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01

@Client.on_message(filters.private & filters.command(['restart']) & filters.user(Config.BOT_OWNER))
async def restart(client, message):
    msg = await message.reply_text(text="<i>Trying to restarting.....</i>")
    await asyncio.sleep(5)
    await msg.edit("<i>Server restarted successfully ✅</i>")
    system("git pull -f && pip3 install --no-cache-dir -r requirements.txt")
    execle(sys.executable, sys.executable, "main.py", environ)


# Don't Remove Credit Tg - @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01

@Client.on_callback_query(filters.regex(r'^help'))
async def helpcb(bot, query):
    buttons = [[
        InlineKeyboardButton('🤔 ʜᴏᴡ ᴛᴏ ᴜsᴇ ᴍᴇ ❓', callback_data='how_to_use')
    ],[
        InlineKeyboardButton('Aʙᴏᴜᴛ ✨️', callback_data='about'),
        InlineKeyboardButton('⚙ Sᴇᴛᴛɪɴɢs', callback_data='settings#main')
    ],[
        InlineKeyboardButton('• back', callback_data='back')
    ]]
    reply_markup = InlineKeyboardMarkup(buttons)
    await query.message.edit_text(text=Script.HELP_TXT, reply_markup=reply_markup)

# Don't Remove Credit Tg - @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01

@Client.on_callback_query(filters.regex(r'^how_to_use'))
async def how_to_use(bot, query):
    buttons = [[InlineKeyboardButton('• back', callback_data='help')]]
    reply_markup = InlineKeyboardMarkup(buttons)
    await query.message.edit_text(
        text=Script.HOW_USE_TXT,
        reply_markup=reply_markup,
        disable_web_page_preview=True
    )

# Don't Remove Credit Tg - @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01

@Client.on_callback_query(filters.regex(r'^back'))
async def back(bot, query):
    reply_markup = InlineKeyboardMarkup(main_buttons)
    await query.message.edit_text(
       reply_markup=reply_markup,
       text=Script.START_TXT.format(query.from_user.first_name))

# Don't Remove Credit Tg - @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01

@Client.on_callback_query(filters.regex(r'^about'))
async def about(bot, query):
    buttons = [[
         InlineKeyboardButton('• back', callback_data='help'),
         InlineKeyboardButton('Stats ✨️', callback_data='status')
    ]]
    reply_markup = InlineKeyboardMarkup(buttons)
    await query.message.edit_text(
        text=Script.ABOUT_TXT,
        reply_markup=reply_markup,
        disable_web_page_preview=True
    )

# Don't Remove Credit Tg - @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01

@Client.on_callback_query(filters.regex(r'^status'))
async def status(bot, query):
    users_count, bots_count = await db.total_users_bots_count()
    forwardings = await db.forwad_count()
    upt = await get_bot_uptime(START_TIME)
    buttons = [[
        InlineKeyboardButton('• back', callback_data='help'),
        InlineKeyboardButton('System Stats ✨️', callback_data='systm_sts'),
    ]]
    reply_markup = InlineKeyboardMarkup(buttons)
    await query.message.edit_text(
        text=Script.STATUS_TXT.format(upt, users_count, bots_count, forwardings),
        reply_markup=reply_markup,
        disable_web_page_preview=True,
    )

# Don't Remove Credit Tg - @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01

@Client.on_callback_query(filters.regex(r'^systm_sts'))
async def sys_status(bot, query):
    buttons = [[InlineKeyboardButton('• back', callback_data='help')]]
    ram = psutil.virtual_memory().percent
    cpu = psutil.cpu_percent()
    disk_usage = psutil.disk_usage('/')
    total_space = disk_usage.total / (1024**3)  # Convert to GB
    used_space = disk_usage.used / (1024**3)    # Convert to GB
    free_space = disk_usage.free / (1024**3)
    text = f"""
╔════❰ sᴇʀᴠᴇʀ sᴛᴀᴛs  ❱═❍⊱❁۪۪
║╭━━━━━━━━━━━━━━━➣
║┣⪼ <b>ᴛᴏᴛᴀʟ ᴅɪsᴋ sᴘᴀᴄᴇ</b>: <code>{total_space:.2f} GB</code>
║┣⪼ <b>ᴜsᴇᴅ</b>: <code>{used_space:.2f} GB</code>
║┣⪼ <b>ꜰʀᴇᴇ</b>: <code>{free_space:.2f} GB</code>
║┣⪼ <b>ᴄᴘᴜ</b>: <code>{cpu}%</code>
║┣⪼ <b>ʀᴀᴍ</b>: <code>{ram}%</code>
║╰━━━━━━━━━━━━━━━➣
╚══════════════════❍⊱❁۪۪
"""
    reply_markup = InlineKeyboardMarkup(buttons)
    await query.message.edit_text(
        text,
        reply_markup=reply_markup,
        disable_web_page_preview=True,
    )

# Don't Remove Credit Tg - @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01

async def get_bot_uptime(start_time):
    # Calculate the uptime in seconds
    uptime_seconds = int(time.time() - start_time)
    uptime_minutes = uptime_seconds // 60
    uptime_hours = uptime_minutes // 60
    uptime_days = uptime_hours // 24
    uptime_weeks = uptime_days // 7
    uptime_string = ""
    if uptime_hours != 0:
        uptime_string += f" {uptime_hours % 24}H"
    if uptime_minutes != 0:
        uptime_string += f" {uptime_minutes % 60}M"
    uptime_string += f" {uptime_seconds % 60} Sec"
    return uptime_string   

# Don't Remove Credit Tg - @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01
