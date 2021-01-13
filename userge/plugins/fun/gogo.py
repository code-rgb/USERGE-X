# For USERGE-X
# Author: github.com/code-rgb
# (C) All Rights Reserved

from urllib.parse import quote

from bs4 import BeautifulSoup as soup
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from pyrogram import filters
from userge.utils import check_owner, get_response, rand_key
from userge import userge

GOGO = "https://gogoanime.so"
GOGO_DB = {"results": {}}


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
            GOGO_DB["results"][key_] = result_url
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
    async def get_quality(url: str, episode: int):
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
            row_.append(btn)
        return InlineKeyboardMarkup(row_)


if userge.has_bot:

    @userge.bot.on_callback_query(filters.regex(pattern="get_eps(.*)"))
    @check_owner
    async def get_eps_from_key(c_q: CallbackQuery):
        key_ = c_q.matches[0].group(1)
        url_ = GOGO_DB["results"].get(key_)
        if not url_:
            return await c_q.answer("Not Found")
        res = await Anime.get_eps(url_)
        btn_, row_ = [], []
        for i in range(1, int(res) + 1):
            btn_.append(
                InlineKeyboardButton(
                    "EP " + str(i), callback_data=f"gogo_get_qual{key_}_{i}"
                )
            )
            if len(btn_) == 5:
                row_.append(btn_)
                btn_ = []
        if len(btn_) != 0:
            row_.append(btn)
        await c_q.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup(row_))

    @userge.bot.on_callback_query(
        filters.regex(pattern=r"gogo_get_qual([a-z0-9]+)_([\d]+)")
    )
    @check_owner
    async def get_qual_from_eps(c_q: CallbackQuery):
        key_ = c_q.matches[0].group(1)
        episode = int(c_q.matches[0].group(2))
        url_ = GOGO_DB["results"].get(key_)
        if not url_:
            return await c_q.answer("Not Found")
        await c_q.edit_message_text(
            text=f"**>> Episode: {episode}**\n\n📹  Choose Quality",
            reply_markup=(await Anime.get_quality(url=url_, episode=episode)),
        )
