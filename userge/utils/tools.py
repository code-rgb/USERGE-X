# pylint: disable=missing-module-docstring
#
# Copyright (C) 2020 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/uaudith/Userge/blob/master/LICENSE >
#
# All rights reserved.

import asyncio
import os
import re
import shlex
from os.path import basename
from typing import List, Optional, Tuple

from html_telegraph_poster import TelegraphPoster
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from ujson import loads

import userge

_LOG = userge.logging.getLogger(__name__)

_BTN_URL_REGEX = re.compile(r"(\[([^\[]+?)]\[buttonurl:(?:/{0,2})(.+?)(:same)?])")


def get_file_id(
    message: "userge.Message",
) -> Optional[str]:
    """ get file_id """
    if message is None:
        return
    file_ = (
        message.audio
        or message.animation
        or message.photo
        or message.sticker
        or message.voice
        or message.video_note
        or message.video
        or message.document
    )
    return file_.file_id if file_ else None


def humanbytes(size: float) -> str:
    """ humanize size """
    if not size:
        return ""
    power = 1024
    t_n = 0
    power_dict = {0: " ", 1: "Ki", 2: "Mi", 3: "Gi", 4: "Ti"}
    while size > power:
        size /= power
        t_n += 1
    return "{:.2f} {}B".format(size, power_dict[t_n])


def time_formatter(seconds: float) -> str:
    """ humanize time """
    minutes, seconds = divmod(int(seconds), 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    tmp = (
        ((str(days) + "d, ") if days else "")
        + ((str(hours) + "h, ") if hours else "")
        + ((str(minutes) + "m, ") if minutes else "")
        + ((str(seconds) + "s, ") if seconds else "")
    )
    return tmp[:-2]


# https://github.com/UsergeTeam/Userge-Plugins/blob/master/plugins/anilist.py
def post_to_telegraph(a_title: str, content: str) -> str:
    """ Create a Telegram Post using HTML Content """
    post_client = TelegraphPoster(use_api=True)
    auth_name = "USERGE-𝑿"
    post_client.create_api_token(auth_name)
    post_page = post_client.post(
        title=a_title,
        author=auth_name,
        author_url="https://t.me/x_xtests",
        text=content,
    )
    return post_page["url"]


async def runcmd(cmd: str) -> Tuple[str, str, int, int]:
    """ run command in terminal """
    args = shlex.split(cmd)
    process = await asyncio.create_subprocess_exec(
        *args, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()
    return (
        stdout.decode("utf-8", "replace").strip(),
        stderr.decode("utf-8", "replace").strip(),
        process.returncode,
        process.pid,
    )


async def take_screen_shot(
    video_file: str, duration: int, path: str = ""
) -> Optional[str]:
    """ take a screenshot """
    _LOG.info(
        "[[[Extracting a frame from %s ||| Video duration => %s]]]",
        video_file,
        duration,
    )
    ttl = duration // 2
    thumb_image_path = path or os.path.join(
        userge.Config.DOWN_PATH, f"{basename(video_file)}.jpg"
    )
    command = f'''ffmpeg -ss {ttl} -i "{video_file}" -vframes 1 "{thumb_image_path}"'''
    err = (await runcmd(command))[1]
    if err:
        _LOG.error(err)
    return thumb_image_path if os.path.exists(thumb_image_path) else None


def parse_buttons(markdown_note: str) -> Tuple[str, Optional[InlineKeyboardMarkup]]:
    """ markdown_note to string and buttons """
    prev = 0
    note_data = ""
    buttons: List[Tuple[str, str, str]] = []
    for match in _BTN_URL_REGEX.finditer(markdown_note):
        n_escapes = 0
        to_check = match.start(1) - 1
        while to_check > 0 and markdown_note[to_check] == "\\":
            n_escapes += 1
            to_check -= 1
        if n_escapes % 2 == 0:
            buttons.append((match.group(2), match.group(3), bool(match.group(4))))
            note_data += markdown_note[prev : match.start(1)]
            prev = match.end(1)
        else:
            note_data += markdown_note[prev:to_check]
            prev = match.start(1) - 1
    note_data += markdown_note[prev:]
    keyb: List[List[InlineKeyboardButton]] = []
    for btn in buttons:
        if btn[2] and keyb:
            keyb[-1].append(InlineKeyboardButton(btn[0], url=btn[1]))
        else:
            keyb.append([InlineKeyboardButton(btn[0], url=btn[1])])
    return note_data.strip(), InlineKeyboardMarkup(keyb) if keyb else None


# https://www.tutorialspoint.com/How-do-you-split-a-list-into-evenly-sized-chunks-in-Python
def sublists(input_list: list, width: int = 3):
    return [input_list[x : x + width] for x in range(0, len(input_list), width)]


# Solves ValueError: No closing quotation by removing ' or " in file name
def safe_filename(path_):
    if path_ is None:
        return
    safename = path_.replace("'", "").replace('"', "")
    if safename != path_:
        os.rename(path_, safename)
    return safename


def clean_obj(obj, convert: bool = False):
    if convert:
        # Pyrogram object to python Dict
        obj = loads(str(obj))
    if isinstance(obj, (list, tuple)):
        return [clean_obj(item) for item in obj]
    if isinstance(obj, dict):
        return {key: clean_obj(value) for key, value in obj.items() if key != "_"}
    return obj
