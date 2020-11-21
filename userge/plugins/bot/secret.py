# Copyright (C) 2020 BY - GitHub.com/code-rgb [TG - @deleteduser420]
# All rights reserved.

import json
import os

from pyrogram import filters
from pyrogram.types import CallbackQuery

from userge import Config, userge

SECRETS = "userge/xcache/secret.txt"


if userge.has_bot:

    @userge.bot.on_callback_query(filters.regex(pattern=r"^secret_(.*)"))
    async def alive_callback(_, c_q: CallbackQuery):
        msg_id = c_q.matches[0].group(1)
        if os.path.exists(SECRETS):
            view_data = json.load(open(SECRETS))
            sender = await userge.get_me()
            msg = f"🔓 𝗠𝗲𝘀𝘀𝗮𝗴𝗲 𝗳𝗿𝗼𝗺: {sender.first_name}"
            msg += f" {sender.last_name}\n" if sender.last_name else "\n"
            data = view_data[msg_id]
            receiver = data["user_id"]
            msg += data["msg"]
            u_id = c_q.from_user.id
            if u_id in Config.OWNER_ID or u_id == receiver:
                await c_q.answer(msg, show_alert=True)
            else:
                await c_q.answer("This Message is Confidential", show_alert=True)
        else:
            await c_q.answer("This message doesn't exist anymore", show_alert=True)
