# Copyright (C) 2020 BY - GitHub.com/code-rgb [TG - @deleteduser420]
# All rights reserved.
"""Module that handles Bot's Pm"""

from userge import userge, Message, Config, get_collection
from pyrogram.types import (  
     InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery )
from pyrogram import filters
from pyrogram.errors import FileIdInvalid, FileReferenceEmpty, BadRequest
from datetime import date
import asyncio


LOG = userge.getLogger("Bot_PM")
CHANNEL = userge.getCLogger("Bot_PM")

BOT_BAN = get_collection("BOT_BAN")
BOT_START = get_collection("BOT_START")
LOGO_ID, LOGO_REF = None, None
# https://github.com/UsergeTeam/Userge-Assistant/.../alive.py#L41
# refresh file id and file reference from TG server


if Config.BOT_TOKEN and Config.OWNER_ID:
    if Config.HU_STRING_SESSION:
        ubot = userge.bot
    else:
        ubot = userge


    @ubot.on_message(filters.private & filters.regex(pattern=r"^/start$"))
    async def start_bot(_, message: Message):
        bot = await userge.bot.get_me()
        master = await userge.get_me()
        u_id = message.from_user.id
        found = await BOT_BAN.find_one({'user_id': u_id})
        if found:
            return
        f_name = message.from_user.first_name
        f_username = message.from_user.username
        u_n = master.username

        hello = f"""
Hello {f_name},
Nice To Meet You! I'm **{bot.first_name}** A Bot. 

        <i><b>Powered by</i> USERGE-X</b>

<i>You Can Contact</i> My Master : **{master.first_name}**
<i>And Check The Repo For More Info.</i>
"""
        if Config.BOT_FORWARDS:          
            hello += "\n<b>NOTE : </b> "
            hello += "**Bot Forwarding is** :  ☑️ `Enabled`\n"
            hello += "<i>All your messages here will be forwared to</i> My MASTER"
        if u_id != Config.OWNER_ID:
            found = await BOT_START.find_one({'user_id': u_id})
            if not found:
                today = date.today()
                d2 = today.strftime("%B %d, %Y")
                start_date = d2.replace(',', '')
                u_n = master.username
                BOT_START.insert_one({'firstname': f_name, 'user_id': u_id, 'date': start_date})
                await asyncio.sleep(5)
                log_msg = f"A New User Started your Bot \n\n• <i>ID</i>: `{u_id}`\n   👤 : "
                log_msg += f"@{f_username}" if f_username else f_name 
                await CHANNEL.log(log_msg)
                
        try:
            if not LOGO_ID:
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
            await callback_query.answer("ONLY MY MASTER CAN DO THAT ! \n\n 𝘿𝙚𝙥𝙡𝙤𝙮 𝙮𝙤𝙪𝙧 𝙤𝙬𝙣 𝙐𝙎𝙀𝙍𝙂𝙀-𝙓 !", show_alert=True)
 
 
@userge.on_cmd("bot_users", about={
    'header': "Get a list Active Users Who started your Bot",
    'examples': "{tr}bot_users"},
    allow_channels=False)
async def bot_users(message: Message):
    """Users Who Stated Your Bot by - /start"""
    msg = ""
    async for c in BOT_START.find():  
        msg += f"• <i>ID:</i> <code>{c['user_id']}</code>\n   <b>Name:</b> {c['firstname']},  <b>Date:</b> `{c['date']}`\n"
    await message.edit_or_send_as_file(
        f"<u><i><b>Bot PM Userlist</b></i></u>\n\n{msg}" if msg else "`Nobody Does it Better`")




