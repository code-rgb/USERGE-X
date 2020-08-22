from userge import userge, Message, Config
from pyrogram import (  
     InlineKeyboardMarkup, InlineKeyboardButton, Filters, CallbackQuery)

if Config.BOT_TOKEN and Config.OWNER_ID:
    if Config.HU_STRING_SESSION:
        ubot = userge.bot
    else:
        ubot = userge

    bot = await userge.bot.get_me()
    master = await userge.get_me()
    hello = f"👋 Hello I'm \"{bot.username}\" a bot Powered by **USERGE-X**, Nice To Meet You !\n\n"
    hello += f"My Master is {master.first_name} ."
    @ubot.on_message(filters.private)
    async def start_bot(_, message: Message):
        await message.reply(
                hello,
                disable_web_page_preview=True,
                parse_mode="markdown",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton(
                        "Contact Owner",
                        url=f"tg://user?id={master.id}"
                    ),
                    InlineKeyboardButton(
                        "USERGE-X",
                        switch_inline_query=""
                    )
                ]])
            )