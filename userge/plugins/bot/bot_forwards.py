# Copyright (C) 2020 BY - GitHub.com/code-rgb [TG - @deleteduser420]
# All rights reserved.

"""Bot Message forwarding"""

import asyncio
import os
from time import time

import ujson
from pyrogram import filters
from pyrogram.errors import (
    BadRequest,
    FloodWait,
    Forbidden,
    MessageIdInvalid,
    UserIsBlocked,
)

from userge import Config, Message, get_collection, userge
from userge.utils import mention_html, time_formatter

LOG = userge.getLogger(__name__)
CHANNEL = userge.getCLogger(__name__)
BOT_BAN = get_collection("BOT_BAN")
BOT_START = get_collection("BOT_START")
SAVED_SETTINGS = get_collection("CONFIGS")


async def _init() -> None:
    data = await SAVED_SETTINGS.find_one({"_id": "BOT_FORWARDS"})
    if data:
        Config.BOT_FORWARDS = bool(data["is_active"])


allowForwardFilter = filters.create(lambda _, __, ___: Config.BOT_FORWARDS)


@userge.on_cmd(
    "bot_fwd", about={"header": "enable / disable Bot Forwards"}, allow_channels=False
)
async def bot_fwd_(message: Message):
    """ enable / disable Bot Forwards """
    if Config.BOT_FORWARDS:
        Config.BOT_FORWARDS = False
        await message.edit("`Bot Forwards disabled !`", del_in=3, log=__name__)
    else:
        Config.BOT_FORWARDS = True
        await message.edit("`Bot Forwards enabled !`", del_in=3, log=__name__)
    await SAVED_SETTINGS.update_one(
        {"_id": "BOT_FORWARDS"},
        {"$set": {"is_active": Config.BOT_FORWARDS}},
        upsert=True,
    )


if not os.path.exists("userge/xcache"):
    os.mkdir("userge/xcache")
PATH = "userge/xcache/bot_forward.txt"


