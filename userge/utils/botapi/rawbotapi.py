import asyncio
from typing import Optional

import aiohttp
import ujson
from pyrogram.types import InlineKeyboardMarkup

from userge.config import Config

from .XParser import mixed_to_html


class XBot:
    def __init__(self):
        token = getattr(Config, "BOT_TOKEN", None)
        if not token:
            return
        self.api = "https://api.telegram.org/bot" + token
        self._session: Optional[aiohttp.ClientSession] = None

    @staticmethod
    def get_new_session() -> aiohttp.ClientSession:
        return aiohttp.ClientSession(
            json_serialize=ujson.dumps, timeout=aiohttp.ClientTimeout(total=300)
        )

    @property
    def session(self) -> Optional[aiohttp.ClientSession]:
        if self._session is None or self._session.closed:
            self._session = self.get_new_session()
        return self._session

    async def post_(self, method: str, params: dict):
        session = self.session
        link = f"{self.api}/{method}"

        timeout = aiohttp.ClientTimeout(total=30)

        try:
            async with session.get(link, params=params, timeout=timeout) as resp:
                data = await resp.json()
        except aiohttp.ClientError as ex:
            await session.close()
            print(ex)
            return
        except asyncio.TimeoutError:
            return
        return data

    async def edit_inline_text(
        self,
        inline_message_id: str,
        text: str,
        reply_markup: InlineKeyboardMarkup = None,
        parse_mode: str = "mixed",
        disable_web_page_preview: bool = False,
    ):
        params = {
            "inline_message_id": inline_message_id,
            "text": await mixed_to_html(text)
            if parse_mode.lower() == "mixed"
            else text,
        }
        if reply_markup:  # :: Optional ::
            params["reply_markup"] = XBot.InlineKeyboard(reply_markup)
        if disable_web_page_preview:
            params["disable_web_page_preview"] = "True"
        if parse_mode.lower() in ("md", "markdown"):
            params["parse_mode"] = "Markdown"
        elif parse_mode.lower() in ("html", "mixed"):
            params["parse_mode"] = "HTML"
        return await self.post_("editMessageText", params)

    async def edit_inline_caption(
        self,
        inline_message_id: str,
        caption: str,
        reply_markup: InlineKeyboardMarkup = None,
        parse_mode: str = "mixed",
    ):
        params = {
            "inline_message_id": inline_message_id,
            "caption": await mixed_to_html(caption)
            if parse_mode.lower() == "mixed"
            else caption,
        }
        if reply_markup:  # :: Optional ::
            params["reply_markup"] = XBot.InlineKeyboard(reply_markup)
        if parse_mode.lower() in ("md", "markdown"):
            params["parse_mode"] = "Markdown"
        elif parse_mode.lower() in ("html", "mixed"):
            params["parse_mode"] = "HTML"
        return await self.post_("editMessageCaption", params)

    async def edit_inline_media(
        self,
        inline_message_id: str,
        media: str,
        reply_markup: InlineKeyboardMarkup = None,
    ):
        params = {"inline_message_id": inline_message_id, "media": media}
        if reply_markup:  # :: Optional ::
            params["reply_markup"] = XBot.InlineKeyboard(reply_markup)
        return await self.post_("editMessageMedia", params)

    async def edit_inline_reply_markup(
        self,
        inline_message_id: str,
        reply_markup: InlineKeyboardMarkup = None,
    ):
        params = {
            "inline_message_id": inline_message_id,
        }
        if reply_markup:  # :: Optional ::
            params["reply_markup"] = XBot.InlineKeyboard(reply_markup)
        return await self.post_("editMessageReplyMarkup", params)

    @staticmethod
    def InlineKeyboard(mkrp):
        if isinstance(mkrp, InlineKeyboardMarkup):
            btn = str(mkrp)
        elif isinstance(mkrp, list):
            btn = str(InlineKeyboardMarkup(mkrp))
        else:
            return None
        buttons = ujson.loads(btn)["inline_keyboard"]
        return ujson.dumps({"inline_keyboard": XBot.clean_markup(buttons)})

    @staticmethod
    def clean_markup(btn_array: list):
        a = []
        b = []
        for rows in btn_array:
            for cell in rows:
                b.append({key: val for key, val in cell.items() if key != "_"})
            a.append(b)
            b = []
        return a


