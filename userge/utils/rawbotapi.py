import json

from userge.config import Config

from .helper import AioHttp


class XBot:
    def __init__(self):
        token = getattr(Config, "BOT_TOKEN", None)
        if not token:
            return
        self.api = "https://api.telegram.org/bot" + token

    async def post_(self, method: str, params: dict):
        return await AioHttp.get_json(f"{self.api}/{method}", params)

    async def edit_inline_text(
        self,
        inline_message_id: str,
        text: str,
        reply_markup: list = None,
        parse_mode: str = "HTML",
        disable_web_page_preview: bool = False,
    ):
        params = {
            "inline_message_id": inline_message_id,
            "text": text,
            "parse_mode": parse_mode,
            "disable_web_page_preview": disable_web_page_preview,
        }
        if reply_markup:  # :: Optional ::
            params["reply_markup"] = json.dumps({"inline_keyboard": reply_markup})
        return await self.post_("editMessageText", params)

    async def edit_inline_caption(
        self,
        inline_message_id: str,
        caption: str,
        reply_markup: list = None,
        parse_mode: str = "HTML",
    ):
        params = {
            "inline_message_id": inline_message_id,
            "caption": caption,
            "parse_mode": parse_mode,
        }
        if reply_markup:  # :: Optional ::
            params["reply_markup"] = json.dumps({"inline_keyboard": reply_markup})
        return await self.post_("editMessageCaption", params)

    async def edit_inline_media(
        self,
        inline_message_id: str,
        media: str,
        reply_markup: list = None,
    ):
        params = {"inline_message_id": inline_message_id, "media": media}
        if reply_markup:  # :: Optional ::
            params["reply_markup"] = json.dumps({"inline_keyboard": reply_markup})
        return await self.post_("editMessageMedia", params)

    async def edit_inline_reply_markup(
        self,
        inline_message_id: str,
        reply_markup: list = None,
    ):
        params = {
            "inline_message_id": inline_message_id,
        }
        if reply_markup:  # :: Optional ::
            params["reply_markup"] = json.dumps({"inline_keyboard": reply_markup})
        return await self.post_("editMessageReplyMarkup", params)


class XMediaTypes:
    @staticmethod
    def InputMediaPhoto(file_id: str, caption: str = None, parse_mode: str = "HTML"):
        media = {"type": "photo", "media": file_id, "parse_mode": parse_mode}
        if caption:
            media["caption"] = caption
        return json.dumps(media)

    @staticmethod
    def InputMediaAnimation(
        file_id: str,
        thumb: str = None,
        caption: str = None,
        parse_mode: str = "HTML",
        width: int = None,
        height: int = None,
        duration: int = None,
    ):
        media = {"type": "animation", "media": file_id, "parse_mode": parse_mode}
        if caption:
            media["caption"] = caption
        if thumb:
            media["thumb"] = thumb
        if width:
            media["width"] = width
        if height:
            media["height"] = height
        if duration:
            media["duration"] = duration
        return json.dumps(media)

    @staticmethod
    def InputMediaDocument(
        file_id: str,
        thumb: str = None,
        caption: str = None,
        parse_mode: str = "HTML",
        disable_content_type_detection: bool = None,
    ):
        media = {"type": "document", "media": file_id, "parse_mode": parse_mode}
        if caption:
            media["caption"] = caption
        if thumb:
            media["thumb"] = thumb
        if isinstance(disable_content_type_detection, bool):
            media["disable_content_type_detection"] = disable_content_type_detection
        return json.dumps(media)

    @staticmethod
    def InputMediaAudio(
        file_id: str,
        thumb: str = None,
        caption: str = None,
        parse_mode: str = "HTML",
        performer: str = None,
        title: str = None,
        duration: int = None,
    ):
        media = {"type": "audio", "media": file_id, "parse_mode": parse_mode}
        if caption:
            media["caption"] = caption
        if thumb:
            media["thumb"] = thumb
        if performer:
            media["performer"] = performer
        if duration:
            media["duration"] = duration
        if title:
            media["title"] = title
        return json.dumps(media)

    @staticmethod
    def InputMediaVideo(
        file_id: str,
        thumb: str = None,
        caption: str = None,
        parse_mode: str = "HTML",
        width: int = None,
        height: int = None,
        duration: int = None,
        supports_streaming: bool = True,
    ):
        media = {
            "type": "video",
            "media": file_id,
            "parse_mode": parse_mode,
            "supports_streaming": supports_streaming,
        }
        if caption:
            media["caption"] = caption
        if thumb:
            media["thumb"] = thumb
        if width:
            media["width"] = width
        if height:
            media["height"] = height
        if duration:
            media["duration"] = duration
        return json.dumps(media)
