# Copyright (C) 2020 BY - GitHub.com/code-rgb [TG - @deleteduser420]
# All rights reserved.


import datetime
import json
import os
from uuid import uuid1

from pyrogram import filters
from pyrogram.errors import MessageNotModified
from pyrogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup

from userge import Config, Message, userge
from userge.utils import mention_html

CHANNEL = userge.getCLogger(__name__)
PATH = "./userge/xcache/spoiler_db.json"


class Spoiler_DB:
    def __init__(self):
        if not os.path.exists(PATH):
            d = {}
            json.dump(d, open(PATH, "w"))
        self.db = json.load(open(PATH))

    def save_msg(self, rnd_id: str, msg_id: int):
        savetime = (datetime.datetime.now()).strftime("%Y-%m-%d %H:%M:%S")
        self.db[rnd_id] = {"msg_id": msg_id, "savetime": str(savetime)}
        self.save()

    def save(self):
        with open(PATH, "w") as outfile:
            json.dump(self.db, outfile, indent=4)


SPOILER_DB = Spoiler_DB()


@userge.on_cmd(
    "spoiler",
    about={
        "header": "Share a spoiler",
        "usage": "{tr}spoiler [reply to media] or Text",
    },
)
async def spoiler_alert_(message: Message):
    content = message.input_str
    reply = message.reply_to_message
    if reply and reply.text:
        content = reply.text.html
    content = "{}".format(content or "")
    if not (content or (reply and reply.media)):
        await message.err("No Content Found!")
        return
    rnd_hex = uuid1().hex
    rnd_id = f"spoiler_{rnd_hex}"
    SPOILER_DB.save_msg(rnd_hex, (await CHANNEL.store(reply, content)))
    bot_name = (await userge.bot.get_me()).username
    link = f"https://t.me/{bot_name}?start={rnd_id}"
    buttons = None
    text_ = "**{} Shared A Spoiler** !\n[> **Click To View** <]({})".format(
        mention_html(message.from_user.id, message.from_user.first_name), link
    )
    if message.client.is_bot:
        buttons = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "Button", callback_data="getl{}".format(rnd_id)
                    ),
                    InlineKeyboardButton(
                        "Text Link", callback_data="nobtnspoiler{}".format(rnd_id)
                    ),
                ],
                [
                    InlineKeyboardButton(
                        "Via Inline", switch_inline_query=rnd_id.replace("_", " ")
                    )
                ],
            ]
        )
        text_ = "<b><u>Choose How You Want to Share the Spoiler.</b></u>"
    await message.edit(text_, reply_markup=buttons, disable_web_page_preview=True)


@userge.bot.on_message(
    filters.private
    & (
        filters.regex(pattern=r"^/start spoiler_([\S]+)")
        | filters.regex(pattern=r"^/spoiler_([\S]+)")
    )
)
async def spoiler_get(_, message: Message):
    spoiler_key = message.matches[0].group(1)
    if not os.path.exists(PATH):
        await message.err("Not Found", del_in=5)
    view_data = SPOILER_DB.db
    mid = view_data.get(spoiler_key, None)
    if mid:
        return await CHANNEL.forward_stored(
            client=userge.bot,
            message_id=mid["msg_id"],
            user_id=message.from_user.id,
            chat_id=message.chat.id,
            reply_to_message_id=message.message_id,
        )
    await message.reply("Not Found / Expired")


if userge.has_bot:

    @userge.bot.on_callback_query(filters.regex(pattern=r"^getl([\S]+)$"))
    async def get_spoiler_link(_, c_q: CallbackQuery):
        u_id = c_q.from_user.id
        if u_id != Config.OWNER_ID and u_id not in Config.SUDO_USERS:
            return await c_q.answer(
                "Given That It's A Stupid-Ass Decision, I've Elected To Ignore It.",
                show_alert=True,
            )
        await c_q.answer("With Buttons", show_alert=False)
        bot_name = (await userge.bot.get_me()).username
        buttons = [
            [
                InlineKeyboardButton(
                    "View Spoiler",
                    url=f"https://t.me/{bot_name}?start={c_q.matches[0].group(1)}",
                )
            ]
        ]
        try:
            await c_q.edit_message_text(
                "<b>Click To View The Spoiler !</b>",
                reply_markup=InlineKeyboardMarkup(buttons),
            )
        except MessageNotModified:
            pass

    @userge.bot.on_callback_query(filters.regex(pattern=r"^nobtnspoiler([\S]+)$"))
    async def get_spoiler_link(_, c_q: CallbackQuery):
        u_id = c_q.from_user.id
        u_name = c_q.from_user.first_name
        if u_id != Config.OWNER_ID and u_id not in Config.SUDO_USERS:
            return await c_q.answer(
                "Given That It's A Stupid-Ass Decision, I've Elected To Ignore It.",
                show_alert=True,
            )
        bot_name = (await userge.bot.get_me()).username
        await c_q.answer("Without Buttons", show_alert=False)
        url = f"https://t.me/{bot_name}?start={c_q.matches[0].group(1)}"
        try:
            await c_q.edit_message_text(
                "**{} Shared A Spoiler** !\n[> **Click To View** <]({})".format(
                    mention_html(u_id, u_name), url
                ),
                disable_web_page_preview=True,
            )
        except MessageNotModified:
            pass
