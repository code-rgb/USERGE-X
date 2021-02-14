"""Google IMGS"""

#  Copyright (C) 2021 BY USERGE-X
#  All rights reserved.
#
#  Author: https://github.com/code-rgb [TG: @DeletedUser420]


from userge import Message, userge, Config, pool
from google_images_download.google_images_download import googleimagesdownload
from .upload import photo_upload, doc_upload
from datetime import datetime
from userge.utils import sublists
from pyrogram.types import InputMediaDocument, InputMediaPhoto
import os
from shutil import rmtree
from pathlib import Path
import asyncio

class Colors:
    # fmt: off
    choice = [
        "red", "orange", "yellow",
        "green", "teal", "blue",
        "purple", "pink", "white",
        "gray", "black", "brown",
    ]
    # fmt: on

@userge.on_cmd(
    "gimg",
    about={
        "header": "Google Image Downloader",
        "description": "Search and download images from google and upload to telegram",
        "flags": {"-l": "limit [1 - 100] (default is 5)", "-s": "size [0-2] <2 - best> (default is 1)", "-d": "Upload as document", "-gif": "download gifs", "-down": "download only"},
        "usage": "{tr}gimg [flags] [query|reply to text]",
        "color": ["-" + _ for  _ in Colors.choice],
        "examples": [
            "{tr}gimg -red wallpaper <red wallpapers>",
            "{tr}gimg tigers <upload 5 pics as gallery>",
            "{tr}gimg -d -l20 tigers <upload 20 pics as document>",
            "{tr}gimg -gif rain <download 5 gifs>",
        ],
    },
    del_pre=True
)
async def gimg_down(message: Message):
    """google images downloader"""
    reply = message.reply_to_message
    args = message.filtered_input_str
    if args:
        text = args
    elif reply:
        text = args or reply.text or reply.caption
    else:
        await message.err("`Input not found!...`", del_in=5)
        return
    await message.edit("🔎")
    start_t = datetime.now()
    color_ = None
    flags_ = message.flags
    allow_gif = bool("gif" in flags_)
    upload_ = not bool("down" in flags_ or allow_gif)
    doc_ = bool("d" in flags_)
    limit = min(int(flags_.get("l", 3)), 100)
    if flags_:
        size = min(int(flags_.get("s", 1)), 3)
        for i in flags_:
            if i in Colors.choice:
                color_ = i
                break
        arguments = await get_arguments(
            query=text,
            limit=limit,
            img_format="gif" if allow_gif else "jpg",
            color=color_,
            upload=upload_,
            size=size
        )
    else:
        arguments = await get_arguments(query=text)
    await message.edit("⬇️  Downloading ...")
    results = await gimg_downloader(arguments=arguments)
    if upload:
        await message.edit("⬆️  Uploading ...")
        try:
            await upload_image_grp(results=results, message=message, doc=doc_)
        except Exception as err:
            await message.err(str(err), del_in=7)
        else:
            end_t = datetime.now()
            time_taken_s = (end_t - start_t).seconds
            await message.edit(f"Uploaded {limit} Pics in {time_taken_s} sec with {results[1]} errors.", del_in=5, log=__name__)
    else:
        end_t = datetime.now()
        time_taken_s = (end_t - start_t).seconds
        await message.edit(f'Downloaded {limit} {"Gifs" if gif else "Pics"} to `{arguments["output_directory"]}` in {time_taken_s} sec with {results[1]} errors.', log=__name__)



async def get_arguments(query: query, limit: int = 5, img_format: str = "jpg", color: str = None, upload: bool = True, size: int = 1):
    arguments = {
        "keywords": query,
        "limit": limit,
        "format": img_format,
        "size": size,
    }
    if upload:
        output_directory = await check_path()
        arguments["no_directory"] = "no_directory"
    else:
        output_directory = await check_path(path_name=query)
    arguments["output_directory"] = output_directory
    if color:
        arguments["color"] = color
    # ------ size ------ #
    if size <= 0:
        size_ = "icon"
    elif size == 1:
        size_ = "medium"
    else:
        size_ = "large"
    arguments["size"] = size_
    # ------------------- #
    return arguments

@pool.run_in_thread
def check_path(path_name: str = "GIMG"):
    path_ = os.path.join(Config.DOWN_PATH, path_name)
    if os.path.lexists(path_):
        rmtree(path_, ignore_errors=True)
    os.mkdir(path_)
    return path_

@pool.run_in_thread
def gimg_downloader(arguments=arguments):
    response = googleimagesdownload()
    path_ = response.download(arguments)
    return path_

async def upload_image_grp(results=tuple, message: Message, doc: bool):
    key_ = list(results[0])[0]
    medias_ = results[0][key_]
    if message.process_is_canceled:
        await message.client.stop_transmission()
    if len(medias_) == 0:
        await message.err(f"No result Found `'{key_}'`", del_in=7)
    if len(medias_) == 1:
        path_ = Path(medias_[0])
        if doc:
            await doc_upload(message=message, path=path_, del_path=True)
        else:
            await photo_upload(message=message, path=path_, del_path=True)
    else:
        mgroups = sublists([(InputMediaDocument(media=x) if doc else InputMediaPhoto(media=x)) for x in medias_], width=10)
        for m_ in mgroups:
            try:
                await message.client.send_media_group(message.chat.id, media=m_)
                await asyncio.sleep(1)
            except FloodWait as f:
                await asyncio.sleep(f.x + 3)



