import re

import bs4
import requests

from userge import Message, userge


@userge.on_cmd(
    "giz",
    about={
        "header": "gizoogle the text",
        "usage": "{tr}giz [text | reply to message]",
        "example": "{tr}giz Hello mate",
    },
)
async def gizoo_(message: Message):
    """gizoogle the text"""
    input_str = message.input_or_reply_str
    if not input_str:
        await message.edit("```You didn't gave the text```", del_in=3)
        return
    try:
        result = text_giz(input_str)
    except BaseException:
        return await message.err("Failed to gizoogle the text.", del_in=3)
    await message.edit(result)


def text_giz(input_text: str) -> str:
    """Taken from https://github.com/chafla/gizoogle-py/blob/master/gizoogle.py"""
    params = {"translatetext": input_text}
    target_url = "http://www.gizoogle.net/textilizer.php"
    resp = requests.post(target_url, data=params)
    # the html returned is in poor form normally.
    soup_input = re.sub(
        "/name=translatetext[^>]*>/", 'name="translatetext" >', resp.text
    )
    soup = bs4.BeautifulSoup(soup_input, "lxml")
    giz = soup.find_all(text=True)
    giz_text = giz[37].strip("\r\n")  # Hacky, but consistent.
    return giz_text
