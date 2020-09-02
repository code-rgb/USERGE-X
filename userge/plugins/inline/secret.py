from userge import userge, Config, get_collection, Message
from pyrogram.types import CallbackQuery
from pyrogram import filters

SECRETS = "userge/xcache/secrets.txt"


if Config.BOT_TOKEN and Config.OWNER_ID:
    if Config.HU_STRING_SESSION:
        ubot = userge.bot
    else:
        ubot = userge

       
    @ubot.on_callback_query(filters.regex(pattern=r"^secret_btn$"))
    async def alive_callback(_, c_q: CallbackQuery): 
        if os.path.exists(SECRETS):
            view_data = json.load(open(SECRETS))
            sender = await userge.get_me()
            msg = f"🔓 𝗠𝗲𝘀𝘀𝗮𝗴𝗲 𝗳𝗿𝗼𝗺: {sender.first_name}"
            if sender.last_name:
                msg += f" {sender.last_name}\n"
            else:
                msg += "\n"
            data = view_data[c_q.inline_message_id]
            receiver =  data['user_id']
            msg += data['msg']
            u_id = c_q.from_user.id 
            if u_id == Config.OWNER_ID or u_id == receiver:
                await c_q.answer(msg, show_alert=True)
            else:
                await c_q.answer("This Message is Confidential 👽", show_alert=True)
        else:
            await c_q.answer("𝘛𝘩𝘪𝘴 𝘮𝘦𝘴𝘴𝘢𝘨𝘦 𝘥𝘰𝘦𝘴𝘯'𝘵 𝘦𝘹𝘪𝘴𝘵 𝘢𝘯𝘺𝘮𝘰𝘳𝘦.", show_alert=True)


@userge.on_cmd("secret", about={
    'header': "for help do .secret"})
async def secret_(message: Message):
    text = "**IN INLINE BOT**\n\n"
    text += "secret [username OR userid] \"Your Secret Message\""
    await message.edit(text, del_in=20)
    