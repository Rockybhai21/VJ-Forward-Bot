
import asyncio, logging
from config import Config
from pyrogram import Client as VJ, idle
from typing import Union, Optional, AsyncGenerator
from logging.handlers import RotatingFileHandler
from plugins.regix import restart_forwards

# Don't Remove Credit Tg - @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01

if __name__ == "__main__":
    VJBot = VJ(
        "VJ-Forward-Bot",
        bot_token=Config.BOT_TOKEN,
        api_id=Config.API_ID,
        api_hash=Config.API_HASH,
        sleep_threshold=120,
        plugins=dict(root="plugins")


users_loop = {}
batch_forward_sessions = {}

@VJBot.on_message(filters.command("batch_forward") & filters.private)
async def batch_forward(client, message):
    user_id = message.chat.id
    args = message.text.split()

    if len(args) != 3:
        return await message.reply("Usage: `/batch_forward <first_msg_link> <last_msg_link>`")

    try:
        start_id = int(args[1].split("/")[-1])
        last_id = int(args[2].split("/")[-1])

        if last_id < start_id:
            return await message.reply("Invalid range! The last message must be after the first message.")

        skip_msg = await client.ask(
            user_id,
            "<b>❪ SET MESSAGE SKIPING NUMBER ❫</b>\n\n"
            "<b>Skip the message as much as you enter the number and the rest of the message will be forwarded</b>\n"
            "Default Skip Number = <code>0</code>\n"
            "<code>eg: You enter 0 = 0 message skipped\n You enter 5 = 5 messages skipped</code>\n\n"
            "/cancel - cancel this process"
        )

        try:
            skip_count = int(skip_msg.text.strip())
            if skip_count < 0:
                return await message.reply("Invalid input! Please enter a number 0 or greater.")
        except ValueError:
            return await message.reply("Invalid input! Please enter a valid number.")

        total_msgs = (last_id - start_id + 1) - skip_count
        if total_msgs <= 0:
            return await message.reply("Skipping too many messages! Nothing left to forward.")

        batch_forward_sessions[user_id] = {
            "start_id": start_id + skip_count,
            "last_id": last_id,
            "total_msgs": total_msgs
        }

        buttons = [
            [InlineKeyboardButton("✅ Yes", callback_data=f"start_batch_{user_id}")],
            [InlineKeyboardButton("❌ No", callback_data="cancel_batch")]
        ]
        markup = InlineKeyboardMarkup(buttons)

        await message.reply(
            f"You're about to forward **{total_msgs} messages**.\n\nConfirm to proceed:",
            reply_markup=markup
        )

    except ValueError:
        await message.reply("Invalid links! Make sure you are providing valid Telegram message links.")

@VJBot.on_callback_query(filters.regex(r"^start_batch_(\d+)$"))
async def confirm_batch_forward(client, query: CallbackQuery):
    user_id = int(query.matches[0].group(1))

    if user_id not in batch_forward_sessions:
        return await query.answer("Session expired! Please start again.", show_alert=True)

    session = batch_forward_sessions.pop(user_id)
    start_id = session["start_id"]
    last_id = session["last_id"]
    total_msgs = session["total_msgs"]

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

@VJBot.on_callback_query(filters.regex(r"^cancel_batch$"))
async def cancel_batch_forward(client, query: CallbackQuery):
    user_id = query.message.chat.id
    batch_forward_sessions.pop(user_id, None)
    await query.message.edit_text("Batch forwarding canceled.")

@VJBot.on_message(filters.command("cancel"))
async def stop_batch(_, message):
    user_id = message.chat.id

    if user_id in users_loop and users_loop[user_id]:
        users_loop[user_id] = False
        await message.reply("Batch forwarding has been stopped successfully.")
    else:
        await message.reply("No active batch process to cancel.")

async def iter_messages(
        self,
        chat_id: Union[int, str],
        limit: int,
        offset: int = 0,
    ) -> Optional[AsyncGenerator["types.Message", None]]:
        """Iterate through a chat sequentially.
        This convenience method does the same as repeatedly calling :meth:`~pyrogram.Client.get_messages` in a loop, thus saving
        you from the hassle of setting up boilerplate code. It is useful for getting the whole chat messages with a
        single call.
        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.
                For your personal cloud (Saved Messages) you can simply use "me" or "self".
                For a contact that exists in your Telegram address book you can use his phone number (str).
                
            limit (``int``):
                Identifier of the last message to be returned.
                
            offset (``int``, *optional*):
                Identifier of the first message to be returned.
                Defaults to 0.
        Returns:
            ``Generator``: A generator yielding :obj:`~pyrogram.types.Message` objects.
        Example:
            .. code-block:: python
                for message in app.iter_messages("pyrogram", 1, 15000):
                    print(message.text)
        """
        current = offset
        while True:
            new_diff = min(200, limit - current)
            if new_diff <= 0:
                return
            messages = await self.get_messages(chat_id, list(range(current, current+new_diff+1)))
            for message in messages:
                yield message
                current += 1
                
async def main():
        await VJBot.start()
        bot_info  = await VJBot.get_me()
        await restart_forwards(VJBot)
        print("Bot Started.")
        await idle()

    asyncio.get_event_loop().run_until_complete(main())
