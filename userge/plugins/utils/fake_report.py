
# Copyright (C) 2020 BY - GitHub.com/code-rgb [TG - @deleteduser420]
# All rights reserved.

import os
from PIL import Image, ImageDraw, ImageFont
from userge import Config
import textwrap
from requests import get
from io import BytesIO



async def reported_user_image(u_name: str):
    """reported user"""
    text1 = 'Block ' + u_name 
    text2 = f'Do you want to block {u_name} from messaging and calling you on Telegram?'
    photo = Image.open(BytesIO(get("https://telegra.ph/file/886e00818c68f53d24f92.jpg").content))
    drawing = ImageDraw.Draw(photo)
    white = (255, 255, 255)
    font1 = ImageFont.truetype("resources/Roboto-Regular.ttf", 45)
    font2 = ImageFont.truetype("resources/Roboto-Medium.ttf", 55)
    drawing.text((132, 201), text1, fill=white, font=font2)
    x = 0
    for u_text in textwrap.wrap(text2, width=38):
        drawing.text(
                    xy=(132, 305 + x),
                    text=u_text,
                    font=font1,
                    fill=white
        )
        x += 53
    img_file = os.path.join(Config.DOWN_PATH, "temp_image.jpg")
    photo.save(img_file)
    return img_file