"""Get a Image Post from Reddit"""
# 👍 https://github.com/D3vd for his awesome API
#
# Copyright (C) 2020 BY - GitHub.com/code-rgb [TG - @DeletedUser420]
# All rights reserved.


import requests
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from userge import Message, userge

from ..fun.nsfw import age_verification

CHANNEL = userge.getCLogger(__name__)
API = "https://meme-api.herokuapp.com/gimme"


@userge.on_cmd(
    "reddit",
    about={
        "header": "get a random reddit post ",
        "usage": "{tr}reddit [subreddit]",
        "examples": "{tr}reddit dankmemes",
    },
)
async def reddit_fetch(message: Message):
    """Random reddit post"""
    reply = message.reply_to_message
    reply_id = reply.message_id if reply else None
    sub_r = message.input_str
    subreddit_api = f"{API}/{sub_r}" if sub_r else API
    try:
        cn = requests.get(subreddit_api)
        r = cn.json()
    except ValueError:
        return await message.err("Value Error", del_in=5)
    if "code" in r:
        code = r["code"]
        code_message = r["message"]
        await CHANNEL.log(f"*Error Code: {code}*\n`{code_message}`")
    else:
        if "url" not in r:
            return await message.err(
                "Coudn't Find a post with Image, Please Try Again", del_in=3
            )
        postlink = r["postLink"]
        subreddit = r["subreddit"]
        title = r["title"]
        media_url = r["url"]
        author = r["author"]
        upvote = r["ups"]
        captionx = f"<b>{title}</b>\n"
        captionx += f"`Posted by u/{author}`\n"
        captionx += f"↕️ <code>{upvote}</code>\n"
        if r["spoiler"]:
            captionx += "⚠️ Post marked as SPOILER\n"
        if r["nsfw"]:
            captionx += "🔞 Post marked Adult \n"

            if await age_verification(message):
                return

        if message.client.is_bot:
            buttons = InlineKeyboardMarkup(
                [[InlineKeyboardButton(text=f"Source: r/{subreddit}", url=postlink)]]
            )
        else:
            await message.delete()
            captionx += f"Source: [r/{subreddit}]({postlink})"
            buttons = None

        if media_url.endswith(".gif"):
            await message.client.send_animation(
                chat_id=message.chat.id,
                animation=media_url,
                caption=captionx,
                reply_to_message_id=reply_id,
                reply_markup=buttons,
            )
        else:
            await message.client.send_photo(
                chat_id=message.chat.id,
                photo=media_url,
                caption=captionx,
                reply_to_message_id=reply_id,
                reply_markup=buttons,
            )


def reddit_thumb_link(preview, thumb=None):
    for i in preview:
        if "width=216" in i:
            thumb = i
            break
    if not thumb:
        thumb = preview.pop()
    return thumb.replace("\u0026", "&")
