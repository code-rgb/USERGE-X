""" Create Buttons Through Bots """

# IMPROVED BY code-rgb
# By @krishna_singhal

import os
import re

from html_telegraph_poster.upload_images import upload_image
from pyrogram.errors.exceptions.bad_request_400 import (
    BadRequest,
    MessageEmpty,
    UserIsBot,
)

from userge import Config, Message, get_collection, userge
from userge.utils import parse_buttons as pb

BUTTON_BASE = get_collection("TEMP_BUTTON")
BTN = r"\[([^\[]+?)\](\[buttonurl:(?:/{0,2})(.+?)(:same)?\])|\[([^\[]+?)\](\(buttonurl:(?:/{0,2})(.+?)(:same)?\))"
BTNX = re.compile(BTN)


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
    """ Create Buttons Through Inline Bots """
    if Config.BOT_TOKEN is None:
        await message.err(
            "First Create a Inline Bot via @Botfather to Create Buttons..."
        )
        return
    replied = message.reply_to_message
    if not (replied and (replied.text or replied.caption)):
        await message.err("Reply a text Msg")
        return
    await message.edit("<code>Creating an inline button...</code>")
    if replied.caption:
        text = replied.caption
        text = check_brackets(text)
        dls_loc = await down_image(message)
        photo_url = str(upload_image(dls_loc))
        BUTTON_BASE.insert_one({"msg_data": text, "photo_url": photo_url})
        os.remove(dls_loc)
    else:
        text = replied.text
        text = check_brackets(text)
        BUTTON_BASE.insert_one({"msg_data": text})
    bot = await userge.bot.get_me()
    x = await userge.get_inline_bot_results(bot.username, "buttonnn")
    await userge.send_inline_bot_result(
        chat_id=message.chat.id, query_id=x.query_id, result_id=x.results[0].id
    )
    await BUTTON_BASE.drop()
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


async def down_image(message):
    message.reply_to_message
    if not os.path.isdir(Config.DOWN_PATH):
        os.makedirs(Config.DOWN_PATH)
    dls = await userge.download_media(
        message=message.reply_to_message, file_name=Config.DOWN_PATH
    )
    return os.path.join(Config.DOWN_PATH, os.path.basename(dls))
