""" Create Buttons Through Bots """

# IMPROVED BY code-rgb

import os
from asyncio import gather
from re import compile as comp_regex

import ujson
from pyrogram.errors import BadRequest, UserIsBot
from pyrogram.types import ReplyKeyboardRemove

from userge import Config, Message, userge
from userge.utils import get_file_id
from userge.utils import parse_buttons as pb

from .bot_pm import get_bot_info

BTN_REGEX = comp_regex(
    r"\[([^\[]+?)](\[buttonurl:(?:/{0,2})(.+?)(:same)?]|\(buttonurl:(?:/{0,2})(.+?)(:same)?\))"
)
PATH = "./userge/xcache/inline_db.json"
CHANNEL = userge.getCLogger(__name__)


class Inline_DB:
    def __init__(self):
        if not os.path.exists(PATH):
            d = {}
            ujson.dump(d, open(PATH, "w"))
        with open(PATH) as r:
            self.db = ujson.load(r)

    def save_msg(self, rnd_id: int, msg_content: str, media_valid: bool, media_id: int):
        self.db[rnd_id] = {
            "msg_content": msg_content,
            "media_valid": media_valid,
            "media_id": media_id,
        }
        self.save()

    def save(self):
        with open(PATH, "w") as outfile:
            ujson.dump(self.db, outfile, indent=4)


InlineDB = Inline_DB()


@userge.on_cmd(
    "cbutton",
    about={
        "header": "Create buttons Using bot",
        "description": "First Create a Bot via @Botfather and "
        "Add bot token To Config Vars",
        "usage": "{tr}cbutton [reply to button msg]",
        "buttons": "<code>[name][buttonurl:link] or [name](buttonurl:link)</code> - <b>add a url button</b>\n"
        "<code>[name][buttonurl:link:same]</code> - "
        "<b>add a url button to same row</b>",
    },
)
async def create_button(msg: Message):
    """Create Buttons Using Bot"""
    if Config.BOT_TOKEN is None:
        await msg.err("First Create a Bot via @Botfather to Create Buttons...")
        return
    string = msg.input_raw
    replied = msg.reply_to_message
    file_id = None
    if replied:
        if replied.caption:
            string = replied.caption.html
        elif replied.text:
            string = replied.text.html
        file_id = get_file_id(replied)
    if not string:
        await msg.err("`need an input!`")
        return
    text, markup = pb(check_brackets(string))
    if not text:
        await msg.err("`need text too!`")
        return
    message_id = replied.message_id if replied else None
    client = msg.client if msg.client.is_bot else msg.client.bot
    try:
        if replied and replied.media and file_id:
            await client.send_cached_media(
                chat_id=msg.chat.id,
                file_id=file_id,
                caption=text,
                reply_to_message_id=message_id,
                reply_markup=markup,
            )
        else:
            await client.send_message(
                chat_id=msg.chat.id,
                text=text,
                reply_to_message_id=message_id,
                reply_markup=markup,
            )
    except UserIsBot:
        await msg.err("oops, your Bot is not here to send Msg!")
    except BadRequest:
        await msg.err("Check Syntax of Your Message for making buttons!")
    except Exception as error:
        await msg.edit(f"`Something went Wrong! 😁`\n\n**ERROR:** `{error}`")
    else:
        await msg.delete()


@userge.on_cmd(
    "ibutton",
    about={
        "header": "Create buttons Using Inline Bot",
        "description": "First Create a Inline via @Botfather and "
        "Add bot token To Config Vars",
        "usage": "{tr}ibutton [reply to button msg]",
        "buttons": "<code>[name][buttonurl:link] or [name](buttonurl:link)</code> - <b>add a url button</b>\n"
        "<code>[name][buttonurl:link:same]</code> - "
        "<b>add a url button to same row</b>",
    },
    check_downpath=True,
)
async def inline_buttons(message: Message):
    await message.edit("<code>Creating an Inline Button...</code>")
    reply = message.reply_to_message
    msg_content = None
    media_valid = False
    media_id = 0
    if reply:
        media_valid = bool(get_file_id(reply))

    if message.input_str:
        msg_content = message.input_str
        if media_valid:
            media_id = (await reply.forward(Config.LOG_CHANNEL_ID)).message_id

    elif reply:
        if media_valid:
            media_id = (await reply.forward(Config.LOG_CHANNEL_ID)).message_id
            msg_content = reply.caption.html if reply.caption else None
        elif reply.text:
            msg_content = reply.text.html

    if not msg_content:
        return await message.err("Content not found", del_in=5)

    rnd_id = userge.rnd_id()
    msg_content = check_brackets(msg_content)
    InlineDB.save_msg(rnd_id, msg_content, media_valid, media_id)
    x = await userge.get_inline_bot_results(
        (await get_bot_info())["bot"].uname, f"btn_{rnd_id}"
    )
    await gather(
        userge.send_inline_bot_result(
            chat_id=message.chat.id,
            query_id=x.query_id,
            result_id=x.results[0].id,
        ),
        message.delete(),
    )


def check_brackets(text: str):
    unmatch = BTN_REGEX.sub("", text)
    textx = ""
    for m in BTN_REGEX.finditer(text):
        if m.group(3):
            textx += m.group(0)
        elif m.group(5):
            textx += f"[{m.group(1)}][buttonurl:{m.group(5)}{m.group(6) or ''}]"
    return unmatch + textx


@userge.on_cmd(
    "noformat",
    about={
        "header": "decompile a message",
        "description": "reply to a message to get it without any text formatting",
        "flags": {"-alt": "for MissRose bot supported format"},
    },
)
async def noformat_message(message: Message):
    reply = message.reply_to_message
    msg_text = None
    buttons = ""
    media = get_file_id(reply)
    if reply.text:
        msg_text = reply.text.html
    elif media:
        msg_text = reply.caption.html if reply.caption else None
    else:
        return await message.err(
            "Not Supported!, reply to a supported media type or text", del_in=5
        )

    if "-alt" in message.flags:
        lbr_ = "("
        rbr_ = ")"
    else:
        lbr_ = "["
        rbr_ = "]"

    if reply.reply_markup and not isinstance(reply.reply_markup, ReplyKeyboardRemove):
        for row in reply.reply_markup.inline_keyboard:
            firstbtn = True
            for btn in row:
                if btn.url:
                    if firstbtn:
                        buttons += f"[{btn.text}]{lbr_}buttonurl:{btn.url}{rbr_}"
                        firstbtn = False
                    else:
                        buttons += f"[{btn.text}]{lbr_}buttonurl:{btn.url}:same{rbr_}"

    if media:
        await gather(
            message.delete(),
            message.client.send_cached_media(
                chat_id=message.chat.id,
                file_id=media,
                caption=f"{msg_text}{buttons}",
                reply_to_message_id=reply.message_id,
                parse_mode=None,
            ),
        )
    else:
        await message.edit(f"{msg_text}{buttons}", parse_mode=None)
