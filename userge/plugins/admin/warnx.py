from pyrogram.errors import PeerIdInvalid
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from time import time
from userge import Config, Message, get_collection, userge

WARN_DATA = get_collection("WARN_DATA")
WARNS_DB = get_collection("WARNS_DB")


no_input_reply = (
    "I don't know who you're talking about, you're going to need to specify a user...!"
)
userid_not_valid = "can't get the user!"
user_is_admin = "Sorry! I can't warn an Admin"
owner_or_sudo = "I can't Ban My Owner and Sudo Users"


@userge.on_cmd("warn", about={"header": "Create buttons Using bot"})
async def warn_func(message: Message):
    reply = message.reply_to_message
    if not (message.input_str or reply):
        return await message.err(no_input_reply, del_in=3)

    if message.input_str:
        warn_input = message.input_str.split(None, 1)
        reason = message.input_str
        if len(warn_input) >= 1 and warn_input[0].isdigit():
            try:
                warned_user = await message.client.get_user(warn_input[0])
            except PeerIdInvalid:
                return await message.err(userid_not_valid, del_in=3)
            reason = "" if len(warn_input) == 1 else warn_input[1]
        elif len(warn_input) == 1 and reply:
            warned_user = reply.from_user
    elif reply:
        warned_user = reply.from_user
        reason = ""

    if await admin_check(message.chat, warned_user.id):
        return await message.err(user_is_admin, del_in=3)
    elif warned_user.id in Config.OWNER_ID or warned_user.id in Config.SUDO_USERS:
        return await message.err(owner_or_sudo, del_in=3)

    found = await WARN_DATA.find_one({"chat_id": message.chat.id})
    if found:
        max_warns = found["max_warns"]
        rules = "https://t.me/useless_x/22"
    else:
        max_warns = 3  # Default
        rules = ""
    ###
    by_user = message.from_user
    wcount = await WARNS_DB.count_documents(
        {"chat_id": message.chat.id, "user_id": warned_user.id}
    )
    chat_title = message.chat.title
    ###
    banned = False
    if wcount < max_warns:
        wcount += 1
    elif wcount >= max_warns:
        banned = await message.chat.kick_member(
            warned_user.id,
            until_date=int(time() + 60)
        )
        
    if banned:
        warn_text = f"Warnings has been exceeded! {warned_user.mention} has been banned!"
    else:
        warn_text = f"""
{by_user.mention} has warned {warned_user.mention} in <b>{chat_title}</b>
Reason: <code>{reason}</code>
Warns: {wcount}/{max_warns}
"""
    

    warn_id = str(
        (
            await WARNS_DB.insert_one(
                {
                    "user_id": warned_user.id,
                    "chat_id": message.chat.id,
                    "reason": str(reason),
                    "by": by_user.id,
                }
            )
        ).inserted_id
    )

    if userge.has_bot and message.client.is_bot:
        btn_row = [
            InlineKeyboardButton(
                "⚠️  Remove Warn", callback_data=f"remove_warn_{warn_id}"
            )
        ]
        if rules:
            btn_row.append(InlineKeyboardButton("📝  Rules", url=rules))

        buttons = None if banned else InlineKeyboardMarkup([btn_row])

        await message.reply(
            warn_text,
            disable_web_page_preview=True,
            reply_markup=buttons,
        )

    



@userge.on_cmd("warnmode", about={"header": "warn_mode"})
async def warn_mode(message: Message):
    warn_types = ['kick', 'ban', 'mute']
    warn_mode = message.input_str
    if not (warn_mode and warn_mode in warn_types):
        return await message.err('Not a valid warm mode', del_in=5)
    
    result = await WARN_DATA.update_one(
        {"chat_id": message.chat.id}, {"$set": {"warn_mode": warn_mode}}, upsert=True
    )
    out = "{} <b>{}</b> for Chat: {}"
    if result.upserted_id:
        out = out.format("warn_mode", "Changed", message.chat.id)
    else:
        out = out.format("warn_mode", "Updated", message.chat.id)
    await message.edit(out)


@userge.on_cmd("maxwarns", about={"header": "maxwarns"})
async def maxwarns(message: Message):
    maxwarns = message.input_str
    result = await WARN_DATA.update_one(
        {"chat_id": message.chat.id}, {"$set": {"rules": int(maxwarns)}}, upsert=True
    )
    out = "{} <b>{}</b> for Chat: {}"
    if result.upserted_id:
        out = out.format("maxwarns", "Changed", message.chat.id)
    else:
        out = out.format("maxwarns", "Updated", message.chat.id)
    await message.edit(out)


@userge.on_cmd("chatrules", about={"header": "chat rules"})
async def chat_rules(message: Message):
    rules = message.input_str
    result = await WARN_DATA.update_one(
        {"chat_id": message.chat.id}, {"$set": {"rules": rules}}, upsert=True
    )
    out = "{} <b>{}</b> for Chat: {}"
    if result.upserted_id:
        out = out.format("Rules", "Changed", message.chat.id)
    else:
        out = out.format("Rules", "Updated", message.chat.id)
    await message.edit(out)


async def admin_check(Chat, user_id: int) -> bool:
    check_status = await Chat.get_member(user_id)
    admin_strings = ["creator", "administrator"]
    return check_status.status in admin_strings
