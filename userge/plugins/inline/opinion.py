# Copyright (C) 2020 BY - GitHub.com/code-rgb [TG - @deleteduser420]
# All rights reserved.


import json
from userge import userge, Message, Config
from pyrogram.errors import FloodWait, BadRequest
from pyrogram.types import (
    InlineKeyboardMarkup, InlineKeyboardButton,
    CallbackQuery)
from pyrogram import filters
import os
import asyncio

if not os.path.exists('userge/xcache'):
    os.mkdir('userge/xcache')
PATH = "userge/xcache/emoji_data.txt"   

if Config.BOT_TOKEN and Config.OWNER_ID:
    if Config.HU_STRING_SESSION:
        ubot = userge.bot
    else:
        ubot = userge
    
    @ubot.on_callback_query(filters.regex(pattern=r"opinion"))
    async def choice_cb(_, callback_query: CallbackQuery):
        ids = callback_query.from_user.id
        if not os.path.exists(PATH):
            d = []
            json.dump(d, open(PATH,'w'))
        counter =  callback_query.data.split('_', 1)
        agree_data = "👍"
        disagree_data = "👎"
        view_data = json.load(open(PATH))
        if len(view_data) == 2:
            if str(ids) in view_data[0]:
                if view_data[0][str(ids)] == "y" and counter[1] == "y":
                    await callback_query.answer("Already Voted for 👍", show_alert=True)
                    return
                if view_data[0][str(ids)] == "n" and counter[1] == "n":
                    await callback_query.answer("Already Voted for 👎", show_alert=True)
                    return
                # Answering Query First then moving forward
                choice = _choice(counter[1])
                await callback_query.answer(f"You Choose  {choice}", show_alert=False)
                #
                if view_data[0][str(ids)] == "y" and counter[1] == "n":
                    agree = int(view_data[1]['agree']) - 1
                    disagree = int(view_data[1]['disagree']) + 1
                    view_data[1] = {"agree": agree, "disagree": disagree}
                    view_data[0][str(ids)] = "n"
                if view_data[0][str(ids)] == "n" and counter[1] == "y":
                    agree = int(view_data[1]['agree']) + 1
                    disagree = view_data[1]['disagree'] - 1
                    view_data[1] = {"agree": agree, "disagree": disagree}
                    view_data[0][str(ids)] = "y"
                json.dump(view_data, open(PATH,'w'))
            else:
                # Answering Query First then moving forward
                choice = _choice(counter[1])
                await callback_query.answer(f"You Choose {choice}", show_alert=False)
                #
                new_id = {ids : counter[1]}
                view_data[0].update(new_id)
                if counter[1] == "y":
                    agree = view_data[1]['agree'] + 1 
                    disagree = view_data[1]['disagree']
                if counter[1] == "n":
                    agree = view_data[1]['agree'] 
                    disagree = view_data[1]['disagree'] + 1
                view_data[1] = {"agree": agree, "disagree": disagree}
                json.dump(view_data, open(PATH,'w'))
        else:
            if len(view_data) == 0:
                # Answering Query First then moving forward
                choice = _choice(counter[1])
                await callback_query.answer(f"You Choose  {choice}", show_alert=False)
                if counter[1] == "y":
                    view_data = [{ids : "y"},{"agree": 1, "disagree": 0}]  
                if counter[1] == "n":
                    view_data = [{ids : "n"},{"agree": 0, "disagree": 1}]
                json.dump(view_data, open(PATH,'w'))

        agree_data += f"  {view_data[1]['agree']}"  
        disagree_data += f"  {view_data[1]['disagree']}" 

        opinion_data = [[InlineKeyboardButton(agree_data, callback_data="opinion_y"),
                        InlineKeyboardButton(disagree_data, callback_data="opinion_n")],
                        [InlineKeyboardButton("📊 Stats", callback_data="e_result")]]
        try:
            await ubot.edit_inline_reply_markup(callback_query.inline_message_id,
                    reply_markup=InlineKeyboardMarkup(opinion_data)
            )
        except Floodwait as e:
            await asyncio.sleep(e.x)
        except BadRequest:
            return


    @ubot.on_callback_query(filters.regex(pattern=r"^e_result$"))
    async def choice_result_cb(_, callback_query: CallbackQuery):
        u_id = callback_query.from_user.id 
        if u_id == Config.OWNER_ID:
            view_data = json.load(open(PATH))
            total = len(view_data[0])
            ag = view_data[1]['agree']
            disag = view_data[1]['disagree']
            agreed = round(( ag / (disag + ag) ) * 100)
            disagreed = round(( disag / (ag + disag) ) * 100)
            msg = "**STATS**\n\n"
            msg += f"• 👤 `{total} People voted`\n\n"
            msg += f"• 👍 `{agreed}% People Agreed`\n\n"
            msg += f"• 👎 `{disagreed}% People Disagreed`\n\n"
            os.remove(PATH) 
            await ubot.edit_inline_text(callback_query.inline_message_id,
                    msg
            )
        else:
            a = await userge.get_me()
            if a.username:
                owner = f"Only @{a.username} Can Access This !"
            else:
                owner = f"Only {a.first_name} Can Access This !"
            await callback_query.answer(owner, show_alert=True)


def _choice(res):
    if res == "y":
        choice = "👍"
    else:
        choice = "👎"
    return choice
        

@userge.on_cmd("opinion", about={
    'header': "Ask for Opinion via Inline Bot, do .opinion to see help"})
async def op_(message: Message):
    text = "**IN INLINE BOT**\n\n"
    text += "op Are Cats Cute?"
    await message.edit(text, del_in=20)