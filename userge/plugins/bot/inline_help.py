# Copyright (C) 2020 BY - GitHub.com/code-rgb [TG - @deleteduser420]
# All rights reserved.
"""Module that handles Inline Help"""

from userge import userge, Message, Config
from pyrogram.types import (  
     InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery)
from pyrogram import filters


if Config.BOT_TOKEN and Config.OWNER_ID:
    if Config.HU_STRING_SESSION:
        ubot = userge.bot
    else:
        ubot = userge

    HELP_BUTTONS =  [
                [InlineKeyboardButton("Secret", callback_data="help_secret"),
                InlineKeyboardButton("Alive", callback_data="help_alive"),
                InlineKeyboardButton("Opinion", callback_data="help_opinion")],

                [InlineKeyboardButton("Ofox", callback_data="help_ofox"),
                InlineKeyboardButton("Gapps", callback_data="help_gapps"),
                InlineKeyboardButton("Stylish", callback_data="help_stylish")],

                [InlineKeyboardButton("Repo", callback_data="help_repo"),
                InlineKeyboardButton("Rick", callback_data="help_rick"),
                InlineKeyboardButton("Help", callback_data="help_help")]
    ]

    BACK_BTN = InlineKeyboardButton("◀️ BACK", callback_data="help_backbtn")

    @ubot.on_message(filters.private & filters.command("inline"))
    async def inline_help(_, message: Message):
        await ubot.send_message(
            chat_id=message.chat.id,
            text="<u><b>INLINE COMMANDS</b></u>",
            reply_markup=InlineKeyboardMarkup(HELP_BUTTONS)
        )
    @ubot.on_callback_query(filters.regex(pattern=r"^help_backbtn$"))
    async def (_, c_q: CallbackQuery): 
        await c_q.edit_message_text(
            text="<u><b>INLINE COMMANDS</b></u>",
            reply_markup=InlineKeyboardMarkup(HELP_BUTTONS)
        )


    @ubot.on_callback_query(filters.regex(pattern=r"^help_secret$"))
    async def gfmnfmfft(_, c_q: CallbackQuery): 
        buttons = [[BACK_BTN, InlineKeyboardButton("📕 Example", switch_inline_query_current_chat="secret @DeletedUser420 *Random GOT spolier*")]]
        msg = "Send a secret message\n\n`secret @username [text]`"
        await c_q.edit_message_text(
                msg,
                reply_markup=InlineKeyboardMarkup(buttons)
        )
    @ubot.on_callback_query(filters.regex(pattern=r"^help_alive$"))
    async def gfmngn(_, c_q: CallbackQuery): 
        buttons = [[BACK_BTN, InlineKeyboardButton("📕 Example", switch_inline_query_current_chat="alive")]]
        msg = "Alive Command for USERGE-X"
        await c_q.edit_message_text(
                msg,
                reply_markup=InlineKeyboardMarkup(buttons)
        )
    @ubot.on_callback_query(filters.regex(pattern=r"^help_opinion$"))
    async def mfhmgtfym(_, c_q: CallbackQuery): 
        buttons = [[BACK_BTN, InlineKeyboardButton("📕 Example", switch_inline_query_current_chat="op Are Cats Cute?")]]
        msg = "Ask for opinion via inline\n\n`op Your Question`"
        await c_q.edit_message_text(
                msg,
                reply_markup=InlineKeyboardMarkup(buttons)
        )
    @ubot.on_callback_query(filters.regex(pattern=r"^help_repo$"))
    async def hgcmghmg(_, c_q: CallbackQuery): 
        buttons = [[BACK_BTN, InlineKeyboardButton("📕 Example", switch_inline_query_current_chat="repo")]]
        msg = "Your USERGE-X github repo"
        await c_q.edit_message_text(
                msg,
                reply_markup=InlineKeyboardMarkup(buttons)
        )
    @ubot.on_callback_query(filters.regex(pattern=r"^help_gapps$"))
    async def dsbsbas(_, c_q: CallbackQuery): 
        buttons = [[BACK_BTN, InlineKeyboardButton("📕 Example", switch_inline_query_current_chat="gapps")]]
        msg = "Get Lastest arm64 Gapps"
        await c_q.edit_message_text(
                msg,
                reply_markup=InlineKeyboardMarkup(buttons)
        )
    @ubot.on_callback_query(filters.regex(pattern=r"^help_ofox$"))
    async def sdvdvsv(_, c_q: CallbackQuery): 
        buttons = [[BACK_BTN, InlineKeyboardButton("📕 Example", switch_inline_query_current_chat="ofox begonia")]]
        msg = "Get Latest Ofox recovery for your device\n\n`ofox <device codename>`"
        await c_q.edit_message_text(
                msg,
                reply_markup=InlineKeyboardMarkup(buttons)
        )
    @ubot.on_callback_query(filters.regex(pattern=r"^help_rick$"))
    async def avas(_, c_q: CallbackQuery): 
        buttons = [[BACK_BTN, InlineKeyboardButton("📕 Example", switch_inline_query_current_chat="rick")]]
        msg = "Rick Roll"
        await c_q.edit_message_text(
                msg,
                reply_markup=InlineKeyboardMarkup(buttons)
        )
    @ubot.on_callback_query(filters.regex(pattern=r"^help_help$"))
    async def asca(_, c_q: CallbackQuery): 
        buttons = [[BACK_BTN, InlineKeyboardButton("📕 Example", switch_inline_query_current_chat="")]]
        msg = "Inline Plugin Help"
        await c_q.edit_message_text(
                msg,
                reply_markup=InlineKeyboardMarkup(buttons)
        )
    