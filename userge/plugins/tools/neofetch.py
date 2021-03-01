# Copyright (C) 2020 BY - GitHub.com/code-rgb [TG - @deleteduser420]
# All rights reserved.


from io import BytesIO

from PIL import Image, ImageDraw, ImageFont
from requests import get

from userge import Message, userge
from userge.utils import runcmd


@userge.on_cmd(
    "neofetch",
    about={
        "header": "Neofetch is a command-line system information tool",
        "description": "displays information about your operating system, software and hardware in an aesthetic and visually pleasing way.",
        "usage": " {tr}neofetch",
        "flags": {"-img": "To Get output as Image"},
        "examples": ["{tr}neofetch", "{tr}neofetch -img"],
    },
)
async def neofetch_(message: Message):
    await message.edit("Getting System Info ...")
    reply = message.reply_to_message
    reply_id = reply.message_id if reply else None
    if "-img" in message.flags:
        await message.delete()
        await message.client.send_photo(
            message.chat.id, await neo_image(), reply_to_message_id=reply_id
        )
    else:
        await message.edit(
            "<code>{}</code>".format((await runcmd("neofetch --stdout"))[0]),
            parse_mode="html",
        )


async def neo_image():
    neofetch = (await runcmd("neofetch --stdout"))[0]
    font_color = (255, 42, 38)  # Red
    white = (255, 255, 255)
    if "Debian" in neofetch:
        base_pic = "https://telegra.ph/file/1f62cbef3fe8e24afc6f7.jpg"
    elif "Kali" in neofetch:
        base_pic = "https://i.imgur.com/iBJxExq.jpg"
        font_color = (87, 157, 255)  # Blue
    else:
        base_pic = "https://telegra.ph/file/f3191b7ecdf13867788c2.jpg"
    font_url = (
        "https://raw.githubusercontent.com/code-rgb/AmongUs/master/FiraCode-Regular.ttf"
    )
    photo = Image.open(BytesIO(get(base_pic).content))
    drawing = ImageDraw.Draw(photo)
    font = ImageFont.truetype(BytesIO(get(font_url).content), 14)
    x = 0
    y = 0
    for u_text in neofetch.splitlines():
        if ":" in u_text:
            ms = u_text.split(":", 1)
            drawing.text(
                xy=(315, 45 + x),
                text=ms[0] + ":",
                font=font,
                fill=font_color,
            )
            drawing.text(
                xy=((8.5 * len(ms[0])) + 315, 45 + x), text=ms[1], font=font, fill=white
            )
        else:
            color = font_color if y == 0 else white
            drawing.text(xy=(315, 53 + y), text=u_text, font=font, fill=color)
        x += 20
        y += 13
    new_pic = BytesIO()
    photo = photo.resize(photo.size, Image.ANTIALIAS)
    photo.save(new_pic, format="JPEG")
    new_pic.name = "NeoFetch.jpg"
    return new_pic
