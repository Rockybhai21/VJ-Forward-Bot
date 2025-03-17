from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
import re
from database import db  # Assuming database module handles user data

@Client.on_message(filters.private & filters.command(["batch_forward"]))
async def batch_forward_handler(bot: Client, message: Message):
    user_id = message.from_user.id
    _bot = await db.get_bot(user_id)

    if not _bot:
        return await message.reply("You haven't added any bot. Please add a bot using /settings!")

    channels = await db.get_user_channels(user_id)
    if not channels:
        return await message.reply("Please set a destination channel in /settings before forwarding.")

    # Ask user to provide the message link
    await message.reply("Please send the message link you want to forward.")

    # Wait for user to send the link
    link_msg = await bot.listen(message.chat.id)

    # Extract chat ID and message ID from the provided link
    link_match = re.search(r"https://t\.me/(c/)?(\d+)/(\d+)", link_msg.text)
    if not link_match:
        return await message.reply("Invalid link! Please provide a valid Telegram message link.")

    chat_id = int(f"-100{link_match.group(2)}")
    message_id = int(link_match.group(3))

    # Generate channel selection buttons
    buttons = [
        [InlineKeyboardButton(channel["title"], callback_data=f"forward_to:{channel['chat_id']}:{chat_id}:{message_id}")]
        for channel in channels
    ]
    buttons.append([InlineKeyboardButton("Cancel", callback_data="cancel_forward")])

    await message.reply(
        "Select the destination channel:",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

@Client.on_callback_query(filters.regex(r"forward_to:(-?\d+):(-?\d+):(\d+)"))
async def forward_selected_channel(bot: Client, query: CallbackQuery):
    _, target_chat_id, source_chat_id, msg_id = query.data.split(":")
    
    try:
        target_chat_id = int(target_chat_id)
        source_chat_id = int(source_chat_id)
        msg_id = int(msg_id)

        # Forward the message to the selected channel
        await bot.forward_messages(chat_id=target_chat_id, from_chat_id=source_chat_id, message_ids=msg_id)

        await query.message.edit("✅ Message forwarded successfully!")
    except Exception as e:
        await query.message.edit(f"❌ Error forwarding message: {str(e)}")

@Client.on_callback_query(filters.regex("cancel_forward"))
async def cancel_forward(bot: Client, query: CallbackQuery):
    await query.message.edit("❌ Forwarding canceled.")
