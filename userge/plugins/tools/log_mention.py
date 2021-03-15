# ported by @Kakashi_HTK/@ashwinstr

from pyrogram import filters
from pyrogram.errors import FloodWait
from userge import Config, Message, userge


@userge.on_message(filters.group & ~filters.bot & ~filters.me)
async def grp_log(_, message: Message):
    if not Config.PM_LOG_GROUP_ID:
        return
    me = await userge.get_me()
    id = message.message_id
    reply = message.reply_to_message
    log = f"""
#TAGS
<b>Sent by :</b> {message.from_user.mention}
<b>Group :</b> <code>{message.chat.title}</code>
<b>Message :</b> <a href={message.link}>link</a>
"""
    if reply:
        replied = reply.from_user.id
        if replied == me.id:
            try:
                await userge.send_message(
                    Config.PM_LOG_GROUP_ID, log, parse_mode="html"
                )
                await userge.forward_messages(
                    Config.PM_LOG_GROUP_ID, message.chat.id, message_ids=id
                )
            except FloodWait as e:
                await asyncio.sleep(e.x + 3)
    if ("@" + me.username) in message.text:
        try:
            await userge.send_message(
                Config.PM_LOG_GROUP_ID, log, parse_mode="html"
            )
            await userge.forward_messages(
                Config.PM_LOG_GROUP_ID, message.chat.id, message_ids=id
            )
        except FloodWait as e:
            await asyncio.sleep(e.x + 3)


@userge.on_message(~filters.group, ~filters.bot)
async def pm_log(_, message: Message):
    chat = message.chat.id
    id = message.message_id
    if not Config.PM_LOG_GROUP_ID:
        return
    u_id = message.from_user.id
    log = f"""
👤 {message.from_user.first_name} sent a new message.
<b>ID : </b><code>{u_id}</code>
"""
    if chat.id != 777000:
        global RECENT_USER
        global COUNT
        if RECENT_USER != u_id or COUNT > 4:
            RECENT_USER = u_id
            await userge.send_message(
                Config.PM_LOG_GROUP_ID,
                log,
                parse_mode="html",
            )
            COUNT = 0
            COUNT = COUNT + 1
            try:
                await userge.forward_messages(
                    Config.PM_LOG_GROUP_ID, chat, id, disable_notification=True
                )
            except FloodWait as e:
                await asyncio.sleep(e.x + 3)
        else:
            try:
                await userge.forward_messages(Config.PM_LOG_GROUP_ID, chat, id, disable_notification=True)
                await userge.send_message(
                    Config.PM_LOG_GROUP_ID,
                    f"""
<b>#Conversation</b> with:
[{chat.first_name}](tg://user?id={chat.id})
""",
                )
            except FloodWait as e:
                await asyncio.sleep(e.x + 3)
