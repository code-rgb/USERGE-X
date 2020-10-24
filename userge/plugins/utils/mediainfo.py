"""MEDIA INFO"""

# Suggested by - @d0n0t (https://github.com/code-rgb/USERGE-X/issues/9)
# Copyright (C) 2020 BY - GitHub.com/code-rgb [TG - @deleteduser420]
# All rights reserved.

import os

from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from userge import Message, userge
from userge.utils import post_to_telegraph, runcmd

TYPES = [
    "audio",
    "document",
    "animation",
    "video",
    "voice",
    "video_note",
    "photo",
    "sticker",
]


@userge.on_cmd("mediainfo", about={"header": "Get Detailed Info About Replied Media"})
async def mediainfo(message: Message):
    """Get Media Info"""
    reply = message.reply_to_message
    if not reply:
        await message.err("reply to media first", del_in=5)
        return
    process = await message.edit("`Processing ...`")
    x_media = None
    for media_type in TYPES:
        if reply[media_type]:
            x_media = media_type
            break
    if not x_media:
        return await message.err("Reply To a Vaild Media Format", del_in=3)
    file_path = await reply.download()
    output_ = await runcmd(f"mediainfo {file_path}")
    out = output_[0] if len(output_) != 0 else None
    if not out:
        out = "Not Supported"
    body_text = f"""<br>
<h2>JSON</h2>
<code>{reply[x_media]}</code>
<br>
<br>
<h2>DETAILS</h2>
<code>{out}</code>
"""
    link = post_to_telegraph(f"pyrogram.types.{x_media}", body_text)
    if message.client.is_bot:
        markup = InlineKeyboardMarkup(
            [[InlineKeyboardButton(text=x_media.upper(), url=link)]]
        )
        await process.edit_text("ℹ️  <b>MEDIA INFO</b>", reply_markup=markup)

    else:
        await message.edit(f"ℹ️  <b>MEDIA INFO:  [{x_media.upper()}]({link})</b>")

    os.remove(file_path)
