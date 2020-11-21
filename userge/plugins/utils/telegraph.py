import os

from telegraph import upload_file

from userge import Config, Message, userge
from userge.utils import progress

_T_LIMIT = 5242880


@userge.on_cmd(
    "telegraph",
    about={
        "header": "Upload file to Telegra.ph's servers",
        "types": [".jpg", ".jpeg", ".png", ".gif", ".mp4"],
        "usage": "reply {tr}telegraph to supported media : limit 5MB",
    },
)
async def telegraph_(message: Message):
    replied = message.reply_to_message
    if not replied:
        await message.err("reply to supported media")
        return
    link = await upload_media_(message)
    if not link:
        return
    await message.edit(
        f"**[Here Your Telegra.ph Link!](https://telegra.ph{link})**",
        disable_web_page_preview=True,
    )


async def upload_media_(message: Message):
    replied = message.reply_to_message
    if not (
        (replied.photo and replied.photo.file_size <= _T_LIMIT)
        or (replied.animation and replied.animation.file_size <= _T_LIMIT)
        or (
            replied.video
            and replied.video.file_name.endswith((".mp4", ".mkv"))
            and replied.video.file_size <= _T_LIMIT
        )
        or (
            replied.document
            and replied.document.file_name.endswith(
                (".jpg", ".jpeg", ".png", ".gif", ".mp4", ".mkv")
            )
            and replied.document.file_size <= _T_LIMIT
        )
    ):
        await message.err("not supported!")
        return
    await message.edit("`processing...`")
    dl_loc = await message.client.download_media(
        message=message.reply_to_message,
        file_name=Config.DOWN_PATH,
        progress=progress,
        progress_args=(message, "trying to download"),
    )
    await message.edit("`uploading to telegraph...`")
    try:
        response = upload_file(dl_loc)
    except Exception as t_e:
        await message.err(t_e)
        return
    os.remove(dl_loc)
    return str(response[0])
