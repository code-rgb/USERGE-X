"""
From Nana-Remix (https://github.com/pokurt/Nana-Remix)
Author: https://github.com/pokurt
"""

import aiohttp


class AioHttp:
    @staticmethod
    async def get_json(link):
        async with aiohttp.ClientSession() as session:
            async with session.get(link) as resp:
                return [resp.status, await resp.json()]

    @staticmethod
    async def get_text(link):
        async with aiohttp.ClientSession() as session:
            async with session.get(link) as resp:
                return [resp.status, await resp.text()]

    @staticmethod
    async def get_raw(link):
        async with aiohttp.ClientSession() as session:
            async with session.get(link) as resp:
                return [resp.status, await resp.read()]
