"""Find Songs Fast"""
# Made by- @DeletedUser420 idea- @AnInnocentboy


from pyrogram.errors import BadRequest
from userge import Message, userge
from userge.utils import get_file_id


@userge.on_cmd(
    "smd",
    about={
        "header": "Search from already uploaded 1M Songs",
        "usage": ".smd lady gaga - poker face",
    },
)
async def song_search(message: Message):
    """get songs from channel"""
    song = message.input_str
    if not song:
        await message.err("Provide a song name or artist name to search", del_in=10)
        return
    search = await message.edit("🔍 __Searching For__ **{}**".format(song))
    chat_id = message.chat.id
    f_id = ""
    try:
        async for msg in userge.search_messages(
            -1001271479322, query=song, limit=1, filter="audio"
        ):
            f_id = get_file_id(msg)
    except BadRequest:
        await search.edit(
            "Join [THIS](https://t.me/joinchat/DdR2SUvJPBouSW4QlbJU4g) channel first"
        )
        return
    if not f_id:
        await search.edit("⚠️ Song Not Found !", del_in=5)
        return
    await userge.send_audio(chat_id, f_id)
    await search.delete()
