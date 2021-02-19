# """
# Idea by @Pokurt
# Repo: https://github.com/pokurt/Nana-Remix/blob/master/nana/utils/aiohttp_helper.py
# """

from asyncio import TimeoutError

import ujson
from aiohttp import ClientSession, ClientTimeout
from typing import Optional
from userge.core.methods.utils.get_logger import GetLogger

LOG = GetLogger.getLogger(__name__)

# """
# Success: status == 200
# Failure: ValueError if status != 200 or timeout
# """


class AioHttp:
    @staticmethod
    async def _manage_session(
        mode: str, link: str, params: Optional[dict] = None, session: Optional[ClientSession] = None
    ):
        try:
            if session not session.closed:
                return await AioHttp._request(
                    mode=mode, session=session, link=link, params=params
                )
            async with ClientSession(json_serialize=ujson.dumps) as xsession:
                return await AioHttp._request(
                    mode=mode, session=xsession, link=link, params=params
                )
        except TimeoutError:
            LOG.warning("Timeout! the site didn't responded in time.")
        except Exception as e:
            LOG.exception(e)

    @staticmethod
    async def _request(mode: str, session: ClientSession, **kwargs):
        wait = 5 if mode == "status" else 30
        async with session.get(
            kwargs["link"], params=kwargs["params"], timeout=ClientTimeout(total=wait)
        ) as resp:
            if mode == "status":
                return resp.status
            if mode == "redirect":
                return resp.url
            if mode == "headers":
                return r.headers
            # Checking response status
            if resp.status != 200:
                return False
            if mode == "json":
                r = await resp.json()
            elif mode == "text":
                r = await resp.text()
            elif mode == "read":
                r = await resp.read()
            return r

    @staticmethod
    async def json(link: str, params: Optional[dict] = None, session: Optional[ClientSession] = None):
        res = await AioHttp._manage_session(
            mode="json", link=link, params=params, session=session
        )
        if not res:
            raise ValueError
        return res

    @staticmethod
    async def text(link: str, params: Optional[dict] = None, session: Optional[ClientSession] = None):
        res = await AioHttp._manage_session(
            mode="text", link=link, params=params, session=session
        )
        if not res:
            raise ValueError
        return res

    @staticmethod
    async def read(link: str, params: Optional[dict] = None, session: Optional[ClientSession] = None):
        res = await AioHttp._manage_session(
            mode="read", link=link, params=params, session=session
        )
        if not res:
            raise ValueError
        return res

    # Just returns the status
    @staticmethod
    async def status(link: str, session: Optional[ClientSession] = None):
        return await AioHttp._manage_session(mode="status", link=link, session=session)

    # returns redirect url
    @staticmethod
    async def redirect_url(link: str, session: Optional[ClientSession] = None):
        return await AioHttp._manage_session(
            mode="redirect", link=link, session=session
        )

    # Just returns the Header
    @staticmethod
    async def headers(link: str, session: Optional[ClientSession] = None, raw: bool = True):
        headers_ = await AioHttp._manage_session(
            mode="headers", link=link, session=session
        )
        if headers_:
            if raw:
                return headers_
            text = ""
            for key, value in headers_.items():
                text += f"🏷 <i>{key}</i>: <code>{value}</code>\n\n"
            return f"<b>URl:</b> {link}\n\n<b>HEADERS:</b>\n\n{text}"
