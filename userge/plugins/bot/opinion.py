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
    
    @ubot.on_callback_query(filters.regex(pattern=r"^op_(y|n)_(\d+)"))
    async def choice_cb(_, c_q: CallbackQuery):
        if not os.path.exists(PATH):
            await c_q.answer("𝑶𝒑𝒊𝒏𝒊𝒐𝒏 𝒅𝒂𝒕𝒂 𝒅𝒐𝒏'𝒕 𝒆𝒙𝒊𝒔𝒕 𝒂𝒏𝒚𝒎𝒐𝒓𝒆.", show_alert=True)
            return
        view_data = json.load(open(PATH))
        opinion_id = c_q.matches[0].group(2)
        ids = c_q.from_user.id
        counter =  c_q.matches[0].group(1)
        agree_data = "👍"
        disagree_data = "👎"
        
        if len(view_data) == 2:
            if str(ids) in view_data[0][opinion_id]:
                if view_data[0][opinion_id][str(ids)] == "y" and counter == "y":
                    await c_q.answer("Already Voted for 👍", show_alert=True)
                    return
                if view_data[0][opinion_id][str(ids)] == "n" and counter == "n":
                    await c_q.answer("Already Voted for 👎", show_alert=True)
                    return
                # Answering Query First then moving forward
                choice = _choice(counter)
                await c_q.answer(f"You Choose  {choice}", show_alert=False)
                #
                if view_data[0][opinion_id][str(ids)] == "y" and counter == "n":
                    agree = int(view_data[1]['agree']) - 1
                    disagree = int(view_data[1]['disagree']) + 1
                    view_data[1] = {"agree": agree, "disagree": disagree}
                    view_data[0][opinion_id][str(ids)] = "n"
                if view_data[0][opinion_id][str(ids)] == "n" and counter == "y":
                    agree = int(view_data[1]['agree']) + 1
                    disagree = view_data[1]['disagree'] - 1
                    view_data[1] = {"agree": agree, "disagree": disagree}
                    view_data[0][opinion_id][str(ids)] = "y"
                json.dump(view_data, open(PATH,'w'))
            else:
                # Answering Query First then moving forward
                choice = _choice(counter)
                await c_q.answer(f"You Choose {choice}", show_alert=False)
                #
                new_id = {ids : counter}
                view_data[0][opinion_id].update(new_id)
                if counter == "y":
                    agree = view_data[1]['agree'] + 1 
                    disagree = view_data[1]['disagree']
                if counter == "n":
                    agree = view_data[1]['agree'] 
                    disagree = view_data[1]['disagree'] + 1
                view_data[1] = {"agree": agree, "disagree": disagree}
                json.dump(view_data, open(PATH,'w'))
        else:
            if len(view_data) == 1:
                # Answering Query First then moving forward
                choice = _choice(counter)
                await c_q.answer(f"You Choose  {choice}", show_alert=False)
                if counter == "y":
                    view_data = [{opinion_id : {ids : "y"}}, {"agree": 1, "disagree": 0}]    #inline_id 
                if counter == "n":
                    view_data = [{opinion_id : {ids : "n"}}, {"agree": 0, "disagree": 1}]    #inline_id 
                json.dump(view_data, open(PATH,'w'))

        agree_data += f"  {view_data[1]['agree']}"  
        disagree_data += f"  {view_data[1]['disagree']}" 

        opinion_data = [[InlineKeyboardButton(agree_data, callback_data=f"op_y_{opinion_id}"),
                        InlineKeyboardButton(disagree_data, callback_data=f"op_n_{opinion_id}")],
                        [InlineKeyboardButton("📊 Stats", callback_data="e_result")]]
        try:
            await ubot.edit_inline_reply_markup(c_q.inline_message_id,
                    reply_markup=InlineKeyboardMarkup(opinion_data)
            )
        except Floodwait as e:
            await asyncio.sleep(e.x)
        except BadRequest:
            return


    @ubot.on_callback_query(filters.regex(pattern=r"^e_result$"))
    async def choice_result_cb(_, c_q: CallbackQuery):
        u_id = c_q.from_user.id 
        if u_id == Config.OWNER_ID:
            view_data = json.load(open(PATH))
            total = len(view_data[0][opinion_id])
            ag = view_data[1]['agree']
            disag = view_data[1]['disagree']
            agreed = round(( ag / (disag + ag) ) * 100)
            disagreed = round(( disag / (ag + disag) ) * 100)
            msg = "**STATS**\n\n"
            msg += f"• 👤 `{total} People voted`\n\n"
            msg += f"• 👍 `{agreed}% People Agreed`\n\n"
            msg += f"• 👎 `{disagreed}% People Disagreed`\n\n"
            
            await ubot.edit_inline_text(c_q.inline_message_id,
                    msg
            )
        else:
            a = await userge.get_me()
            if a.username:
                owner = f"Only @{a.username} Can Access This !"
            else:
                owner = f"Only {a.first_name} Can Access This !"
            await c_q.answer(owner, show_alert=True)


def _choice(res):
    if res == "y":
        choice = "👍"
    else:
        choice = "👎"
    return choice
        

@userge.on_cmd(
    "opinion", about={
        'header': "Ask for Opinion via Inline Bot",
        'usage': "Reply {tr}opinion"
                 "[INLINE] op Text",
        'examples': ["{tr}opinion", "INLINE - @[your bot name] op Are Cats Cute?"]},
    allow_channels=False, allow_via_bot=False)
async def op_(message: Message):
    replied = message.reply_to_message
    if not replied:
        await message.err("Reply to a message First")
    bot = await userge.bot.get_me()
    x = await userge.get_inline_bot_results(bot.username, "op **Do you Agree with the replied suggestion ?**")
    await userge.send_inline_bot_result(chat_id=message.chat.id,
                                            query_id=x.query_id,
                                            result_id=x.results[1].id,
                                            reply_to_message_id=replied.message_id)
    await message.delete()