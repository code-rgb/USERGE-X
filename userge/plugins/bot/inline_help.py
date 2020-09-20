# Copyright (C) 2020 BY - GitHub.com/code-rgb [TG - @deleteduser420]
# All rights reserved.
"""Module that handles Inline Help"""

from userge import userge, Message, Config
from pyrogram.types import (  
     InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery)
from pyrogram import filters


HELP_BUTTONS = None


COMMANDS = {
            "secret" : { 'help_txt' : 'Send a secret message\n\n`secret @username [text]`', 'i_q' : 'secret @DeletedUser420 This is a secret message'},
            "alive" : { 'help_txt' : 'Alive Command for USERGE-X', 'i_q' : 'alive'},
            "opinion" : { 'help_txt' : 'Ask for opinion via inline\n\n`op Your Question`', 'i_q' : 'op Are Cats Cute ?'},
            "repo" : { 'help_txt' : 'Your USERGE-X Github repo', 'i_q' : 'repo'},
            "gapps" : { 'help_txt' : 'Lastest arm64 Gapps', 'i_q' : 'gapps'},
            "ofox" : { 'help_txt' : 'Lastest Ofox Recovery\n\n`ofox <device codename>`', 'i_q' : 'ofox whyred'},
            "rick" : { 'help_txt' : 'Useless Rick Roll', 'i_q' : 'rick'},
            "help" : { 'help_txt' : 'Help For All Bot plugins', 'i_q' : ''},
            "stylish" : { 'help_txt' : 'Write it in Style\n\n`stylish [text]`', 'i_q' : 'stylish USERGE-X'}
            }


if Config.BOT_TOKEN and Config.OWNER_ID:
    if Config.HU_STRING_SESSION:
        ubot = userge.bot
    else:
        ubot = userge


    def help_btn_generator():
        btn = []
        b = []
        for cmd in list(COMMANDS.keys()):
            name = cmd.capitalize()
            call_back = f"ihelp_{cmd}"
            b.append(
               InlineKeyboardButton(name, callback_data=call_back)
            )
            if len(b) == 3:
                btn.append(b)
                b = []
        return btn
   

    if not HELP_BUTTONS:
        HELP_BUTTONS = help_btn_generator()

    BACK_BTN = InlineKeyboardButton("◀️ BACK", callback_data="backbtn_ihelp")


    @ubot.on_message(filters.private & filters.command("inline"))
    async def inline_help(_, message: Message):
        await ubot.send_message(
            chat_id=message.chat.id,
            text="<u><b>INLINE COMMANDS</b></u>",
            reply_markup=InlineKeyboardMarkup(HELP_BUTTONS)
        )


    @ubot.on_callback_query(filters.regex(pattern=r"^backbtn_ihelp$"))
    async def back_btn(_, c_q: CallbackQuery): 
        await c_q.edit_message_text(
            text="<u><b>INLINE COMMANDS</b></u>",
            reply_markup=InlineKeyboardMarkup(HELP_BUTTONS)
        )


    @ubot.on_callback_query(filters.regex(pattern=r"^ihelp_([a-zA-Z]+)$"))
    async def help_query(_, c_q: CallbackQuery): 
        command_name = c_q.matches[0].group(1)
        msg = COMMANDS[command_name]['help_txt']
        switch_i_q = COMMANDS[command_name]['i_q']
        buttons = [[BACK_BTN, InlineKeyboardButton("📕 Example", switch_inline_query_current_chat=switch_i_q)]]
        await c_q.edit_message_text(
                msg,
                reply_markup=InlineKeyboardMarkup(buttons)
        )
