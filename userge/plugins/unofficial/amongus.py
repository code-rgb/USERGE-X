"""Create Cool Among US Stickers"""

# Copyright (C) 2020 BY USERGE-X
# All rights reserved.
# Author : https://github.com/KeyZenD ( FTG Modules )
# Ported By Github/code-rgb [TG- @deleteduser420]


import os
from io import BytesIO
from random import randint
from textwrap import wrap

from PIL import Image, ImageDraw, ImageFont
from requests import get
from userge import Config, Message, userge

CLRS = {
    "red": 1,
    "lime": 2,
    "green": 3,
    "blue": 4,
    "cyan": 5,
    "brown": 6,
    "purple": 7,
    "pink": 8,
    "orange": 9,
    "yellow": 10,
    "white": 11,
    "black": 12,
}


@userge.on_cmd(
    "amongus",
    about={
        "header": "Create a Sticker based on the popular game Among Us",
        "usage": "{tr}amongus [color] [text | reply to message]",
        "color": "<code>-red ,  -lime ,  -green ,  -blue ,  -cyan ,  -brown ,  "
        "-purple ,  -pink ,  -orange ,  -yellow ,  -white ,  -black"
        "</code>",
        "examples": ["{tr}amongus call an emergency meeting", "{tr}amongus -red Sus"],
    },
)
async def among_us(message: Message):
    """among us sticker"""
    reply = message.reply_to_message
    args = message.filtered_input_str
    if args:
        text = args
    elif reply:
        text = args or reply.text
    else:
        await message.err("`Input not found!...`", del_in=5)
        return
    await message.edit("What the SUS")
    if message.flags:
        choice = list((message.flags).keys())[0]
        choice = choice.replace("-", "")
        if choice not in list(CLRS):
            return await message.err(
                "Invalid color input ! See help for more info.", del_in=5
            )
        color = CLRS[choice]
    else:
        color = randint(1, 12)
    stickerx = await amongus_gen(text, color)
    reply_id = reply.message_id if reply else None
    await message.delete()
    await userge.send_sticker(
        message.chat.id, sticker=stickerx, reply_to_message_id=reply_id
    )
    os.remove(stickerx)


async def amongus_gen(text: str, clr: int) -> str:
    url = "https://raw.githubusercontent.com/code-rgb/AmongUs/master/"
    font = ImageFont.truetype(BytesIO(get(url + "bold.ttf").content), 60)
    imposter = Image.open(BytesIO(get(f"{url}{clr}.png").content))
    text_ = "\n".join(["\n".join(wrap(part, 30)) for part in text.split("\n")])
    w, h = ImageDraw.Draw(Image.new("RGB", (1, 1))).multiline_textsize(
        text_, font, stroke_width=2
    )
    text = Image.new("RGBA", (w + 30, h + 30))
    ImageDraw.Draw(text).multiline_text(
        (15, 15), text_, "#FFF", font, stroke_width=2, stroke_fill="#000"
    )
    w = imposter.width + text.width + 10
    h = max(imposter.height, text.height)
    image = Image.new("RGBA", (w, h))
    image.paste(imposter, (0, h - imposter.height), imposter)
    image.paste(text, (w - text.width, 0), text)
    image.thumbnail((512, 512))
    output = BytesIO()
    output.name = "imposter.webp"
    webp_file = os.path.join(Config.DOWN_PATH, output.name)
    image.save(webp_file, "WebP")
    return webp_file
