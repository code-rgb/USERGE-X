# Copyright (C) 2020 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/uaudith/Userge/blob/master/LICENSE >
#
# All rights reserved.

import aiohttp

from userge import Config, Message, logging, pool, userge

NEKOBIN_URL = "https://nekobin.com/"

_LEVELS = {
    "debug": logging.DEBUG,
    "info": logging.INFO,
    "warning": logging.WARNING,
    "error": logging.ERROR,
    "critical": logging.CRITICAL,
}


@userge.on_cmd(
    "logs",
    about={
        "header": "check USERGE-X logs",
        "flags": {
            "-d": "get logs in document",
            "-h": "get heroku logs",
            "-l": "heroku logs lines limit : default 100",
        },
    },
    allow_channels=False,
)
async def check_logs(message: Message):
    """check logs"""
    await message.edit("`checking logs ...`")
    if "-h" in message.flags and Config.HEROKU_APP:
        limit = int(message.flags.get("-l", 100))
        logs = await pool.run_in_thread(Config.HEROKU_APP.get_log)(lines=limit)
        await message.client.send_as_file(
            chat_id=message.chat.id,
            text=logs,
            filename="userge-heroku.log",
            caption=f"userge-heroku.log [ {limit} lines ]",
        )
    elif "-d" not in message.flags:
        with open("logs/userge.log", "r") as d_f:
            text = d_f.read()
        async with aiohttp.ClientSession() as ses:
            async with ses.post(
                NEKOBIN_URL + "api/documents", json={"content": text}
            ) as resp:
                if resp.status == 201:
                    response = await resp.json()
                    key = response["result"]["key"]
                    file_ext = ".txt"
                    final_url = NEKOBIN_URL + key + file_ext
                    final_url_raw = f"{NEKOBIN_URL}raw/{key}{file_ext}"
                    reply_text = "**Here Are Your Logs** :\n"
                    reply_text += (
                        f"• [NEKO]({final_url})            • [RAW]({final_url_raw})"
                    )
                    await message.edit(reply_text, disable_web_page_preview=True)
                else:
                    await message.edit("Failed to reach Nekobin !")
                    await message.client.send_document(
                        chat_id=message.chat.id,
                        document="logs/userge.log",
                        caption="**USERGE-X Logs**",
                    )
    else:
        await message.delete()
        await message.client.send_document(
            chat_id=message.chat.id,
            document="logs/userge.log",
            caption="**USERGE-X Logs**",
        )


@userge.on_cmd(
    "setlvl",
    about={
        "header": "set logger level, default to info",
        "types": ["debug", "info", "warning", "error", "critical"],
        "usage": "{tr}setlvl [level]",
        "examples": ["{tr}setlvl info", "{tr}setlvl debug"],
    },
)
async def set_level(message: Message):
    """set logger level"""
    await message.edit("`setting logger level ...`")
    level = message.input_str.lower()
    if level not in _LEVELS:
        await message.err("unknown level !")
        return
    for logger in (logging.getLogger(name) for name in logging.root.manager.loggerDict):
        logger.setLevel(_LEVELS[level])
    await message.edit(
        f"`successfully set logger level as` : **{level.upper()}**", del_in=3
    )
