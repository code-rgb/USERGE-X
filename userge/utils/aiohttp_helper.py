from userge.utils import xbot


class get_response:
    @staticmethod
    # Can be used without initialising
    async def json(link: str, params: dict = None):
        session = xbot.session
        async with session.get(link, params=params) as resp:
            assert resp.status == 200
            # Raises an AssertionError if status != 200
            return await resp.json()

    @staticmethod
    async def text(link: str, params: dict = None):
        session = xbot.session
        async with session.get(link, params=params) as resp:
            assert resp.status == 200
            return await resp.text()

    @staticmethod
    async def read(link: str, params: dict = None):
        session = xbot.session
        async with session.get(link, params=params) as resp:
            assert resp.status == 200
            return await resp.read()
