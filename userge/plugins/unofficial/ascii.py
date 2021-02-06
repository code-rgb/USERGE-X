"""Reply to an Media to convert to ascii Image"""
# Module by @deleteduser420 (https://github.com/code-rgb)
# Copyright 2017, Shanshan Wang, MIT license
# Based on https://gist.github.com/wshanshan/c825efca4501a491447056849dd207d6

import os
import random

import numpy as np
from colour import Color
from PIL import Image, ImageDraw, ImageFont, ImageOps
from userge import Config, Message, userge
from userge.utils import media_to_image


@userge.on_cmd(
    "ascii",
    about={
        "header": "Ascii Image",
        "description": "transform on any Media to an Ascii Image. ",
        "usage": " {tr}ascii [reply to media]",
        "flags": {"-alt": "To get inverted Ascii Image"},
        "examples": ["{tr}ascii [reply to media]", "{tr}ascii -alt [reply to media]"],
    },
)
async def ascii_(message: Message):
    replied = message.reply_to_message
    if not replied:
        await message.edit("```Reply To Message Dummy```")
        await message.reply_sticker("CAADAQADhgADwKwII4f61VT65CNGFgQ")
        return
    ascii_type = "alt" if "-alt" in message.flags else ""
    dls_loc = await media_to_image(message)
    if not dls_loc:
        return
    c_list = random_color()
    color1 = c_list[0]
    color2 = c_list[1]
    bgcolor = "#080808"
    img_file = asciiart(dls_loc, 0.3, 1.9, color1, color2, bgcolor, ascii_type)
    await message.client.send_document(
        chat_id=message.chat.id,
        document=img_file,
        force_document=True,
        reply_to_message_id=replied.message_id,
    )
    await message.delete()
    os.remove(img_file)
    os.remove(dls_loc)


def asciiart(in_f, SC, GCF, color1, color2, bgcolor, ascii_type):
    chars = np.asarray(list(" .,:irs?@9B&#"))
    font = ImageFont.load_default()
    letter_width = font.getsize("x")[0]
    letter_height = font.getsize("x")[1]
    WCF = letter_height / letter_width
    img = Image.open(in_f)
    if img.mode != "RGB":
        img = img.convert("RGB")
    if ascii_type == "alt":
        img = ImageOps.invert(img)
    widthByLetter = round(img.size[0] * SC * WCF)
    heightByLetter = round(img.size[1] * SC)
    S = (widthByLetter, heightByLetter)
    img = img.resize(S)
    img = np.sum(np.asarray(img), axis=2)
    img -= img.min()
    img = (1.0 - img / img.max()) ** GCF * (chars.size - 1)
    lines = ("\n".join(("".join(r) for r in chars[img.astype(int)]))).split("\n")
    nbins = len(lines)
    colorRange = list(Color(color1).range_to(Color(color2), nbins))
    newImg_width = letter_width * widthByLetter
    newImg_height = letter_height * heightByLetter
    newImg = Image.new("RGBA", (newImg_width, newImg_height), bgcolor)
    draw = ImageDraw.Draw(newImg)
    leftpadding = 0
    y = 0
    for lineIdx, line in enumerate(lines):
        color = colorRange[lineIdx]
        draw.text((leftpadding, y), line, color.hex, font=font)
        y += letter_height
    image_name = "ascii.png"
    img_file = os.path.join(Config.DOWN_PATH, image_name)
    newImg.save(img_file)
    return img_file


def random_color():
    number_of_colors = 2
    return [
        "#" + "".join([random.choice("0123456789ABCDEF") for j in range(6)])
        for i in range(number_of_colors)
    ]
