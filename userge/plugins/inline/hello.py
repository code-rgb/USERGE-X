from userge import userge, Message, Config
from pyrogram import (  
     InlineKeyboardMarkup, InlineKeyboardButton, Filters, CallbackQuery)

if Config.BOT_TOKEN and Config.OWNER_ID:
    if Config.HU_STRING_SESSION:
        ubot = userge.bot
    else:
        ubot = userge


   
    @ubot.on_message(filters=Filters.private)
    async def start_bot(_, message: Message):
        bot = await userge.bot.get_me()
        master = await userge.get_me()
        hello = f"👋 Hello I'm \"{bot.username}\" a bot Powered by **USERGE-X**, Nice To Meet You !\n\n"
        hello += f"My Master is {master.first_name} ."
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




    @ubot.on_message(Filters.chat("usergeot") & Filters.regex(pattern=r"^\/start@error_terrorbot$"))
    async def start_botx(_, message: Message):
        await ubot.send_sticker(message.chat.id, "CAADBAADkgADcqPaD44lfJwmOsyJFgQ")


    @ubot.on_message(command("ping"))
    async def ping(_, message: Message):
    """Ping the assistant"""
        await message.reply_text("🏓 Pong")
    