if userge.has_bot:

    @userge.bot.on_message(
        allowForwardFilter
        & ~filters.user(list(Config.OWNER_ID))
        & filters.private
        & filters.incoming
        & ~filters.command("start")
    )
    async def forward_bot(_, message: Message):
        found = await BOT_BAN.find_one({"user_id": message.from_user.id})
        if found:
            return
        msg_id = message.message_id
        try:
            msg_owner = await userge.bot.forward_messages(
                Config.OWNER_ID[0], message.chat.id, msg_id
            )
        except MessageIdInvalid:
            await CHANNEL.log(
                f"**ERROR**: can't send message to __ID__: {Config.OWNER_ID[0]}\nNote: message will be send to the first id in `OWNER_ID` only!"
            )
            return
        except UserIsBlocked:
            await CHANNEL.log("**ERROR**: You Blocked your Bot !")
            return
        update = bool(os.path.exists(PATH))
        await dumper(msg_owner.message_id, message.from_user.id, update)

    @userge.bot.on_message(
        allowForwardFilter
        & filters.user(list(Config.OWNER_ID))
        & filters.private
        & filters.reply
        & ~filters.regex(
            pattern="^(/.*|\{}(?:spoiler|cbutton)(?:$|.*))".format(Config.SUDO_TRIGGER)
        )
    )
    async def forward_reply(_, message: Message):
        replied = message.reply_to_message
        to_user = replied.forward_from
        msg_id = message.message_id
        to_copy = not message.poll
        if not to_user:
            if not replied.forward_sender_name:
                return
            try:
                with open(PATH) as f:
                    data = ujson.load(f)
                user_id = data[0][str(replied.message_id)]
                if to_copy:
                    await userge.bot.copy_message(
                        chat_id=user_id, from_chat_id=message.chat.id, message_id=msg_id
                    )
                else:
                    await userge.bot.forward_messages(
                        chat_id=user_id, from_chat_id=message.chat.id, message_id=msg_id
                    )
            except (BadRequest, Forbidden) as err:
                if "block" in str(err).lower():
                    await message.reply(
                        "**ERROR:** `You cannot reply to this user as he blocked your bot !`",
                        del_in=5,
                    )
                return
            except Exception:
                await userge.bot.send_message(
                    message.chat.id,
                    "`You can't reply to old messages with if user's"
                    "forward privacy is enabled`",
                    del_in=5,
                )
                return
        else:
            # Incase message is your own forward
            if to_user.id in Config.OWNER_ID:
                return
            if to_copy:
                await userge.bot.copy_message(
                    chat_id=to_user.id, from_chat_id=message.chat.id, message_id=msg_id
                )
            else:
                await userge.bot.forward_messages(
                    chat_id=to_user.id, from_chat_id=message.chat.id, message_id=msg_id
                )

    # Based - https://github.com/UsergeTeam/Userge/.../gban.py

    @userge.bot.on_message(
        filters.user(list(Config.OWNER_ID))
        & filters.private
        & filters.incoming
        & filters.regex(pattern=r"^\/ban(?: )(.+)")
    )
    async def bot_ban_(_, message: Message):
        """ ban a user from bot """
        start_ban = await userge.bot.send_message(message.chat.id, "`Banning...`")
        user_id, reason = extract_content(message)  # Ban by giving ID & Reason
        if not user_id:
            await start_ban.edit("User ID Not found", del_in=10)
            return
        if not reason:
            await userge.bot.send_message(
                message.chat.id, "Ban Aborted! provide a reason first!"
            )
            return
        get_mem = await userge.bot.get_users(user_id)
        firstname = get_mem.first_name
        user_id = get_mem.id
        if user_id in Config.OWNER_ID:
            await start_ban.edit(r"I Can't Ban You My Master")
            return
        if user_id in Config.SUDO_USERS:
            await start_ban.edit(
                "That user is in my Sudo List,"
                "Hence I can't ban him from bot\n"
                "\n**Tip:** Remove them from Sudo List and try again.",
                del_in=5,
            )
            return
        found = await BOT_BAN.find_one({"user_id": user_id})
        if found:
            await start_ban.edit(
                "**#Already_Banned From Bot PM**\n\n"
                "User Already Exists in My Bot BAN List.\n"
                f"**Reason For Bot BAN:** `{found['reason']}`",
                del_in=5,
            )
            return
        banned_msg = (
            "<i>**You Have been Banned Forever**" f"</i>\n**Reason** : {reason}"
        )
        await asyncio.gather(
            BOT_BAN.insert_one(
                {"firstname": firstname, "user_id": user_id, "reason": reason}
            ),
            start_ban.edit(
                r"\\**#Banned From Bot PM_User**//"
                f"\n\n**First Name:** [{firstname}](tg://user?id={user_id})\n"
                f"**User ID:** `{user_id}`\n**Reason:** `{reason}`"
            ),
            userge.bot.send_message(user_id, banned_msg),
        )

    @userge.bot.on_message(
        allowForwardFilter
        & filters.user(list(Config.OWNER_ID))
        & filters.private
        & filters.command("broadcast")
    )
    async def broadcast_(_, message: Message):
        replied = message.reply_to_message
        if not replied:
            await userge.bot.send_message(
                message.chat.id, "Reply to a message for BROADCAST"
            )
            return
        start_ = time()
        br_cast = await replied.reply("`Broadcasting ...`")
        b_msg = replied.message_id
        blocked_users = []
        count = 0
        to_copy = not replied.poll
        async for c in BOT_START.find():
            try:
                b_id = c["user_id"]
                await userge.bot.send_message(
                    b_id, "🔊 You received a **new** Broadcast."
                )
                if to_copy:
                    await userge.bot.copy_message(
                        chat_id=b_id, from_chat_id=message.chat.id, message_id=b_msg
                    )
                else:
                    await userge.bot.forward_messages(
                        chat_id=b_id, from_chat_id=message.chat.id, message_id=b_msg
                    )
                await asyncio.sleep(0.05)
                # https://github.com/aiogram/aiogram/blob/ee12911f240175d216ce33c78012994a34fe2e25/examples/broadcast_example.py#L65
            except FloodWait as e:
                await asyncio.sleep(e.x)
            except (BadRequest, Forbidden):
                blocked_users.append(
                    b_id
                )  # Collect the user id and removing them later
            except Exception as err:
                await CHANNEL.log(str(err))
            else:
                count += 1
                if count % 5 == 0:
                    try:
                        await br_cast.edit(
                            f"`Broadcasting ...`\n\n• ✔️ Success:  **{count}**\n• ✖️ Failed:  **{len(blocked_users)}**"
                        )
                    except FloodWait as e:
                        await asyncio.sleep(e.x)
        end_ = time()
        b_info = f"🔊  Successfully broadcasted message to ➜  <b>{count} users.</b>"
        if len(blocked_users) != 0:
            b_info += f"\n🚫  <b>{len(blocked_users)} users</b> blocked your bot recently, so have been removed."
        b_info += f"\n⏳  <code>Process took: {time_formatter(end_ - start_)}</code>."
        await br_cast.edit(b_info, log=__name__)
        if blocked_users:
            for buser in blocked_users:
                await BOT_START.find_one_and_delete({"user_id": buser})

    @userge.bot.on_message(
        filters.user(list(Config.OWNER_ID))
        & filters.private
        & filters.reply
        & filters.command("uinfo")
    )
    async def uinfo_(_, message: Message):
        replied = message.reply_to_message
        if not replied:
            await userge.bot.send_message(
                message.chat.id, "Reply to a message to see user info"
            )
            return
        fwd = replied.forward_from
        info_msg = await message.reply("`🔎 Searching for user in database ...`")
        usr = None
        if replied.forward_sender_name:
            try:
                with open(PATH) as f:
                    data = ujson.load(f)
                user_id = data[0].get(str(replied.message_id))
                usr = (await userge.bot.get_users(user_id)).mention
            except (BadRequest, FileNotFoundError):
                user_id = None
        elif fwd:
            usr = fwd.mention
            user_id = fwd.id
        if not (user_id and usr):
            return await message.err("Not Found", del_in=3)
        await info_msg.edit(f"<b><u>User Info</u></b>\n\n__ID__ `{user_id}`\n👤: {usr}")


