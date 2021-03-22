# Copyright (C) 2020 BY - GitHub.com/code-rgb [TG - @deleteduser420]
# All rights reserved.


import asyncio
import os

import ujson
from pyrogram import filters
from pyrogram.errors import BadRequest, FloodWait
from pyrogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup

from userge import Config, Message, userge

PATH = "userge/xcache/emoji_data.txt"
CHANNEL = userge.getCLogger(__name__)


if userge.has_bot:

    @userge.bot.on_callback_query(filters.regex(pattern=r"^op_(y|n)_(\d+)$"))
    async def choice_cb(_, c_q: CallbackQuery):
        if not os.path.exists(PATH):
            await c_q.answer("𝑶𝒑𝒊𝒏𝒊𝒐𝒏 𝒅𝒂𝒕𝒂 𝒅𝒐𝒏'𝒕 𝒆𝒙𝒊𝒔𝒕 𝒂𝒏𝒚𝒎𝒐𝒓𝒆.", show_alert=True)
            return
        opinion_id = c_q.matches[0].group(2)
        ids = c_q.from_user.id
        counter = c_q.matches[0].group(1)
        with open(PATH) as f:
            data = ujson.load(f)
        view_data = data[str(opinion_id)]
        agree_data = "👍"
        disagree_data = "👎"

        if len(view_data) == 2:
            if str(ids) in view_data[0]:
                if view_data[0][str(ids)] == "y" and counter == "y":
                    await c_q.answer("Already Voted for 👍", show_alert=True)
                    return
                if view_data[0][str(ids)] == "n" and counter == "n":
                    await c_q.answer("Already Voted for 👎", show_alert=True)
                    return
                # Answering Query First then moving forward
                choice = _choice(counter)
                await c_q.answer(f"You Choose  {choice}", show_alert=False)
                #
                if view_data[0][str(ids)] == "y" and counter == "n":
                    agree = int(view_data[1]["agree"]) - 1
                    disagree = int(view_data[1]["disagree"]) + 1
                    view_data[1] = {"agree": agree, "disagree": disagree}
                    view_data[0][str(ids)] = "n"
                if view_data[0][str(ids)] == "n" and counter == "y":
                    agree = int(view_data[1]["agree"]) + 1
                    disagree = view_data[1]["disagree"] - 1
                    view_data[1] = {"agree": agree, "disagree": disagree}
                    view_data[0][str(ids)] = "y"
            else:
                # Answering Query First then moving forward
                choice = _choice(counter)
                await c_q.answer(f"You Choose {choice}", show_alert=False)
                #
                new_id = {ids: counter}
                view_data[0].update(new_id)
                if counter == "y":
                    agree = view_data[1]["agree"] + 1
                    disagree = view_data[1]["disagree"]
                if counter == "n":
                    agree = view_data[1]["agree"]
                    disagree = view_data[1]["disagree"] + 1
                view_data[1] = {"agree": agree, "disagree": disagree}
            data[str(opinion_id)] = view_data
            with open(PATH, "w") as outfile:
                ujson.dump(data, outfile)
        else:
            if len(view_data) == 1:
                # Answering Query First then moving forward
                choice = _choice(counter)
                await c_q.answer(f"You Choose  {choice}", show_alert=False)
                if counter == "y":
                    view_data = [{ids: "y"}, {"agree": 1, "disagree": 0}]
                if counter == "n":
                    view_data = [{ids: "n"}, {"agree": 0, "disagree": 1}]
                data[str(opinion_id)] = view_data
                with open(PATH, "w") as outfile:
                    ujson.dump(data, outfile)
        agree_data += f"  {view_data[1]['agree']}"
        disagree_data += f"  {view_data[1]['disagree']}"
        opinion_data = [
            [
                InlineKeyboardButton(agree_data, callback_data=f"op_y_{opinion_id}"),
                InlineKeyboardButton(disagree_data, callback_data=f"op_n_{opinion_id}"),
            ],
            [InlineKeyboardButton("📊 Stats", callback_data=f"opresult_{opinion_id}")],
        ]
        try:
            await c_q.edit_message_reply_markup(
                reply_markup=InlineKeyboardMarkup(opinion_data)
            )
        except FloodWait as e:
            await asyncio.sleep(e.x)
        except BadRequest:
            return

    @userge.bot.on_callback_query(filters.regex(pattern=r"^opresult_(\d+)$"))
    async def choice_result_cb(_, c_q: CallbackQuery):
        u_id = c_q.from_user.id
        opinion_id = c_q.matches[0].group(1)
        if u_id in Config.OWNER_ID:
            data = ujson.load(open(PATH))
            view_data = data[str(opinion_id)]
            total = len(view_data[0])
            ag = view_data[1]["agree"]
            disag = view_data[1]["disagree"]
            agreed = round((ag / (disag + ag)) * 100)
            disagreed = round((disag / (ag + disag)) * 100)
            msg = "📊 **Final Stats**\n\n"
            msg += f"• 👤 `{total} People voted`\n\n"
            msg += f"• 👍 `{agreed}% People Agreed`\n\n"
            msg += f"• 👎 `{disagreed}% People Disagreed`\n\n"
            await c_q.edit_message_text(msg)
        else:
            a = await userge.get_me()
            if a.username:
                owner = f"Only @{a.username} Can Access This !"
            else:
                owner = f"Only {a.first_name} Can Access This !"
            await c_q.answer(owner, show_alert=True)


def _choice(res):
    return "👍" if res == "y" else "👎"


@userge.on_cmd(
    "opinion",
    about={
        "header": "Ask for Opinion via Inline Bot",
        "usage": "Reply {tr}opinion" "[INLINE] op Text",
        "examples": ["{tr}opinion", "INLINE - @[your bot name] op Are Cats Cute?"],
    },
    allow_channels=False,
    allow_via_bot=False,
    check_downpath=True,
)
async def op_(message: Message):
    replied = message.reply_to_message
    if not replied:
        await message.err("Reply to a message First")
    bot = await userge.bot.get_me()
    x = await userge.get_inline_bot_results(
        bot.username, "op <i>**Do you Agree with the replied suggestion ?**</i>"
    )
    await userge.send_inline_bot_result(
        chat_id=message.chat.id,
        query_id=x.query_id,
        result_id=x.results[0].id,
        reply_to_message_id=replied.message_id,
    )
    await message.delete()