class XMediaTypes:
    @staticmethod
    async def InputMediaPhoto(
        file_id: str, caption: str = None, parse_mode: str = "mixed"
    ):
        media = {"type": "photo", "media": file_id}
        if caption:
            if parse_mode.lower() == "mixed":
                caption = await mixed_to_html(caption)
            media["caption"] = caption
        if parse_mode.lower() in ("md", "markdown"):
            media["parse_mode"] = "Markdown"
        elif parse_mode.lower() in ("html", "mixed"):
            media["parse_mode"] = "HTML"
        return ujson.dumps(media)

    @staticmethod
    async def InputMediaAnimation(
        file_id: str,
        thumb: str = None,
        caption: str = None,
        parse_mode: str = "mixed",
        width: int = None,
        height: int = None,
        duration: int = None,
    ):
        media = {"type": "animation", "media": file_id}
        if caption:
            if parse_mode.lower() == "mixed":
                caption = await mixed_to_html(caption)
            media["caption"] = caption
        if thumb:
            media["thumb"] = thumb
        if width:
            media["width"] = width
        if height:
            media["height"] = height
        if duration:
            media["duration"] = duration
        if parse_mode.lower() in ("md", "markdown"):
            media["parse_mode"] = "Markdown"
        elif parse_mode.lower() in ("html", "mixed"):
            media["parse_mode"] = "HTML"
        return ujson.dumps(media)

    @staticmethod
    async def InputMediaDocument(
        file_id: str,
        thumb: str = None,
        caption: str = None,
        parse_mode: str = "mixed",
        disable_content_type_detection: bool = "None",
    ):
        media = {"type": "document", "media": file_id}
        if caption:
            if parse_mode.lower() == "mixed":
                caption = await mixed_to_html(caption)
            media["caption"] = caption
        if thumb:
            media["thumb"] = thumb
        if isinstance(disable_content_type_detection, bool):
            media["disable_content_type_detection"] = disable_content_type_detection
        if parse_mode.lower() in ("md", "markdown"):
            media["parse_mode"] = "Markdown"
        elif parse_mode.lower() in ("html", "mixed"):
            media["parse_mode"] = "HTML"
        return ujson.dumps(media)

    @staticmethod
    async def InputMediaAudio(
        file_id: str,
        thumb: str = None,
        caption: str = None,
        parse_mode: str = "mixed",
        performer: str = None,
        title: str = None,
        duration: int = None,
    ):
        media = {"type": "audio", "media": file_id}
        if caption:
            if parse_mode.lower() == "mixed":
                caption = await mixed_to_html(caption)
            media["caption"] = caption
        if thumb:
            media["thumb"] = thumb
        if performer:
            media["performer"] = performer
        if duration:
            media["duration"] = duration
        if title:
            media["title"] = title
        if parse_mode.lower() in ("md", "markdown"):
            media["parse_mode"] = "Markdown"
        elif parse_mode.lower() in ("html", "mixed"):
            media["parse_mode"] = "HTML"

        return ujson.dumps(media)

    @staticmethod
    async def InputMediaVideo(
        file_id: str,
        thumb: str = None,
        caption: str = None,
        parse_mode: str = "mixed",
        width: int = None,
        height: int = None,
        duration: int = None,
        supports_streaming: bool = True,
    ):
        media = {
            "type": "video",
            "media": file_id,
            "supports_streaming": True,
        }
        if not supports_streaming:
            media["supports_streaming"] = False
        if caption:
            if parse_mode.lower() == "mixed":
                caption = await mixed_to_html(caption)
            media["caption"] = caption
        if thumb:
            media["thumb"] = thumb
        if width:
            media["width"] = width
        if height:
            media["height"] = height
        if duration:
            media["duration"] = duration

        if parse_mode.lower() in ("md", "markdown"):
            media["parse_mode"] = "Markdown"
        elif parse_mode.lower() in ("html", "mixed"):
            media["parse_mode"] = "HTML"

        return ujson.dumps(media)


# bot api class
xbot = XBot()
