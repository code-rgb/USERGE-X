"""Fun plugin"""

import asyncio
from re import search

from pyrogram import filters
from pyrogram.errors import BadRequest, Forbidden
from pyrogram.types import CallbackQuery

from userge import Config, Message, userge


@userge.on_cmd("alive", about={"header": "Just For Fun"}, allow_channels=False)
async def alive_inline(message: Message):
    bot = await userge.bot.get_me()
    try:
        x = await userge.get_inline_bot_results(bot.username, "alive")
        y = await userge.send_inline_bot_result(
            chat_id=message.chat.id, query_id=x.query_id, result_id=x.results[0].id
        )
    except (Forbidden, BadRequest) as ex:
        return await message.err(str(ex), del_in=5)
    await message.delete()
    await asyncio.sleep(90)
    await userge.delete_messages(message.chat.id, y.updates[0].id)


if userge.has_bot:

    @userge.bot.on_callback_query(filters.regex(pattern=r"^settings_btn$"))
    async def alive_cb(_, callback_query: CallbackQuery):
        if Config.HEROKU_APP:
            dynos_saver = _parse_arg(Config.RUN_DYNO_SAVER)
        else:
            dynos_saver = "Not Supported"
        alive_s = "Extra plugins : {}\n".format(
            _parse_arg(Config.LOAD_UNOFFICIAL_PLUGINS)
        )
        alive_s += f"Sudo : {_parse_arg(Config.SUDO_ENABLED)}\n"
        alive_s += f"Antispam : {_parse_arg(Config.ANTISPAM_SENTRY)}\n"
        alive_s += f"Dyno Saver : {dynos_saver}\n"
        alive_s += f"Bot Forwards : {_parse_arg(Config.BOT_FORWARDS)}\n"
        alive_s += f"Pm Logger : {_parse_arg(Config.PM_LOGGING)}"
        await callback_query.answer(alive_s, show_alert=True)


def _parse_arg(arg: bool) -> str:
    return "𝙴𝚗𝚊𝚋𝚕𝚎𝚍" if arg else "𝙳𝚒𝚜𝚊𝚋𝚕𝚎𝚍"


async def check_media_link(media_link: str):
    alive_regex_ = r"http[s]?://(i\.imgur\.com|telegra\.ph/file|t\.me)/(\w+)(?:\.|/)(gif|jpg|png|jpeg|[0-9]+)(?:/([0-9]+))?"
    match = search(alive_regex_, media_link)
    if not match:
        return None, None
    if match.group(1) == "i.imgur.com":
        link = match.group(0)
        link_type = "url_gif" if match.group(3) == "gif" else "url_image"
    elif match.group(1) == "telegra.ph/file":
        link = match.group(0)
        link_type = "url_image"
    else:
        link_type = "tg_media"
        if match.group(2) == "c":
            chat_id = int("-100" + str(match.group(3)))
            message_id = match.group(4)
        else:
            chat_id = match.group(2)
            message_id = match.group(3)
        link = [chat_id, int(message_id)]
    return link_type, link
ive_info(),
                reply_markup=Bot_Alive.alive_buttons(),
            )
    else:
        bot = await userge.bot.get_me()
        try:
            x = await userge.get_inline_bot_results(bot.username, "alive")
            y = await userge.send_inline_bot_result(
                chat_id=message.chat.id, query_id=x.query_id, result_id=x.results[0].id
            )
        except (Forbidden, BadRequest) as ex:
            return await message.err(str(ex), del_in=5)
        await message.delete()
        await asyncio.sleep(120)
        await userge.delete_messages(message.chat.id, y.updates[0].id)


