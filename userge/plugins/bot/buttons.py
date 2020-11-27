""" Create Buttons Through Bots """

# IMPROVED BY code-rgb

import json
import os
import re

from pyrogram.errors import BadRequest, MessageEmpty, UserIsBot

from userge import Config, Message, get_collection, userge
from userge.utils import get_file_id_and_ref
from userge.utils import parse_buttons as pb

BUTTON_BASE = get_collection("TEMP_BUTTON")
BTN = r"\[([^\[]+?)\](\[buttonurl:(?:/{0,2})(.+?)(:same)?\])|\[([^\[]+?)\](\(buttonurl:(?:/{0,2})(.+?)(:same)?\))"
BTNX = re.compile(BTN)
PATH = "./userge/xcache/inline_db.json"
CHANNEL = userge.getCLogger(__name__)


class Inline_DB:
    def __init__(self):
        if not os.path.exists(PATH):
            d = {}
            json.dump(d, open(PATH, "w"))
        self.db = json.load(open(PATH))

    def save_msg(self, msg_id: int, msg_data: str, is_media: bool):
        self.db[msg_id] = {"is_media": is_media, "msg_data": msg_data}
        self.save()

    def save(self):
        with open(PATH, "w") as outfile:
            json.dump(self.db, outfile, indent=4)


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
    """ Create Buttons Using Bot """
    if Config.BOT_TOKEN is None:
        await msg.err("First Create a Bot via @Botfather to Create Buttons...")
        return
    replied = msg.reply_to_message
    if not (replied and replied.text):
        await msg.err("Reply a text Msg")
        return
    rep_txt = check_brackets(replied.text)
    text, buttons = pb(rep_txt)
    try:
        await userge.bot.send_message(
            chat_id=msg.chat.id,
            text=text,
            reply_to_message_id=replied.message_id,
            reply_markup=buttons,
        )
    except UserIsBot:
        await msg.err("oops, your Bot is not here to send Msg!")
    except BadRequest:
        await msg.err("Check Syntax of Your Message for making buttons!")
    except MessageEmpty:
        await msg.err("Message Object is Empty!")
    except Exception as error:
        await msg.edit(f"`Something went Wrong! `\n\n**ERROR:** `{error}`")
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
)
async def inline_buttons(message: Message):
    reply = message.reply_to_message
    text_x = None
    is_media = False
    if not reply or message.input_str:
        return await message.err("Reply to a message or give input")
    if message.input_str:
        msg_id = message.message_id
        text_x = message.input_str
        if reply and reply.media:
            f_id, f_ref = get_file_id_and_ref(reply)
            is_media = True if f_id else False
    elif reply:
        msg_id = reply.message_id
        f_id, f_ref = get_file_id_and_ref(reply)
        if f_id and reply.caption:
            is_media = True
            text_x = reply.caption.html
        elif reply.text:
            text_x = reply.text.html

    if not text_x:
        return await message.err("Reply to a message or give input")

    if is_media:
        msg_id = (await reply.forward(Config.LOG_CHANNEL_ID)).message_id

    InlineDB.save_msg(msg_id, text_x, is_media)
    await CHANNEL.log(f"{msg_id}\n\n{text_x}\n\n{is_media}")
    bot = await userge.bot.get_me()
    x = await userge.get_inline_bot_results(bot.username, f"btn_{msg_id}")
    await userge.send_inline_bot_result(
        chat_id=message.chat.id,
        query_id=x.query_id,
        result_id=x.results[0].id,
        reply_to_message_id=replied.message_id,
    )
    await message.delete()


def check_brackets(text):
    unmatch = re.sub(BTN, "", text)
    textx = ""
    for m in BTNX.finditer(text):
        if m.group(1):
            word = m.group(0)
        else:
            change = m.group(6).replace("(", "[").replace(")", "]")
            word = "[" + m.group(5) + "]"
            word += change
        textx += word
    text = unmatch + textx
    return text


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
    medias = get_file_id_and_ref(reply)
    if reply.text:
        msg_text = reply.text.html
    elif medias[0]:
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

    if reply.reply_markup:
        for row in reply.reply_markup.inline_keyboard:
            firstbtn = True
            for btn in row:
                if btn.url:
                    if firstbtn:
                        buttons += f"[{btn.text}]{lbr_}buttonurl:{btn.url}{rbr_}"
                        firstbtn = False
                    else:
                        buttons += f"[{btn.text}]{lbr_}buttonurl:{btn.url}:same{rbr_}"

    if medias[0]:
        await message.delete()
        await message.client.send_cached_media(
            chat_id=message.chat.id,
            file_id=medias[0],
            file_ref=medias[1],
            caption=f"{msg_text}{buttons}",
            reply_to_message_id=reply.message_id,
            parse_mode=None,
        )
    else:
        await message.edit(f"{msg_text}{buttons}", parse_mode=None)
