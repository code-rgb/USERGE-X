"""Photo grabber by Noob"""

from userge import userge
from pyrogram.types import Message

@userge.on_cmd(
    "poto",
    about={
        "header": "upload the photo of replied person or chat",
        "usage": "upload the photo of replied person or chat",
        "examples": ".poto",
    },
    allow_channels=False,
)
async def photograb(message: Message):
    if message.reply_to_message and message.reply_to_message.from_users.photo:
        getid = message.reply_to_message.from_user.photo.big_file_id
        getphoto = await userge.download_media(getid)
        await userge.send_photo(message.chat.id,photo=getphoto)
        os.remove(getphoto)
    elif message.chat.photo:
        phid = message.chat.photo.big_file_id
        ppo = await userge.download_media(phid)
        await userge.send_photo(message.chat.id,photo=ppo)
        os.remove(ppo)
    else:
        await message.edit_text("Didnt Found Anything !")
