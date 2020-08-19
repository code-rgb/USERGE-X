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
        counter =  callback_query.data.split('_', 2)
        agree_data = "Yes 👍"
        disagree_data = "Nope 👎"
        opinion_y = "opinion_y_"
        opinion_n = "opinion_n_"
        if counter[1] == "y"
            add = int(counter[2]) + 1
            opinion_y += str(add)
            agree_data += f" ({add})"
        if counter[1] == "n"
            add = int(counter[2]) + 1
            opinion_n += str(add)
            disagree_data += f" ({add})"

        opinion_data = [[InlineKeyboardButton(agree_data, callback_data=opinion_y),
                     InlineKeyboardButton(disagree_data, callback_data=opinion_n)]]
                    

        await ubot.edit_inline_reply_markup(callback_query.inline_message_id,
                 reply_markup=InlineKeyboardMarkup(opinion_data)
        )
        
    
        
