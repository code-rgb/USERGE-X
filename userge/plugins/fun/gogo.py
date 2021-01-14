# For USERGE-X
# Author: github.com/code-rgb
# (C) All Rights Reserved

from urllib.parse import quote

from bs4 import BeautifulSoup as soup
from pyrogram import filters
from pyrogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.errors import FloodWait
import asyncio
from userge import userge
from userge.utils import check_owner, get_response, rand_key

GOGO = "https://gogoanime.so"
GOGO_DB = {}


class Anime:
    @staticmethod
    async def _get_html(link: str, add_pre: bool = True):
        if add_pre:
            link = GOGO + link
        content = await get_response.text(link)
        return soup(content, "lxml")

    @staticmethod
    async def search(query: str):
        page = await Anime._get_html("/search.html?keyword=" + quote(query))
        out = []
        for i in page.find("ul", {"class": "items"}).findAll("li"):
            result_ = i.find("p", {"class": "name"})
            title = result_.a.text.strip()
            release = i.find("p", {"class": "released"}).text.strip()
            result_url = GOGO + result_.a.get("href")
            image = i.div.a.img.get("src")
            k_ = image.rsplit("/", 1)
            if len(k_) == 2:
                k_[1] = quote(k_[1])
            key_ = rand_key()
            GOGO_DB[key_] = {"url": result_url}
            out.append(
                {
                    "key": key_,
                    "title": title,
                    "release": release,
                    "image": "/".join(k_),
                }
            )
        return out

    @staticmethod
    async def get_eps(link: str):
        page = await Anime._get_html(link, add_pre=False)
        end_ = page.find("ul", {"id": "episode_page"}).findAll("li")[-1].a.get("ep_end")
        return end_

    @staticmethod
    def _get_name(link: str):
        name_ = "/" + (link.rsplit("/", 1))[1]
        return name_

    @staticmethod
    async def get_quality(url: str, episode: int, key_: str):
        endpoint = f"{Anime._get_name(url)}-episode-{episode}"
        page_ = await Anime._get_html(endpoint)
        link_ = page_.find("li", {"class": "dowloads"}).a.get("href")
        # get qualities from download page
        page = await Anime._get_html(link_, add_pre=False)
        btn_, row_ = [], []
        for i in page.findAll("div", {"class": "dowload"}):
            qual = i.a
            if qual.get("target") != "_blank":
                name = qual.text.replace("Download", "").strip()
                btn_.append(InlineKeyboardButton(name, url=qual.get("href")))
                if len(btn_) == 2:
                    row_.append(btn_)
                    btn_ = []
        if len(btn_) != 0:
            row_.append(btn_)
        row_.append(InlineKeyboardButton("Back", callback_data=f"get_eps{key_}"))
        return InlineKeyboardMarkup(row_)


if userge.has_bot:

    @userge.bot.on_callback_query(filters.regex(pattern="get_eps(.*)"))
    @check_owner
    async def get_eps_from_key(c_q: CallbackQuery):
        key_ = c_q.matches[0].group(1)
        url_ = GOGO_DB.get(key_).get("url")
        if not url_:
            return await c_q.answer("Not Found")
        await c_q.answer()
        res = await Anime.get_eps(url_)
        btn_, row_, paginate = [], [], []
        for i in range(1, int(res) + 1):
            btn_.append(
                InlineKeyboardButton(
                    "EP " + str(i), callback_data=f"gogo_get_qual{key_}_{i}"
                )
            )
            if len(btn_) == 4:
                row_.append(btn_)
                btn_ = []
            if len(row_) == 7:
                paginate.append(row_)
                row_ = []
        if len(btn_) != 0:
            row_.append(btn_)
        if len(row_) != 0:
            paginate.append(row_)
        GOGO_DB[key_]["page"] = paginate
        p_len = len(paginate)
        if p_len > 1:
            paginate[0].append(
                [
                    InlineKeyboardButton(
                        "1 / " + str(p_len), callback_data=f"gogo_page{key_}_0"
                    ),
                    InlineKeyboardButton("Next", callback_data=f"gogo_next{key_}_0"),
                ]
            )
        await c_q.edit_message_reply_markup(
            reply_markup=InlineKeyboardMarkup(paginate[0])
        )

    @userge.bot.on_callback_query(
        filters.regex(pattern=r"gogo_get_qual([a-z0-9]+)_([\d]+)")
    )
    @check_owner
    async def get_qual_from_eps(c_q: CallbackQuery):
        key_ = c_q.matches[0].group(1)
        episode = int(c_q.matches[0].group(2))
        url_ = GOGO_DB.get(key_).get("url")
        if not url_:
            return await c_q.answer("Not Found")
        await c_q.answer()
        await c_q.edit_message_text(
            text=f"**>> Episode: {episode}**\n\n📹  Choose Quality",
            reply_markup=(await Anime.get_quality(url=url_, episode=episode, key_=key_)),
        )

    @userge.bot.on_callback_query(
        filters.regex(pattern=r"gogo_(next|back)([a-z0-9]+)_([\d]+)")
    )
    @check_owner
    async def gogo_paginate(c_q: CallbackQuery):
        direction = c_q.matches[0].group(1)
        key_ = c_q.matches[0].group(2)
        pos = int(c_q.matches[0].group(3))
        pages = GOGO_DB.get(key_).get("page")
        p_len = len(pages)
        del_back = False
        if not pages:
            return await c_q.answer("Not Found")
        await c_q.answer()
        if direction == "next":
            if pos >= p_len:
                return await c_q.answer("That's All Folks !")
            page = pos + 1
        else:
            page = pos - 1
            if page =< 0:
                del_back = True

        
        button_base = [
                InlineKeyboardButton(
                    "Back", callback_data=f"gogo_back{key_}_{page}"
                ),
                InlineKeyboardButton(
                    f"{page} / {p_len}",
                    callback_data=f"gogo_page{key_}_{page}",
                ),
                InlineKeyboardButton(
                    "Next", callback_data=f"gogo_next{key_}_{page}"
                ),
        ]
        if del_back:
            button_base.pop(0)
        mkrp = pages[page].append(button_base)
        try:
            await c_q.edit_message_reply_markup(
                reply_markup=InlineKeyboardMarkup(pages[page])
            )
            await asyncio.sleep(0.2)
        except FloodWait as e:
            await asyncio.sleep(e.x + 3)
