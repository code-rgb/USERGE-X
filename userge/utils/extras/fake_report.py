# Copyright (C) 2020 BY - GitHub.com/code-rgb [TG - @deleteduser420]
# All rights reserved.


import textwrap
from io import BytesIO

from PIL import Image, ImageDraw, ImageFont
from requests import get


async def reported_user_image(u_name: str):
    """reported user"""
    text1 = "Block " + u_name
    text2 = f"Do you want to block {u_name} from messaging and calling you on Telegram?"
    in_memory = BytesIO(
        get("https://telegra.ph/file/886e00818c68f53d24f92.jpg").content
    )
    photo = Image.open(in_memory)
    drawing = ImageDraw.Draw(photo)
    white = (255, 255, 255)
    font1 = ImageFont.truetype("resources/Roboto-Regular.ttf", 45)
    font2 = ImageFont.truetype("resources/Roboto-Medium.ttf", 55)
    drawing.text((132, 201), text1, fill=white, font=font2)
    x = 0
    for u_text in textwrap.wrap(text2, width=38):
        drawing.text(xy=(132, 305 + x), text=u_text, font=font1, fill=white)
        x += 53
    new_pic = BytesIO()
    photo.save(new_pic, format="JPEG")
    new_pic.name = "Blocked.jpg"
    return new_pic
