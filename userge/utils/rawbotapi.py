import json

from userge.config import Config

from .helper import AioHttp


class XBot:
    def __init__(self):
        token = getattr(Config, "BOT_TOKEN", None)
        if not token:
            return
        self.api = "https://api.telegram.org/bot" + token

    async def editMessageText(
        self,
        inline_message_id: str,
        text: str,
        reply_markup: list = None,
        parse_mode: str = "HTML",
        disable_web_page_preview: bool = False
    ):
        method = self.api + "/editMessageText"
        params = {
            "inline_message_id": inline_message_id,
            "text": text,
            "parse_mode": parse_mode,
            "disable_web_page_preview": disable_web_page_preview
        }
        if reply_markup: # :: Optional ::
            params["reply_markup"] = json.dumps({"inline_keyboard": reply_markup})
        return await AioHttp.get_json(method, params)

    async def editMessageCaption(
        self,
        inline_message_id: str,
        caption: str = None,
        reply_markup: list = None,
        parse_mode: str = "HTML",
    ):
        method = self.api + "/editMessageCaption"
        params = {
            "inline_message_id": inline_message_id,
            "parse_mode": parse_mode,
        }
        if caption: # :: Optional ::
            params["caption"] = caption
        if reply_markup: # :: Optional ::
            params["reply_markup"] = json.dumps({"inline_keyboard": reply_markup})
        return await AioHttp.get_json(method, params)

    async def editMessageMedia(
        self,
        inline_message_id: str,
        media: str,
        reply_markup: list = None,
    ):
        method = self.api + "/editMessageMedia"
        params = {
            "inline_message_id": inline_message_id,
            "media": media
        }
        if reply_markup: # :: Optional ::
            params["reply_markup"] = json.dumps({"inline_keyboard": reply_markup})
        return await AioHttp.get_json(method, params)

    async def editMessageReplyMarkup(
        self,
        inline_message_id: str,
        reply_markup: list = None,
    ):
        method = self.api + "/editMessageReplyMarkup"
        params = {
            "inline_message_id": inline_message_id,
        }
        if reply_markup: # :: Optional ::
            params["reply_markup"] = json.dumps({"inline_keyboard": reply_markup})
        return await AioHttp.get_json(method, params)
