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
    async def _get_html(link: str, down_link: bool = False):
        if not down_link:
            link = GOGO + link
        content = await get_response.text(link)
        return soup(content, "lxml")

    @staticmethod
    async def search(query: str):
        page = await Anime._get_html("/search.html?keyword=" + quote(query))
        out = []
        for i in page.find("ul", {"class": "items"}).findAll("li"):
            i.div.a.img.get("src")
            result_ = i.find("p", {"class": "name"})
            title = result_.a.text.strip()
            release = i.find("p", {"class": "released"}).text.strip()
            result_url = GOGO + result_.a.get("href")
            out.append({"title": title, "release": release, "result_url": result_url})
        return out

    @staticmethod
    async def get_eps(link: str):
        chrome_options = webdriver.ChromeOptions()
        chrome_options.binary_location = Config.GOOGLE_CHROME_BIN
        chrome_options.add_argument("--ignore-certificate-errors")
        chrome_options.add_argument("--test-type")
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-gpu")
        driver = webdriver.Chrome(chrome_options=chrome_options)
        driver.get(link)
        html = driver.find_element_by_xpath('//*[@id="episode_related"]').get_attribute(
            "innerHTML"
        )
        driver.close()
        page = soup(html, "lxml")
        out = {}
        for i in page.findAll("a"):
            ep_ = i.div.text.replace("EP", "").strip()
            if ep_.isdigit():
                out[int(ep_)] = i.get("href").strip()
        return out

    @staticmethod
    async def get_quality(endpoint: str):
        page_ = await Anime._get_html(endpoint)
        link_ = page_.find("li", {"class": "dowloads"}).a.get("href")
        # get qualities from download page
        page = await Anime._get_html(link_, down_link=True)
        btn_, row_ = [], []
        for i in page.findAll("div", {"class": "dowload"}):
            qual = i.a
            if qual.get("target") != "_blank":
                name = qual.text.replace("Download", "").strip()
                if "HDP" not in name:
                    btn_.append(InlineKeyboardButton(name, url=qual.get("href")))
                    if len(btn_) == 2:
                        row_.append(btn_)
                        btn_ = []
        if len(btn_) != 0:
            row_.append(btn)
        return InlineKeyboardMarkup(row_)