if userge.has_bot:

    @userge.bot.on_callback_query(filters.regex(pattern=r"^settings_btn$"))
    async def alive_cb(_, callback_query: CallbackQuery):
        alive_s = f"𝗕𝗢𝗧 𝗨𝗣𝗧𝗜𝗠𝗘 : {userge.uptime}\n"
        alive_s += "𝗘𝘅𝘁𝗿𝗮 𝗣𝗹𝘂𝗴𝗶𝗻𝘀 : {}\n".format(
            _parse_arg(Config.LOAD_UNOFFICIAL_PLUGINS)
        )
        alive_s += f"𝗦𝘂𝗱𝗼 : {_parse_arg(Config.SUDO_ENABLED)}\n"
        alive_s += f"𝗔𝗻𝘁𝗶𝘀𝗽𝗮𝗺 : {_parse_arg(Config.ANTISPAM_SENTRY)}\n"
        if Config.HEROKU_APP:
            alive_s += f"𝗗𝘆𝗻𝗼 𝗦𝗮𝘃𝗲𝗿 : {_parse_arg(Config.RUN_DYNO_SAVER)}\n"
        alive_s += f"𝗕𝗼𝘁 𝗙𝗼𝗿𝘄𝗮𝗿𝗱𝘀 : {_parse_arg(Config.BOT_FORWARDS)}\n"
        alive_s += f"𝗣𝗠 𝗟𝗼𝗴𝗴𝗲𝗿 : {_parse_arg(Config.PM_LOGGING)}"
        await callback_query.answer(alive_s, show_alert=True)


def _parse_arg(arg: bool) -> str:
    return "𝙴𝚗𝚊𝚋𝚕𝚎𝚍" if arg else "𝙳𝚒𝚜𝚊𝚋𝚕𝚎𝚍"


class Bot_Alive:
    @staticmethod
    async def check_media_link(media_link: str):
        alive_regex_ = r"http[s]?://(i\.imgur\.com|telegra\.ph/file|t\.me)/(\w+)(?:\.|/)(gif|jpg|png|jpeg|[0-9]+)(?:/([0-9]+))?"
        match = search(alive_regex_, media_link)
        if not match:
            return None, None
        if match.group(1) == "i.imgur.com":
            link = match.group(0)
            link_type = "url_gif" if match.group(3) == "gif" else "url_image"
        elif match.group(1) == "telegra.ph/file":
            link = match.group(0)
            link_type = "url_image"
        else:
            link_type = "tg_media"
            if match.group(2) == "c":
                chat_id = int("-100" + str(match.group(3)))
                message_id = match.group(4)
            else:
                chat_id = match.group(2)
                message_id = match.group(3)
            link = [chat_id, int(message_id)]
        return link_type, link

    @staticmethod
    def alive_info():
        alive_info = f"""
<b>[Paimon](tg://openmessage?user_id=1486647366)  is Up and Running...

  Python :                 <code>v{versions.__python_version__}</code>
  <b>Pyrogram</b> :         <code>v{versions.__pyro_version__}</code>
  Bot :          <code>v{get_version()}</code>-X-157

  <b>Bot Mode :  {Bot_Alive._get_mode()}</b>
"""
        return alive_info

    @staticmethod
    def _get_mode() -> str:
        if RawClient.DUAL_MODE:
            return "DUAL"
        if Config.BOT_TOKEN:
            return "BOT"
        return "USER"

    @staticmethod
    def alive_buttons():
        buttons = [
            [
                InlineKeyboardButton("SETTINGS", callback_data="settings_btn"),
                InlineKeyboardButton(text="REPO", url=Config.UPSTREAM_REPO),
            ]
        ]
        return InlineKeyboardMarkup(buttons)

    @staticmethod
    def alive_default_imgs():
        alive_imgs = [
            "https://telegra.ph/file/11123ef7dff2f1e19e79d.jpg",
            "https://i.imgur.com/uzKdTXG.jpg",
            "https://telegra.ph/file/6ecab390e4974c74c3764.png",
            "https://telegra.ph/file/995c75983a6c0e4499b55.png",
            "https://telegra.ph/file/86cc25c78ad667ca5e691.png",
        ]
        return rand_array(alive_imgs)
