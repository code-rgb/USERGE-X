import re 
from pyrogram.types import (
    InlineQueryResultArticle, InputTextMessageContent,
    InlineKeyboardMarkup, InlineKeyboardButton,
    CallbackQuery, InlineQuery, InlineQueryResultPhoto)
from pyrogram import filters

from userge import userge, Message, Config


if Config.BOT_TOKEN and Config.OWNER_ID:
    if Config.HU_STRING_SESSION:
        ubot = userge.bot
    else:
        ubot = userge


    @ubot.on_callback_query(filters.regex(pattern=r"^btn_press$"))
    async def test_callback(_, callback_query: CallbackQuery):
        await callback_query.answer("Button contains: '{}'".format(callback_query.data), show_alert=True)
