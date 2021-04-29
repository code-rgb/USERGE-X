"""Plugin to manage federations"""
# Author: Copyright (C) 2020 KenHV [https://github.com/KenHV]

# For USERGE-X
# Ported to Pyrogram + Rewrite with Mongo DB
# by: (TG - @DeletedUser420) [https://github.com/code-rgb]
# Thanks @Lostb053  for writing help
import asyncio

from pyrogram import filters
from pyrogram.errors import FloodWait, Forbidden, PeerIdInvalid

from userge import Config, Message, get_collection, userge

FED_LIST = get_collection("FED_LIST")
CHANNEL = userge.getCLogger(__name__)


@userge.on_cmd(
    "addf",
    about={
        "header": "Add a chat to fed list",
        "description": "Add a chat to fed list where message is to be sent",
        "usage": "{tr}addf",
    },
    allow_bots=False,
    allow_channels=False,
    allow_private=False,
)
async def addfed_(message: Message):
    """Adds current chat to connected Feds."""
    name = message.input_str or message.chat.title
    chat_id = message.chat.id
    found = await FED_LIST.find_one({"chat_id": chat_id})
    if found:
        await message.edit(
            f"Chat __ID__: `{chat_id}`\nFed: **{found['fed_name']}**\n\nAlready exists in Fed List !",
            del_in=7,
        )
        return
    await FED_LIST.insert_one({"fed_name": name, "chat_id": chat_id})
    msg_ = f"__ID__ `{chat_id}` added to Fed: **{name}**"
    await message.edit(msg_, log=__name__, del_in=7)


@userge.on_cmd(
    "delf",
    about={
        "header": "Remove a chat from fed list",
        "flags": {"-all": "Remove all the feds from fedlist"},
        "description": "Remove a chat from fed list",
        "usage": "{tr}delf",
    },
    allow_bots=False,
    allow_channels=False,
    allow_private=False,
)
async def delfed_(message: Message):
    """Removes current chat from connected Feds."""
    if "-all" in message.flags:
        msg_ = "**Disconnected from all connected federations!**"
        await message.edit(msg_, log=__name__, del_in=7)
        await FED_LIST.drop()
    else:
        try:
            chat_ = await message.client.get_chat(message.input_str or message.chat.id)
        except (PeerIdInvalid, IndexError):
            return await message.err("Provide a valid Chat ID", del_in=7)
        chat_id = chat_.id
        out = f"{chat_.title}\nChat ID: {chat_id}\n"
        found = await FED_LIST.find_one({"chat_id": chat_id})
        if found:
            msg_ = out + f"Successfully Removed Fed: **{found['fed_name']}**"
            await message.edit(msg_, log=__name__, del_in=7)
            await FED_LIST.delete_one(found)
        else:
            return await message.err(
                out + "**Does't exist in your Fed List !**", del_in=7
            )


