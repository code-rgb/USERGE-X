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
    ):
        method = self.api + "/editMessageText"
        params = {
            "inline_message_id": inline_message_id,
            "text": text,
            "parse_mode": parse_mode,
        }
        if reply_markup:
            params["reply_markup"] = json.dumps({"inline_keyboard": reply_markup})
        return json.loads(await AioHttp.get_json(method, params))

    async def editMessageCaption(
        self,
        inline_message_id: str,
        caption: str,
        reply_markup: list = None,
        parse_mode: str = "HTML",
    ):
        method = self.api + "/editMessageCaption"
        params = {
            "inline_message_id": inline_message_id,
            "caption": caption,
            "parse_mode": parse_mode,
        }
        if reply_markup:
            params["reply_markup"] = json.dumps({"inline_keyboard": reply_markup})
        return json.loads(await AioHttp.get_json(method, params))


# TODO editMessageMedia, editMessageReplyMarkup
