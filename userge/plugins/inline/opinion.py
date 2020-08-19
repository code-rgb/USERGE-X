from userge import userge, Message, Config
from pyrogram import (
    InlineKeyboardMarkup, InlineKeyboardButton,
    Filters, CallbackQuery)



if Config.BOT_TOKEN and Config.OWNER_ID:
    if Config.HU_STRING_SESSION:
        ubot = userge.bot
    else:
        ubot = userge
# WIP

    @ubot.on_callback_query(filters=Filters.regex(pattern=r"opinion"))
    async def choice_cb(_, callback_query: CallbackQuery):
        a = callback_query
        await ubot.edit_inline_text(callback_query.inline_message_id, a)
        # agree_data = "Yes 👍"
        # disagree_data = "Nope 👎"
        # if callback_query.data == opinion_n
            
        
        # if callback_query.data == opinion_y

        # opinion_data = [[InlineKeyboardButton(agree_data, callback_data="opinion_y"),
        #             InlineKeyboardButton(disagree_data, callback_data="opinion_n")]]
                    

        # await ubot.edit_inline_reply_markup(callback_query.inline_message_id,
        #         reply_markup=InlineKeyboardMarkup(opinion_data)
        # )
        
    
        
