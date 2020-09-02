from userge import userge, Message, Config, get_collection
from pyrogram.types import (  
     InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery )
from pyrogram import filters
from pyrogram.errors.exceptions import FileIdInvalid, FileReferenceEmpty
from pyrogram.errors.exceptions.bad_request_400 import BadRequest
from datetime import date
import asyncio

started = date.today()

BOT_START = get_collection("BOT_START")

# https://github.com/UsergeTeam/Userge-Assistant/.../alive.py#L41
# refresh file id and file reference from TG server

LOGO_ID, LOGO_REF = None, None


if Config.BOT_TOKEN and Config.OWNER_ID:
    if Config.HU_STRING_SESSION:
        ubot = userge.bot
    else:
        ubot = userge


    @ubot.on_message(filters.private & filters.command("start"))
    async def start_bot(_, message: Message):
        bot = await userge.bot.get_me()
        master = await userge.get_me()
        u_id = message.from_user.id
        f_name = message.from_user.first_name
        hello = f"""
Hello [{f_name}](tg://user?id={u_id}),
Nice To Meet You! I'm **@{bot.username}**

        A Bot Powered by **USERGE-X**

<i>You Can Contact My Master</i> - **{master.first_name}**
<i>And Check The Repo For More Info.</i>
"""
        u_n = master.username
        if u_id != Config.OWNER_ID:
            found = await BOT_START.find_one({'user_id': u_id})
            if not found:
                await asyncio.gather(
                    BOT_START.insert_one(
                        {'firstname': f_name, 'user_id': u_id, 'date': started})
        try:
            if LOGO_ID:
                await sendit(message, LOGO_ID, LOGO_REF, hello, u_n)
            else:
                await refresh_id()
                await sendit(message, LOGO_ID, LOGO_REF, hello, u_n)
        except (FileIdInvalid, FileReferenceEmpty, BadRequest):
            await refresh_id()
            await sendit(message, LOGO_ID, LOGO_REF, hello, u_n)


    async def refresh_id():
        global LOGO_ID, LOGO_REF
        vid = (await ubot.get_messages('useless_x', 2)).video
        LOGO_ID = vid.file_id
        LOGO_REF = vid.file_ref


    async def sendit(message, fileid, fileref, caption, u_n):
        await ubot.send_video(
            chat_id=message.chat.id,
            video=fileid, 
            file_ref=fileref,
            caption=caption,
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("CONTACT", url=f"t.me/{u_n}"),
                InlineKeyboardButton("REPO", url="https://github.com/code-rgb/USERGE-X")],
                [InlineKeyboardButton("➕ ADD TO GROUP", callback_data="add_to_grp")
                ]]
            )
        )

    @ubot.on_callback_query(filters.regex(pattern=r"^add_to_grp$"))
    async def add_to_grp(_, callback_query: CallbackQuery): 
        u_id = callback_query.from_user.id 
        if u_id == Config.OWNER_ID:
            botname = (await ubot.get_me()).username
            msg = "**🤖 Add Your Bot to Group** \n\n <u>Note:</u>  <i>Admin Privilege Required !</i>"
            add_bot = f"http://t.me/{botname}?startgroup=start"

            buttons = [[InlineKeyboardButton("➕ PRESS TO ADD", url=add_bot)]]
            await callback_query.edit_message_text(
                    msg,
                    reply_markup=InlineKeyboardMarkup(buttons)
            )
        else:
            await callback_query.answer("ONLY MY MASTER CAN DO THAT ! \n\n Deploy Your Own USGERGE-X", show_alert=True)
 
 
            
@userge.on_cmd("bot_pm", about={
    'header': "Module That Makes your bot to respond to /start"})
async def op_(message: Message):
    text = "**Works Only in Bot's PM**\n\n"
    text += "<code>Do /start</code>"
    await message.edit(text, del_in=20)




