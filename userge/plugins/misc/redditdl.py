"""Get a Image Post from Reddit"""
# 👍 https://github.com/D3vd for his awesome API
#
# Copyright (C) 2020 BY - GitHub.com/code-rgb [TG - @DeletedUser420]
# All rights reserved.


import requests
from userge import userge, Message
from pyrogram.types import (
    InlineKeyboardMarkup, InlineKeyboardButton,
)


CHANNEL = userge.getCLogger(__name__)
API = "https://meme-api.herokuapp.com/gimme"


@userge.on_cmd("reddit", about={
    'header': "get a random reddit post ",
    'usage': "{tr}reddit [subreddit]",
    'examples': "{tr}reddit dankmemes"})
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
        return await message.err('Value Error', del_in=5)
    if "code" in r:
        code = r['code']
        code_message = r['message']
        return await CHANNEL.log(f"*Error Code: {code}*\n`{code_message}`")
    else:
        if not 'url' in r:
            return await message.err('Coudn\'t Find a post with Image, Please Try Again', del_in=3)
        postlink = r['postLink']
        subreddit = r['subreddit']
        title = r['title']
        image = r['url']
        author = r['author']
        upvote = r['ups']
        captionx = f"<b>{title}</b>\n"
        captionx += f"`Posted by u/{author}`\n"
        captionx += f"↕️ <code>{upvote}</code>\n"
        if r['spoiler']:
            captionx += "⚠️ Post marked as SPOILER\n"
        if r['nsfw']:
            captionx += "🔞 Post marked Adult \n"
    
    if message.client.is_bot:
        buttons = [[InlineKeyboardButton(text=f"Source: r/{subreddit}", url=postlink)]] 
        await userge.bot.send_photo(
            chat_id=message.chat.id,
            photo=image,
            caption=captionx,
            reply_to_message_id=reply_id,
            reply_markup=InlineKeyboardMarkup(buttons)
        )
    else:
        await message.delete()
        captionx += f"Source: [r/{subreddit}]({postlink})"
        await userge.send_photo(
            chat_id=message.chat.id,
            photo=image,
            caption=captionx,
            reply_to_message_id=reply_id,
        )
