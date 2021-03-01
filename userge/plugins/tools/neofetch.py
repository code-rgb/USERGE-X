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
    base_pic = (
        "https://telegra.ph/file/1f62cbef3fe8e24afc6f7.jpg"
        if "Debian" in neofetch
        else (
            "https://i.imgur.com/iBJxExq.jpg"
            if "Kali" in neofetch
            else "https://telegra.ph/file/f3191b7ecdf13867788c2.jpg"
        )
    )
    to_print = neofetch.splitlines()
    in_memory = BytesIO(get(base_pic).content)
    font_url = (
        "https://raw.githubusercontent.com/code-rgb/AmongUs/master/FiraCode-Regular.ttf"
    )
    photo = Image.open(in_memory)
    drawing = ImageDraw.Draw(photo)
    white = (255, 255, 255)
    font = ImageFont.truetype(BytesIO(get(font_url).content), 14)
    x = 0
    y = 0
    for u_text in to_print:
        if ":" in u_text:
            ms = u_text.split(":", 1)
            drawing.text(
                xy=(315, 45 + x),
                text=ms[0] + ":",
                font=font,
                fill=(0, 95, 208) if "Kali" in neofetch else (247, 65, 62),
            )
            drawing.text(
                xy=((8.5 * len(ms[0])) + 315, 45 + x), text=ms[1], font=font, fill=white
            )
        else:
            color = (247, 65, 62) if y == 0 else white
            drawing.text(xy=(315, 53 + y), text=u_text, font=font, fill=color)
        x += 20
        y += 13
    new_pic = BytesIO()
    photo = photo.resize(photo.size, Image.ANTIALIAS)
    photo.save(new_pic, format="JPEG")
    new_pic.name = "NeoFetch.jpg"
    return new_pic
