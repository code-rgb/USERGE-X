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
                status_ = resp.status
                data_ = await resp.json()
            await session.close()
        return status_, data_

    @staticmethod
    async def get_text(link):
        async with aiohttp.ClientSession() as session:
            async with session.get(link) as resp:
                status_ = resp.status
                data_ = await resp.text()
            await session.close()
        return status_, data_

    @staticmethod
    async def get_raw(link):
        async with aiohttp.ClientSession() as session:
            async with session.get(link) as resp:
                status_ = resp.status
                data_ = await resp.read()
            await session.close()
        return status_, data_
