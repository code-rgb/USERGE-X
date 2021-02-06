# Copyright (C) 2020 BY - GitHub.com/code-rgb [TG - @deleteduser420]
# All rights reserved.

import os

import ujson
from pyrogram import filters
from pyrogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup

from userge import Config, userge

if userge.has_bot:

    @userge.bot.on_callback_query(filters.regex(pattern=r"^(secret|troll)_(.*)"))
    async def alive_callback(_, c_q: CallbackQuery):
        secret_path = "userge/xcache/secret.json"
        mode = c_q.matches[0].group(1)
        key_ = c_q.matches[0].group(2)
        if not os.path.exists(secret_path):
            await c_q.answer("This message doesn't exist anymore", show_alert=True)
            return
        with open(secret_path) as f:
            s_data = ujson.load(f)
            view_data = s_data.get(key_)
        try:
            sender = await userge.get_users(int(view_data.get("sender")))
        except (BadRequest, IndexError):
            sender = await userge.get_me()
        sender_name = f"{sender.first_name} {sender.last_name or ''}".strip()
        u_id = c_q.from_user.id
        # Fit name in one line
        msg = f"🔓 𝗠𝗲𝘀𝘀𝗮𝗴𝗲 𝗳𝗿𝗼𝗺: {sender_name}"
        adjust = len(msg.encode("utf-8")) - 30
        if adjust > 0:
            msg = msg[: adjust * -1]
        msg += f'\n{view_data.get("msg")}'
        # max char. limit in callback answer
        final_l = len(msg.encode("utf-8")) - 200
        if final_l > 0:
            msg = msg[: final_l * -1]
        sender_id = sender.id
        receiver = view_data["receiver"]
        receiver_id = int(receiver["id"])
        receiver_name = receiver["name"]
        if mode == "secret":
            if u_id in Config.OWNER_ID or u_id in (sender_id, receiver_id):
                await c_q.answer(msg, show_alert=True)
            else:
                await c_q.answer("This Message is Confidential", show_alert=True)
                return
            msg_body = f"📩 <b>Secret Msg</b> for <b>{receiver_name}</b>. Only he/she can open it."
            msg_b_data = f"secret_{key_}"
        else:  # Troll
            if u_id != receiver_id:
                await c_q.answer(msg, show_alert=True)
            else:
                await c_q.answer(
                    f"Except {receiver_name}, everyone can see this message xD",
                    show_alert=True,
                )
                return
            msg_body = f"😈 <b>{receiver_name}</b> can't view this message."
            msg_b_data = f"troll_{key_}"
        # Views
        views = view_data["views"]
        v_count = len(views)
        if v_count != 0 and not (u_id in Config.OWNER_ID or u_id in views):
            view_data["views"] = views.append(u_id)
            buttons = InlineKeyboardMarkup(
                [[InlineKeyboardButton("🔐  SHOW", callback_data=msg_b_data)]]
            )
            msg_body += f"\n\n👁 **Views:** {v_count + 1}"
            await c_q.edit_message_text(
                text=msg_body, disable_web_page_preview=True, reply_markup=buttons
            )
            s_data[key_] = view_data
            with open(secret_path, "w") as r:
                ujson.dump(s_data, r, indent=4)
