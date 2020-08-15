from userge import userge, Config, get_collection
from pyrogram import Filters, CallbackQuery
SECRET_MSG = get_collection("SECRET_MSG") 

if Config.BOT_TOKEN and Config.OWNER_ID:
    if Config.HU_STRING_SESSION:
        ubot = userge.bot
    else:
        ubot = userge

@ubot.on_callback_query(filters=Filters.regex(pattern=r"^secret_btn$"))
async def alive_callback(_, callback_query: CallbackQuery):
    async for data in SECRET_MSG.find():
        user_id = int(data['user_id'])
        msg = data['msg']
    if callback_query.from_user.id == (Config.OWNER_ID or user_id):
        await callback_query.answer(msg, show_alert=True)
    else:
        await callback_query.answer("This Message is Confidential 👽", show_alert=True)
    











