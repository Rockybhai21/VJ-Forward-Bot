# Don't Remove Credit Tg - @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01

import re
import asyncio 
from .utils import STS
from database import Db, db
from config import temp 
from script import Script
from pyrogram import Client, filters, enums
from pyrogram.errors import FloodWait 
from pyrogram.errors.exceptions.not_acceptable_406 import ChannelPrivate as PrivateChat
from pyrogram.errors.exceptions.bad_request_400 import ChannelInvalid, ChatAdminRequired, UsernameInvalid, UsernameNotModified, ChannelPrivate
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
import json

@Client.on_message(filters.group & filters.forwarded)
async def forward_from_group(bot, message):
    """ Handles forwarded messages from groups """
    try:
        if message.forward_from_chat:  
            forward_chat_id = message.forward_from_chat.id  
            last_msg_id = message.forward_from_message_id  

            # Try forwarding to the detected group
            await bot.forward_messages(forward_chat_id, message.chat.id, last_msg_id)

        elif message.sender_chat:  # If forwarded from an anonymous admin
            await message.reply("This message was sent by an **anonymous admin**. Please send the message link instead.")
    
    except Exception as e:
        print(f"Error forwarding from group: {e}")
        await message.reply("Failed to forward. Please check bot permissions.")

@Client.on_message(filters.group & filters.text)
async def extract_and_forward_links(bot, message):
    """ Detects Telegram links in messages and extracts them """
    match = re.search(r"(https://t\.me/\S+/\d+)", message.text)  # Detect message link
    if match:
        link = match.group(1)  # Extract the link
        try:
            await bot.send_message(message.chat.id, f"Forwarding message: {link}")
        except Exception as e:
            print(f"Error forwarding link: {e}")

@Client.on_message(filters.private & filters.text)
async def forward_from_post_link(bot, message):
    """ Starts forwarding messages from a specified post link """
    post_link = message.text.strip()
    
    # Regular expression to match the Telegram post link
    regex = re.compile(r"(https://)?(t\.me/|telegram\.me/|telegram\.dog/)(c/)?(\d+|[a-zA-Z_0-9]+)/(\d+)$")
    match = regex.match(post_link)
    
    if not match:
        return await message.reply("Invalid link. Please provide a valid Telegram post link.")
    
    chat_id = match.group(4)
    last_msg_id = int(match.group(5))
    
    if chat_id.isnumeric():
        chat_id = int("-100" + chat_id)  # Convert to group ID format if necessary

    # Start forwarding messages from the specified message ID
    try:
        # Fetch the total number of messages to forward (you can set a limit)
        total_messages_to_forward = 10  # Example: forward 10 messages
        for msg_id in range(last_msg_id, last_msg_id + total_messages_to_forward):
            await bot.forward_messages(chat_id, chat_id, msg_id)
            await message.reply(f"Forwarded message ID: {msg_id}")
    except Exception as e:
        await message.reply(f"An error occurred while forwarding: {str(e)}")

@Client.on_message(filters.group & filters.forwarded)
async def forward_to_custom_group(bot, message):
    """ Forwards group messages to a user-defined target group """
    try:
        with open("config.json", "r") as file:
            config = json.load(file)
            forward_chat_id = config.get("forward_group")
    except:
        return await message.reply("No forwarding group set. Use /setgroup <group_id>.")

    if forward_chat_id:
        try:
            await bot.forward_messages(forward_chat_id, message.chat.id, message.message_id)
            await message.reply(f"Forwarded to `{forward_chat_id}`")
        except Exception as e:
            print(f"Error forwarding: {e}")
            await message.reply("Failed to forward. Check bot permissions.")

