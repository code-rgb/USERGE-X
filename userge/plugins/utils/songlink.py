"""song link for all supported music streaming platform"""

# Copyright (C) 2021 BY USERGE-X
# All rights reserved.
#
# Author: https://github.com/code-rgb [TG: @DeletedUser420]
#
# Idea : https://t.me/USERGE_X/107828
# API: https://odesli.co/

from html import escape
from re import search
from typing import Dict, Optional
from urllib.parse import quote

from userge import Message, userge
from userge.utils import get_response


@userge.on_cmd(
    "songlink",
    about={
        "header": "link to a song on any supported music streaming platform",
        "usage": "{tr}songlink [URL]",
    },
)
async def getlink_(message: Message):
    """song links"""
    if not (link := (await find_url_from_msg(message))[0]):
        return
    await message.edit(f'🔎 Searching for `"{link}"`')
    resp = await get_song_link(link)
    if resp is None:
        await message.err(
            "Oops something went wrong! Please try again later.", del_in=5
        )
        return
    await message.edit(get_data(resp) or "404 Not Found")


async def get_song_link(link: str) -> Optional[Dict]:
    try:
        r = await get_response.json(
            "https://api.song.link/v1-alpha.1/links?url=" + quote(link)
        )
    except ValueError:
        pass
    else:
        return r


async def find_url_from_msg(message: Message, show_err: bool = True) -> Optional[str]:
    reply = message.reply_to_message
    msg = None
    if message.input_str:
        txt = message.input_str
        msg = message
    elif reply and (reply.text or reply.caption):
        txt = reply.text or reply.caption
        msg = reply
    if not msg:
        if show_err:
            await message.err("No Input Found !", del_in=5)
        return
    try:
        url_e = [
            _
            for _ in (msg.entities or msg.caption_entities)
            if _.type in ("url", "text_link")
        ]
    except TypeError:
        if show_err:
            await message.err("No Valid URL was found !", del_in=5)
        return
    if len(url_e) > 0:
        y = url_e[0]
        link = txt[y.offset : (y.offset + y.length)] if y.type == "url" else y.url
        return link, msg


def beautify(text: str) -> str:
    match = search(r"[A-Z]", text)
    if match:
        x = match.group(0)
        text = text.replace(x, " " + x)
    text = text.title()
    if "Youtube" in text:
        out = text.replace("Youtube", "YouTube")
    elif "Soundcloud" in text:
        out = text.replace("Soundcloud", "SoundCloud")
    else:
        out = text
    return out


def get_data(resp: Dict) -> str:
    platforms = resp["linksByPlatform"]
    data_ = resp["entitiesByUniqueId"][resp["entityUniqueId"]]
    title = data_.get("title")
    artist = data_.get("artistName")
    thumb = data_.get("thumbnailUrl")
    des = f"[\u200c]({thumb})" if thumb else ""
    if title:
        des += f"{htmlink(title, platforms[data_['platforms'][0]].get('url'))}"
    if artist:
        des += f"\nARTIST(S): __{artist}__"
    des += "\n\n🎧  LISTEN ON:\n<b>" + "  |  ".join(
        [
            f"{htmlink(beautify(x), platforms[x].get('url'))}"
            for x in platforms
            if x != "itunes"
        ]
    )
    return des + "</b>"


def htmlink(text: str, link: str) -> str:
    return f"<a href={escape(link)}>{escape(text)}</a>"
