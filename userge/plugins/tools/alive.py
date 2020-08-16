from pyrogram import Filters, CallbackQuery
from userge import userge, Message, Config, versions, get_version

@userge.on_cmd("alive", about={
    'header': "Just For Fun"}, allow_channels=False)
async def alive_inline(message: Message):
    bot = await userge.bot.get_me()
    x = await userge.get_inline_bot_results(bot.username, "alive")
    await userge.send_inline_bot_result(chat_id=message.chat.id,
                                        query_id=x.query_id,
                                        result_id=x.results[1].id)
    await message.delete()

if Config.BOT_TOKEN and Config.OWNER_ID:
    if Config.HU_STRING_SESSION:
        ubot = userge.bot
    else:
        ubot = userge

@ubot.on_callback_query(filters=Filters.regex(pattern=r"^info_btn$"))
async def alive_callback(_, callback_query: CallbackQuery):
    alive_msg = f"""
    • 🕔 𝗨𝗽𝘁𝗶𝗺𝗲 : {userge.uptime}
    • 🐍 𝗣𝘆𝘁𝗵𝗼𝗻 : v {versions.__python_version__}
    • 🔥 𝗣𝘆𝗿𝗼𝗴𝗿𝗮𝗺 : v {versions.__pyro_version__}
    • 🧬 𝗨𝘀𝗲𝗿𝗴𝗲 : v {get_version()}

"""
    await callback_query.answer(alive_msg, show_alert=True)
