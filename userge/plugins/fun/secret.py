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
    sender = await userge.get_me()
    msg = f"🔓 𝗠𝗲𝘀𝘀𝗮𝗴𝗲 𝗳𝗿𝗼𝗺: {sender.first_name}"
    if sender.last_name:
        msg += f" {sender.last_name}\n"
    else:
        msg += "\n"
    async for data in SECRET_MSG.find():
        receiver = data['user_id']
        msg += data['msg']
    u_id = callback_query.from_user.id
    if u_id == Config.OWNER_ID or u_id == receiver:
        await callback_query.answer(msg, show_alert=True)
    else:
        await callback_query.answer("This Message is Confidential 👽", show_alert=True)
    











