from pyrogram import Client, filters
from pyrogram.errors import PeerIdInvalid, MessageIdInvalid
import time

# Configurable batch size
BATCH_SIZE = 5  

@Client.on_message(filters.command("batch_forward"))
async def batch_forward(bot, message):
    chat_id = message.chat.id

    # Ask user for the message link
    await message.reply("🔗 Send me the link of the message you want to batch forward.")

    # Wait for the user’s response
    user_response = await bot.listen(chat_id)
    if not user_response.text:
        return await message.reply("⚠️ Please send a valid Telegram message link.")

    try:
        # Extract chat ID and message ID from the link
        link_parts = user_response.text.split("/")
        chat_username = link_parts[-3]
        message_id = int(link_parts[-1])

        # Get the source chat and message
        source_chat = await bot.get_chat(chat_username)
        messages = await bot.get_messages(source_chat.id, message_ids=range(message_id, message_id + BATCH_SIZE))

        if not messages:
            return await message.reply("⚠️ No messages found for batch forwarding.")

        await message.reply(f"✅ Found {len(messages)} messages! Starting batch forwarding...")

        # Forward messages in batches
        for i in range(0, len(messages), BATCH_SIZE):
            batch = messages[i:i + BATCH_SIZE]
            for msg in batch:
                await msg.forward(chat_id)
                time.sleep(1)  # Optional delay

        await message.reply("🎉 Batch forwarding complete!")

    except (PeerIdInvalid, MessageIdInvalid, ValueError, IndexError):
        await message.reply("⚠️ Invalid message link. Please try again.")