async def dumper(a: int, b: int, update: bool):
    if update:
        with open(PATH) as f:
            data = ujson.load(f)
        data[0].update({a: b})  # Update
    else:
        data = [{a: b}]

    with open(PATH, "w") as outfile:
        ujson.dump(data, outfile)


def extract_content(msg: Message):  # Modified a bound method
    id_reason = msg.matches[0].group(1)
    replied = msg.reply_to_message
    user_id, reason = None, None
    if replied:
        fwd = replied.forward_from
        if fwd and id_reason:
            user_id = fwd.id
            reason = id_reason
        if replied.forward_sender_name and id_reason:
            reason = id_reason
            try:
                with open(PATH) as f:
                    data = ujson.load(f)
            except FileNotFoundError:
                pass
            else:
                user_id = data[0].get(str(replied.message_id))
    else:
        if id_reason:
            data = id_reason.split(maxsplit=1)
            # Grab First Word and Process it.
            if len(data) == 2:
                user, reason = data
            elif len(data) == 1:
                user = data[0]
            # if user id, convert it to integer
            if user.isdigit():
                user_id = int(user)
            # User @ Mention.
            if user.startswith("@"):
                user_id = user
    return user_id, reason


@userge.on_cmd(
    "bblist",
    about={
        "header": "Get a List of Bot Banned Users",
        "description": "Get Up-to-date list of users Bot Banned by you.",
        "examples": "{tr}bblist",
    },
    allow_channels=False,
)
async def list_bot_banned(message: Message):
    """ view Bot Banned users """
    msg = ""
    async for c in BOT_BAN.find():
        msg += (
            "**User** : "
            + str(c["firstname"])
            + "-> with **User ID** -> "
            + str(c["user_id"])
            + " is **Bot Banned for** : "
            + str(c["reason"])
            + "\n\n"
        )

    await message.edit_or_send_as_file(
        f"**--Bot Banned Users List--**\n\n{msg}" if msg else "`bblist empty!`"
    )


@userge.on_cmd(
    "unbban",
    about={
        "header": "Unban an User from bot",
        "description": "Removes an user from your Bot Ban List",
        "examples": "{tr}unbban [userid]",
    },
    allow_channels=False,
    allow_bots=True,
)
async def ungban_user(message: Message):
    """ unban a user from Bot's PM"""
    await message.edit("`UN-BOT Banning ...`")
    user_id = int(message.input_str)
    if not user_id:
        await message.err("user-id not found")
        return
    try:
        get_mem = await message.client.get_user_dict(user_id)
        firstname = get_mem["fname"]
        user_id = get_mem["id"]
    except:
        await message.edit("`userid Invalid`", del_in=7)
        return
    found = await BOT_BAN.find_one({"user_id": user_id})
    if not found:
        await message.err("User Not Found in My Bot Ban List")
        return
    await asyncio.gather(
        BOT_BAN.delete_one(found),
        message.edit(
            r"\\**#UnBotbanned_User**//"
            f"\n\n**First Name:** {mention_html(user_id, firstname)}"
            f"**User ID:** `{user_id}`"
        ),
    )


@userge.on_cmd(
    "bot_forwards", about={"header": "Help regarding commands for bot forwards"}
)
async def bf_help(message: Message):
    """See this For Help"""
    cmd_ = Config.CMD_TRIGGER
    bot_forwards_help = f"""
        **Available Commands**

    [Toggle]
• `{cmd_}bot_fwd` - Enable / Disable bot Forwards

    <i>works **only in** bot pm</i>
• `/ban` - Ban a User from Bot PM
    e.g-
    /ban [reply to forwarded message with reason]
    /ban [user_id/user_name] reason

• `/broadcast` - Send a Broadcast Message to Users in your `{cmd_}bot_users`
    e.g-
    /broadcast [reply to a message]

• `/uinfo` - Get user Info
    e.g-
    /uinfo [reply to forwarded message]
  
    <i>can work outside bot pm</i>
• `{cmd_}bblist` - BotBanList (Users Banned from your Bot's PM)
    e.g-
    {cmd_}bblist

• `{cmd_}unbban` - UnBotBan  (Unban Users that are in BotBanList)
    e.g-
    {cmd_}unbban [user_id/user_name]
    Hint: Check bblist for banned users.
"""
    await message.edit(bot_forwards_help, del_in=60)
