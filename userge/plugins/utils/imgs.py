"""
Download & Upload Images on Telegram\n
Syntax: `.img <Name>` or `.img (replied message)`
\n Upgraded and Google Image Error Fixed by @NeoMatrix90 aka @kirito6969
from oub
"""
import os
import shutil

from pyrogram.types import InputMediaPhoto

from userge import Message, userge
from userge.img import googleimagesdownload


@userge.on_cmd(
    "img",
    about={
        "header": "Fetch images from google",
        "flags": {"-l": "limit : defaults to 3"},
        "usage": "{tr}img [flag] [query] or {tr}img [flag] reply_to_message",
        "examples": ["{tr}img userge", "{tr}img -l3 userge"],
    },
)
async def img_sampler(message: Message):
    query = message.filtered_input_str or message.reply_to_message.text
    if not query:
        return await message.edit(
            "Reply to a message or pass a query to search!", del_in=10
        )
    cat = await message.edit("`Processing...`")
    lim = int(message.flags.get("-l", 3))
    if lim > 10:
        lim = int(10)
    if lim <= 0:
        lim = int(1)
    response = googleimagesdownload()
    # creating list of arguments
    arguments = {
        "keywords": query,
        "limit": lim,
        "format": "jpg",
        "no_directory": "no_directory",
    }
    # passing the arguments to the function
    try:
        paths = response.download(arguments)
    except Exception as e:
        return await cat.edit(f"Error: \n`{e}`")
    media = []
    if paths:
        lst = paths[0][query]
        for kek in lst:
            media.append(InputMediaPhoto(kek))
    else:
        return await message.reply("fk")
    await message.client.send_media_group(message.chat.id, media=media)
    shutil.rmtree(os.path.dirname(os.path.abspath(lst[0])), ignore_errors=True)
    await cat.delete()
