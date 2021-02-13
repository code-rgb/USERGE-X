"""
Idea by @Pokurt
Repo: https://github.com/pokurt/Nana-Remix/blob/master/nana/utils/aiohttp_helper.py
"""

from aiohttp import ClientSession, ClientTimeout


class get_response:
    @staticmethod
    # Can be used without initialising
    async def json(link: str, params: dict = None):
        async with ClientSession() as session:
            async with session.get(
                link, params=params, timeout=ClientTimeout(total=30)
            ) as resp:
                if resp.status != 200:
                    raise ValueError
                # Raises an AssertionError if status != 200
                return await resp.json()

    @staticmethod
    async def text(link: str, params: dict = None):
        async with ClientSession() as session:
            async with session.get(
                link, params=params, timeout=ClientTimeout(total=30)
            ) as resp:
                if resp.status != 200:
                    raise ValueError
                return await resp.text()

    @staticmethod
    async def read(link: str, params: dict = None):
        async with ClientSession() as session:
            async with session.get(
                link, params=params, timeout=ClientTimeout(total=30)
            ) as resp:
                if resp.status != 200:
                    raise ValueError
                return await resp.read()

    # Just returns the Header
    @staticmethod
    async def status(link: str, wait: int = 5):
        async with ClientSession() as session:
            async with session.get(link, timeout=ClientTimeout(total=wait)) as resp:
                return resp.status
