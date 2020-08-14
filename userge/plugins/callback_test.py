import re 
from pyrogram import (
    InlineQueryResultArticle, InputTextMessageContent,
    InlineKeyboardMarkup, InlineKeyboardButton,
    Filters, CallbackQuery, InlineQuery, InlineQueryResultPhoto)

from userge import userge, Message, Config

if Config.BOT_TOKEN and Config.OWNER_ID:
    if Config.HU_STRING_SESSION:
        ubot = userge.bot
    else:
        ubot = userge

@ubot.on_callback_query(filters=Filters.regex(pattern=r"^btn_press$"))
async def test_callback(_, callback_query: CallbackQuery):
    await callback_query.answer("Button contains: '{}'".format(callback_query.data), show_alert=True)
