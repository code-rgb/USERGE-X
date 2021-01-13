# For USERGE-X
# Author: github.com/code-rgb
# (C) All Rights Reserved

from urllib.parse import quote

from bs4 import BeautifulSoup as soup
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from selenium import webdriver

from userge import Config
from userge.utils import get_response

GOGO = "https://gogoanime.so"


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
            out.append(
                {
                    "title": title,
                    "release": release,
                    "result_url": result_url,
                    "image": "/".join(k_),
                }
            )
        return out

    @staticmethod
    async def get_eps(link: str):
        page = await Anime._get_html(link, add_pre=False)
        end_ = page.find("ul", {"id": "episode_page"}).findAll("li")[-1].a.get("ep_end")
        name_ = "/" + (link.rsplit("/", 1))[1]
        return {'total': int(end_), "name": name_}

    @staticmethod
    async def get_quality(anime_: str, episode):
        endpoint = f"{anime_}-episode-{episode}"
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
