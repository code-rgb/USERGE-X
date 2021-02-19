# """
# Idea by @Pokurt
# Repo: https://github.com/pokurt/Nana-Remix/blob/master/nana/utils/aiohttp_helper.py
# """

from asyncio import TimeoutError

import ujson
from aiohttp import ClientSession, ClientTimeout

# """
# Success: status == 200
# Failure: ValueError if status != 200 or timeout
# """


class AioHttp:
    @staticmethod
    async def _manage_session(
        mode: str, link: str, params: dict = None, session: ClientSession = None
    ):
        try:
            if session is not None or session.closed:
                return await AioHttp._request(
                    mode=mode, session=session, link=link, params=params
                )
            else:
                async with ClientSession(json_serialize=ujson.dumps) as session:
                    return await AioHttp._request(
                        mode=mode, session=session, link=link, params=params
                    )
        except TimeoutError:
            return

    @staticmethod
    async def _request(mode: str, session: ClientSession, **kwargs):
        wait = 5 if mode == "status" else 30
        async with session.get(
            kwargs["link"], params=kwargs["params"], timeout=ClientTimeout(total=wait)
        ) as resp:
            if mode == "status":
                return resp.status
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
    async def json(link: str, params: dict = None, session: ClientSession = None):
        res = await AioHttp._manage_session(
            mode="json", link=link, params=params, session=session
        )
        if not res:
            raise ValueError
        return res

    @staticmethod
    async def text(link: str, params: dict = None, session: ClientSession = None):
        res = await AioHttp._manage_session(
            mode="text", link=link, params=params, session=session
        )
        if not res:
            raise ValueError
        return res

    @staticmethod
    async def read(link: str, params: dict = None, session: ClientSession = None):
        res = await AioHttp._manage_session(
            mode="read", link=link, params=params, session=session
        )
        if not res:
            raise ValueError
        return res

    # Just returns the Header
    @staticmethod
    async def status(link: str, session: ClientSession = None):
        return await AioHttp._manage_session(mode="status", link=link, session=session)
