# Copyright (C) 2020 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/uaudith/Userge/blob/master/LICENSE >
#
# All rights reserved.

from pyrogram.errors.exceptions import FileIdInvalid, FileReferenceEmpty
from pyrogram.errors.exceptions.bad_request_400 import BadRequest, ChannelInvalid, MediaEmpty

from userge import userge, Message, Config, versions, get_version

LOGO_STICKER_ID, LOGO_STICKER_REF = None, None


@userge.on_cmd("alive", about={
    'header': "This command is just for fun"}, allow_channels=False)
async def alive(message: Message):
    await message.delete()
    await sendit(message)
    LicenseX = "[v3.0 GNU](https://github.com/UsergeTeam/Userge/blob/master/LICENSE)"
    if {Config.LOAD_UNOFFICIAL_PLUGINS}:
        extra_plugin = "✅ Enabled"
    else:
        extra_plugin = "❌ Disabled"
    output = f"""
**USERGE-X is Up and Running**

<u>Extra Plugins</u> : `{extra_plugin}`

• 🕔** Uptime** : `{userge.uptime}`
• 🐍** Python** : `v{versions.__python_version__}`
• 🔥** Pyrogram** : `v{versions.__pyro_version__}`
• 🧬** Userge** : `v{get_version()}`
• 🌟** Repo** : [Userge-X]({Config.UPSTREAM_REPO})
• 📑** License** : {LicenseX}

"""
    await message.client.send_message(message.chat.id, output, disable_web_page_preview=True)


async def refresh_id():

    global LOGO_STICKER_ID, LOGO_STICKER_REF  # pylint: disable=global-statement
    sticker = (await userge.get_messages("Errors_Archive", 1443)).sticker
    LOGO_STICKER_ID = sticker.file_id
    LOGO_STICKER_REF = sticker.file_ref


async def send_sticker(message):
    try:
        await message.client.send_sticker(
            message.chat.id, LOGO_STICKER_ID, file_ref=LOGO_STICKER_REF)
    except MediaEmpty:
        pass


async def sendit(message):
    if LOGO_STICKER_ID:
        try:
            await send_sticker(message)
        except (FileIdInvalid, FileReferenceEmpty, BadRequest):
            try:
                await refresh_id()
            except ChannelInvalid:
                pass
            else:
                await send_sticker(message)
    else:
        try:
            await refresh_id()
        except ChannelInvalid:
            pass
        else:
            await send_sticker(message)
