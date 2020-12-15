import aiohttp


class AioHttp:
    # From Nana-Remix (https://github.com/pokurt/Nana-Remix)
    @staticmethod
    async def get_json(link: str, params: dict = None):
        async with aiohttp.ClientSession() as session:
            async with session.get(link, params=params) as resp:
                data = await resp.json() if resp.status == 200 else None
            await session.close()
        return data

    @staticmethod
    async def get_text(link: str, params: dict = None):
        async with aiohttp.ClientSession() as session:
            async with session.get(link, params=params) as resp:
                data = await resp.text() if resp.status == 200 else None
            await session.close()
        return data

    @staticmethod
    async def get_raw(link: str, params: dict = None):
        async with aiohttp.ClientSession() as session:
            async with session.get(link, params=params) as resp:
                data = await resp.read() if resp.status == 200 else None
            await session.close()
        return data