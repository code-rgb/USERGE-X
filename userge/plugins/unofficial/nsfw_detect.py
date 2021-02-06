# Copyright (C) 2020 BY - GitHub.com/code-rgb [TG - @deleteduser420]
# All rights reserved.

"""Detects Nsfw content with the help of A.I."""

import os

import aiohttp

# if you prefer requests
# import requests
from userge import Config, Message, userge
from userge.utils import media_to_image


@userge.on_cmd(
    "detect",
    about={
        "header": "Scan media for nsfw content",
        "usage": "{tr}detect [reply to media]",
    },
)
async def detect_(message: Message):
    """detect nsfw"""
    reply = message.reply_to_message
    if not reply:
        await message.err("reply to media !", del_in=5)
        return
    if not Config.DEEP_AI:
        await message.edit(
            "add VAR `DEEP_AI` get Api Key from https://deepai.org/", del_in=7
        )
        return
    image = await media_to_image(message)

    # Request method
    # r = requests.post(
    #     "https://api.deepai.org/api/nsfw-detector",
    #     files={
    #         "image": open(photo, "rb"),
    #     },
    #     headers={"api-key": Config.DEEP_AI},
    # )

    out = await post_photo(image)
    if "status" in out:
        await message.err(out["status"], del_in=6)
        return
    r_json = out["output"]
    pic_id = out["id"]
    percentage = r_json["nsfw_score"] * 100
    detections = r_json["detections"]
    result = "<b><u>Detected Nudity</u> :</b>\n[❯❯❯](https://api.deepai.org/job-view-file/{}/inputs/image.jpg) <code>{:.3f} %</code>\n\n".format(
        pic_id, percentage
    )
    if detections:
        for parts in detections:
            name = parts["name"]
            confidence = int(float(parts["confidence"]) * 100)
            result += f"• {name}:\n   <code>{confidence} %</code>\n"
    await message.edit(result, disable_web_page_preview=True)
    os.remove(image)


# Aiohttp method
async def post_photo(photo: str):
    async with aiohttp.ClientSession() as session:
        async with session.post(
            "https://api.deepai.org/api/nsfw-detector",
            data={
                "image": open(photo, "rb"),
            },
            headers={"api-key": Config.DEEP_AI},
        ) as response:
            result = await response.json()
    return result