@Client.on_message(filters.private & filters.command(["forward"]))
async def run(bot, message):
    buttons = []
    btn_data = {}
    user_id = message.from_user.id
    _bot = await db.get_bot(user_id)
    if not _bot:
        _bot = await db.get_userbot(user_id)
        if not _bot:
            return await message.reply("<code>You didn't add any bot. Please add a bot using /settings!</code>")
    channels = await db.get_user_channels(user_id)
    if not channels:
        return await message.reply_text("Please set a channel in /settings before forwarding.")
    if len(channels) > 1:
        for channel in channels:
            buttons.append([KeyboardButton(f"{channel['title']}")])
            btn_data[channel['title']] = channel['chat_id']
        buttons.append([KeyboardButton("cancel")]) 
        _toid = await bot.ask(message.chat.id, Script.TO_MSG.format(_bot['name'], _bot['username']), reply_markup=ReplyKeyboardMarkup(buttons, one_time_keyboard=True, resize_keyboard=True))
        if _toid.text.startswith(('/', 'cancel')):
            return await message.reply_text(Script.CANCEL, reply_markup=ReplyKeyboardRemove())
        to_title = _toid.text
        toid = btn_data.get(to_title)
        if not toid:
            return await message.reply_text("Wrong channel chosen!", reply_markup=ReplyKeyboardRemove())
    else:
        toid = channels[0]['chat_id']
        to_title = channels[0]['title']
    fromid = await bot.ask(message.chat.id, Script.FROM_MSG, reply_markup=ReplyKeyboardRemove())
    if fromid.text and fromid.text.startswith('/'):
        await message.reply(Script.CANCEL)
        return 
    if fromid.text and not fromid.forward_date:
        regex = re.compile("(https://)?(t\.me/|telegram\.me/|telegram\.dog/)(c/)?(\d+|[a-zA-Z_0-9]+)/(\d+)$")
        match = regex.match(fromid.text.replace("?single", ""))
        if not match:
            return await message.reply('Invalid link')
        chat_id = match.group(4)
        last_msg_id = int(match.group(5))
        if chat_id.isnumeric():
            chat_id  = int(("-100" + chat_id))
    elif fromid.forward_from_chat.type in [enums.ChatType.CHANNEL, 'supergroup']:
        last_msg_id = fromid.forward_from_message_id
        chat_id = fromid.forward_from_chat.username or fromid.forward_from_chat.id
        if last_msg_id is None:
            return await message.reply_text("**This may be a forwarded message from a group and sent by an anonymous admin. Instead of this, please send the last message link from the group.**")
    else:
        await message.reply_text("**Invalid!**")
        return 
    try:
        title = (await bot.get_chat(chat_id)).title
    except (PrivateChat, ChannelPrivate, ChannelInvalid):
        title = "private" if fromid.text else fromid.forward_from_chat.title
    except (UsernameInvalid, UsernameNotModified):
        return await message.reply('Invalid Link specified.')
    except Exception as e:
        return await message.reply(f'Errors - {e}')
    skipno = await bot.ask(message.chat.id, Script.SKIP_MSG)
    if skipno.text.startswith('/'):
        await message.reply(Script.CANCEL)
        return
    forward_id = f"{user_id}-{skipno.id}"
    buttons = [[
        InlineKeyboardButton('Yes ✅', callback_data=f"start_public_{forward_id}"),
        InlineKeyboardButton('No ❌', callback_data="close_btn")
    ]]
    reply_markup = InlineKeyboardMarkup(buttons)
    await message.reply_text(
        text=Script.DOUBLE_CHECK.format(botname=_bot['name'], botuname=_bot['username'], from_chat=title, to_chat=to_title, skip=skipno.text),
        disable_web_page_preview=True,
        reply_markup=reply_markup
    )
    STS(forward_id).store(chat_id, toid, int(skipno.text), int(last_msg_id))

@Client.on_callback_query(filters.regex(r"^start_batch_(\d+)$"))
async def confirm_batch_forward(client, query: CallbackQuery):
    user_id = int(query.matches[0].group(1))

    if user_id not in batch_forward_sessions:
        return await query.answer("Session expired! Please start again.", show_alert=True)

    session = batch_forward_sessions.pop(user_id)
    start_id = session["start_id"]
    last_id = session["last_id"]
    total_msgs = session["total_msgs"]

    # Notify user and start processing
    pin_msg = await query.message.reply(f"Batch forwarding started ⚡\nProcessing: 0/{total_msgs}")
    await pin_msg.pin()

    users_loop[user_id] = True
    try:
        for msg_id in range(start_id, last_id + 1):
            if user_id in users_loop and users_loop[user_id]:
                await client.forward_messages(query.message.chat.id, query.message.chat.id, msg_id)
                await pin_msg.edit_text(f"Batch forwarding in progress: {msg_id - start_id + 1}/{total_msgs}")

        await pin_msg.edit_text("✅ Batch forwarding completed successfully!")
    except Exception as e:
        await query.message.reply(f"Error: {str(e)}")
    finally:
        users_loop.pop(user_id, None)

@Client.on_callback_query(filters.regex(r"^cancel_batch$"))
async def cancel_batch_forward(client, query: CallbackQuery):
    user_id = query.message.chat.id
    batch_forward_sessions.pop(user_id, None)  # Remove session if exists
    await query.message.edit_text("Batch forwarding canceled.")

# Don't Remove Credit Tg - @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01
