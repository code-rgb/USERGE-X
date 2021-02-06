# Copyright (C) 2020 BY - GitHub.com/code-rgb [TG - @deleteduser420]
# All rights reserved.

import time

from userge import Message, userge
from userge.utils import post_to_telegraph, time_formatter

from ..utils.telegraph import upload_media_


@userge.on_cmd(
    "tg",
    about={
        "header": "For Posting Text on Telegraph",
        "flags": {"-m": "To Post Media with Caption", "-mono": "For Monospace text"},
        "usage": "{tr}tg Title [reply to text]",
    },
)
async def tele_text(message: Message):
    """Paste on Telegra.ph"""
    start = time.time()
    replied = message.reply_to_message
    if not replied:
        await message.err("Reply To Message First !", del_in=5)
        return
    if not replied.text and not replied.caption:
        await message.err("Replied Message Doesn't Contain Text. 🤨", del_in=5)
        return
    await message.edit("Pasting...")
    text = replied.text or replied.caption
    if "-mono" in message.flags:
        text = "<code>{}</code>".format(text)
    else:
        text = text.html
    if "-m" in message.flags:
        if not (
            replied.photo or replied.video or replied.document or replied.animation
        ):
            return await message.err("Media Type Not Supported", del_in=3)
        link = await upload_media_(message)
        if link == "error":
            return
        if link.endswith((".mp4", ".mkv")):
            media_link = f'<video controls src="https://telegra.ph{link}">Browser not supported</video>'
        else:
            media_link = f'<img src="https://telegra.ph{link}">'
        text = media_link + text
    user = await userge.get_me()
    user_n = f"@{user.username}" if user.username else user.first_name
    title = message.filtered_input_str
    if not title:
        title = f"By {user_n}"
    link = post_to_telegraph(title, text)
    msg = "**Pasted to -** "
    msg += f"<b><a href={link}>{link.replace('http://telegra.ph/', '')}</a></b>\n"
    end = time.time()
    msg += f"in <code>{time_formatter(end - start)}</code> sec"
    await message.edit(msg, disable_web_page_preview=True)