@userge.on_cmd(
    "fban",
    about={
        "header": "Fban user",
        "description": "Fban the user from the list of fed",
        "usage": "{tr}fban [username|reply to user|user_id] [reason (optional)]",
        "flags": {"-p": "Fban with proof"},
    },
    allow_bots=False,
    allow_channels=False,
)
async def fban_(message: Message):
    """Bans a user from connected Feds."""
    user, reason = message.extract_user_and_text
    fban_arg = ["❯", "❯❯", "❯❯❯", "❯❯❯ <b>FBanned {}</b>"]
    await message.edit(fban_arg[0])
    error_msg = "Provide a User ID or reply to a User"
    if user is None:
        return await message.err(error_msg, del_in=7)
    try:
        user_ = await message.client.get_users(user)
    except (PeerIdInvalid, IndexError):
        return await message.err(error_msg, del_in=7)
    user = user_.id
    if (
        user in Config.SUDO_USERS
        or user in Config.OWNER_ID
        or user == (await message.client.get_me()).id
    ):
        return await message.err(
            "Can't F-Ban user that exists in Sudo or Owner", del_in=7
        )
    failed = []
    total = 0
    reason = reason or "Not specified."
    reply = message.reply_to_message
    with_proof = bool("-p" in message.flags and reply)
    await message.edit(fban_arg[1])
    async for data in FED_LIST.find():
        total += 1
        chat_id = int(data["chat_id"])
        if with_proof:
            try:
                await reply.forward(chat_id)
            except Forbidden:
                # Can't send media
                pass
        try:
            async with userge.conversation(chat_id, timeout=8) as conv:
                await conv.send_message(f"/fban {user} {reason}")
                response = await conv.get_response(
                    mark_read=True,
                    filters=(filters.user([609517172]) & ~filters.service),
                )
                resp = response.text.lower()
                if not (
                    ("new fedban" in resp)
                    or ("starting a federation ban" in resp)
                    or ("start a federation ban" in resp)
                    or ("fedban reason updated" in resp)
                ):
                    failed.append(f"{data['fed_name']}  \n__ID__: `{data['chat_id']}`")
        except FloodWait as f:
            await asyncio.sleep(f.x + 3)
        except Exception:
            failed.append(data["fed_name"])
    if total == 0:
        return await message.err(
            "You Don't have any feds connected!\nsee .help addf, for more info."
        )
    await message.edit(fban_arg[2])

    if len(failed) != 0:
        status = f"Failed to fban in {len(failed)}/{total} feds.\n"
        for i in failed:
            status += "• " + i + "\n"
    else:
        status = f"Success! Fbanned in `{total}` feds."
    msg_ = (
        fban_arg[3].format(user_.mention)
        + f"\n**Reason:** {reason}\n**Status:** {status}"
    )
    if with_proof:
        proof_link = (await reply.forward(Config.LOG_CHANNEL_ID)).link
        msg_ += f"\n\n<b>[ [PROOF]({proof_link}) ]</b>"
    await message.edit(msg_, log=__name__)


@userge.on_cmd(
    "unfban",
    about={
        "header": "Unfban user",
        "description": "Unfban the user from the list of fed",
        "usage": "{tr}unfban [username|reply to user|user_id]",
    },
    allow_bots=False,
    allow_channels=False,
)
async def unfban_(message: Message):
    """Unbans a user from connected Feds."""
    user = (message.extract_user_and_text)[0]
    fban_arg = ["❯", "❯❯", "❯❯❯", "❯❯❯ <b>Un-FBanned {}</b>"]
    await message.edit(fban_arg[0])
    error_msg = "Provide a User ID or reply to a User"
    if user is None:
        return await message.err(error_msg, del_in=7)
    try:
        user_ = await message.client.get_users(user)
    except (PeerIdInvalid, IndexError):
        return await message.err(error_msg, del_in=7)
    user = user_.id
    failed = []
    total = 0
    await message.edit(fban_arg[1])
    async for data in FED_LIST.find():
        total += 1
        chat_id = int(data["chat_id"])
        try:
            async with userge.conversation(chat_id, timeout=8) as conv:
                await conv.send_message(f"/unfban {user}")
                response = await conv.get_response(
                    mark_read=True,
                    filters=(filters.user([609517172]) & ~filters.service),
                )
                resp = response.text.lower()
                if not (
                    ("new un-fedban" in resp)
                    or ("i'll give" in resp)
                    or ("un-fedban" in resp)
                ):
                    failed.append(f"{data['fed_name']}  \n__ID__: `{data['chat_id']}`")

        except BaseException:
            failed.append(data["fed_name"])
    if total == 0:
        return await message.err(
            "You Don't have any feds connected!\nsee .help addf, for more info."
        )
    await message.edit(fban_arg[2])

    if len(failed) != 0:
        status = f"Failed to un-fban in `{len(failed)}/{total}` feds.\n"
        for i in failed:
            status += "• " + i + "\n"
    else:
        status = f"Success! Un-Fbanned in `{total}` feds."
    msg_ = fban_arg[3].format(user_.mention) + f"\n**Status:** {status}"
    await message.edit(msg_, log=__name__)


@userge.on_cmd(
    "listf",
    about={
        "header": "Fed Chat List",
        "description": "Get a list of chats added in fed",
        "usage": "{tr}listf",
    },
)
async def fban_lst_(message: Message):
    """List all connected Feds."""
    out = ""
    async for data in FED_LIST.find():
        out += f"• <i>ID<b/i>: `{data['chat_id']}`\n  Fed: <b>{data['fed_name']}</b>\n"
    await message.edit_or_send_as_file(
        "**Connected federations:**\n\n" + out
        if out
        else "**You haven't connected to any federations yet!**",
        caption="Connected Fed List",
    )
