"""Block/Unblock Targetted User!"""

# Plugin By - XlayerCharon[XCB] X github.com/code-rgb
# TG ~>>//@CharonCB21 X //@DeletedUser420


import asyncio

from pyrogram.errors import BadRequest

from userge import Config, Message, userge
from userge.utils import mention_html

CHANNEL = userge.getCLogger(__name__)


@userge.on_cmd(
    "block",
    about={
        "header": "Blocks a User!",
        "usage": "{tr}block [ID] or [Reply To User]",
        "examples": "{tr}block @CharonCB21",
    },
)
async def block_user(message: Message):
    """Blocks a User!"""
    reply = message.reply_to_message
    if not (reply or message.input_str):
        await message.err("Reply to a user or give ID to block him/her !", del_in=5)
        return
    user_id = reply.from_user.id if reply else message.input_str
    bot_id = (await userge.bot.get_me()).id
    if user_id == bot_id or user_id in Config.OWNER_ID:
        await message.edit("Are you serious bruh? :/")
        await asyncio.sleep(2)
        await message.edit("Do you want me to block myself? :|", del_in=5)
    elif user_id in Config.SUDO_USERS:
        await message.err("Remove User From Sudo First", del_in=5)
    else:
        try:
            user = await userge.get_users(user_id)
        except BadRequest:
            await message.err("User ID is Invalid !", del_in=5)
            return
        await userge.block_user(user_id)
        blocked_msg = action_msg(user, "BLOCKED")
        await message.edit(blocked_msg, del_in=5, log=__name__)


@userge.on_cmd(
    "unblock",
    about={
        "header": "Unblocks a User!",
        "usage": "{tr}unblock [ID] or [Reply To User]",
        "examples": "{tr}unblock @CharonCB21",
    },
)
async def unblock_user(message: Message):
    """Unblocks a User!"""
    reply = message.reply_to_message
    if not (reply or message.input_str):
        await message.err("Reply to a user or give ID to unblock him/her!", del_in=5)
        return
    user_id = reply.from_user.id if reply else message.input_str
    if user_id in Config.OWNER_ID:
        await message.edit("Are you serious bruh? :/")
        await asyncio.sleep(2)
        await message.edit("How am i even supposed to unblock myself? :|", del_in=5)
    else:
        try:
            user = await userge.get_users(user_id)
        except BadRequest:
            await message.err("User ID is Invalid !", del_in=5)
            return
        await userge.unblock_user(user_id)
        unblocked_msg = action_msg(user, "UNBLOCKED")
        await message.edit(unblocked_msg, del_in=5, log=__name__)


def action_msg(user, action):
    return f"#{action}_USER\n>>  {mention_html(user.id, user.first_name)} has been <b>{action} in PM</b>."
