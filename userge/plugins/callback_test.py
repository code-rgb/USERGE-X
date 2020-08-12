#name callback_test.py
import re 
from pyrogram import (
    InlineQueryResultArticle, InputTextMessageContent,
    InlineKeyboardMarkup, InlineKeyboardButton,
    Filters, CallbackQuery, InlineQuery, InlineQueryResultPhoto)
from pyrogram.errors.exceptions.bad_request_400 import MessageNotModified, MessageIdInvalid, UserIsBot, BadRequest, MessageEmpty
from userge import userge, Message, Config, get_collection

# unnecessary imports IKR

if Config.BOT_TOKEN and Config.OWNER_ID:
    if Config.HU_STRING_SESSION:
        ubot = userge.bot
    else:
        ubot = userge

# def error_call(_, CallbackQuery):
#     if re.match("notfound", CallbackQuery.data):
#         return True

# call_create = Filters.create(error_call)

@ubot.on_callback_query(filters=Filters.regex(pattern=r"^right_btn$"))
async def xyz_callback(CallbackQuery):
    await CallbackQuery.edit_message_text("processing...")
    if CallbackQuery.data == 'right_btn':
        await CallbackQuery.edit_message_text("YOU Pressed Right Button")
    elif CallbackQuery.data == 'left_btn':
        await CallbackQuery.edit_message_text("YOU Pressed Left Button")
    await CallbackQuery.answer("Tell Me if you can see this text", show_alert=True)