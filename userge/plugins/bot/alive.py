"""Fun plugin"""

from pyrogram import filters
from pyrogram.types import CallbackQuery
from userge import userge, Message, Config
from userge.core.ext import RawClient
import asyncio


@userge.on_cmd("alive", about={
    'header': "Just For Fun"}, allow_channels=False)
async def alive_inline(message: Message):
    bot = await userge.bot.get_me()
    x = await userge.get_inline_bot_results(bot.username, "alive")
    
    y = await userge.send_inline_bot_result(chat_id=message.chat.id,
                                        query_id=x.query_id,
                                        result_id=x.results[1].id)
    await message.delete()
    await asyncio.sleep(35)
    await userge.delete_messages(message.chat.id, y.updates[0].id)


if Config.BOT_TOKEN and Config.OWNER_ID:
    if Config.HU_STRING_SESSION:
        ubot = userge.bot
    else:
        ubot = userge


    @ubot.on_callback_query(filters.regex(pattern=r"^settings_btn$"))
    async def alive_cb(_, callback_query: CallbackQuery):
        if Config.HEROKU_APP:
            dynos_saver = _parse_arg(Config.RUN_DYNO_SAVER)
        else:
            dynos_saver = "Not Supported"
            
        alive_s=f"• 👥 𝗦𝘂𝗱𝗼 : {_parse_arg(Config.SUDO_ENABLED)}\n"
        alive_s+=f"• 🚨 𝗔𝗻𝘁𝗶𝘀𝗽𝗮𝗺 : {_parse_arg(Config.ANTISPAM_SENTRY)}\n"
        alive_s+=f"• ↕️ 𝗗𝘂𝗮𝗹 𝗠𝗼𝗱𝗲 : {_parse_arg(RawClient.DUAL_MODE)}\n"
        alive_s+=f"• ⛽️ 𝗗𝘆𝗻𝗼 𝗦𝗮𝘃𝗲𝗿 : {dynos_saver}\n"
        alive_s+=f"• 💬 𝗕𝗼𝘁 𝗙𝗼𝗿𝘄𝗮𝗿𝗱𝘀 : {_parse_arg(Config.BOT_FORWARDS)}\n"
        alive_s+=f"• ➕ 𝗘𝘅𝘁𝗿𝗮 𝗣𝗹𝘂𝗴𝗶𝗻𝘀 : {_parse_arg(Config.LOAD_UNOFFICIAL_PLUGINS)}"

        await callback_query.answer(alive_s, show_alert=True)


def _parse_arg(arg: bool) -> str:
    return " ✅ 𝙴𝚗𝚊𝚋𝚕𝚎𝚍" if arg else " ❌ 𝙳𝚒𝚜𝚊𝚋𝚕𝚎𝚍"     
