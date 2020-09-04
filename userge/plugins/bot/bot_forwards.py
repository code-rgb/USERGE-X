# Copyright (C) 2020 BY - GitHub.com/code-rgb [TG - @deleteduser420]
# All rights reserved.

#TODO: Add Toggle

from userge import userge, Message, Config, get_collection
from pyrogram import filters
from pyrogram.errors.exceptions import MessageIdInvalid
from pyrogram.errors import FloodWait, BadRequest
import json
import os
import asyncio


LOG = userge.getLogger("Bot_Forwards")
CHANNEL = userge.getCLogger("Bot_Forwards")

BOT_BAN = get_collection("BOT_BAN")
BOT_START = get_collection("BOT_START")
SAVED_SETTINGS = get_collection("CONFIGS")


async def _init() -> None:
    data = await SAVED_SETTINGS.find_one({'_id': 'BOT_FORWARDS'})
    if data:
        Config.BOT_FORWARDS = bool(data['is_active'])

allowForwardFilter = filters.create(lambda _, __, ___: Config.BOT_FORWARDS)

@userge.on_cmd("bot_fwd", about={'header': "enable / disable Bot Forwards"}, allow_channels=False)
async def bot_fwd_(message: Message):
    """ enable / disable Bot Forwards """
    if Config.BOT_FORWARDS:
        Config.BOT_FORWARDS = False
        await message.edit("`Bot Forwards disabled !`", del_in=3)
    else:
        Config.BOT_FORWARDS = True
        await message.edit("`Bot Forwards enabled !`", del_in=3)
    await SAVED_SETTINGS.update_one(
        {'_id': 'BOT_FORWARDS'}, {"$set": {'is_active': Config.BOT_FORWARDS}}, upsert=True)


if not os.path.exists('userge/xcache'):
    os.mkdir('userge/xcache')
PATH = "userge/xcache/bot_forward.txt"

if Config.BOT_TOKEN and Config.OWNER_ID:
    if Config.HU_STRING_SESSION:
        ubot = userge.bot
    else:
        ubot = userge
    
    
    @ubot.on_message(allowForwardFilter & ~filters.user(Config.OWNER_ID) & (filters.private & filters.incoming))
    async def forward_bot(_, message: Message):
        found = await BOT_BAN.find_one({'user_id': message.from_user.id})
        if found:
            return
        else:
            msg_id = message.message_id
            try:
                msg_owner = await ubot.forward_messages(Config.OWNER_ID, message.chat.id, msg_id)
            except MessageIdInvalid:
                return
            if not os.path.exists(PATH):
                update = False
            else:
                update = True
            await dumper(msg_owner.message_id, message.from_user.id, update)

    
    @ubot.on_message(allowForwardFilter & filters.user(Config.OWNER_ID) & filters.private & filters.reply & ~filters.regex(pattern=r"\/.+")) 
    async def forward_reply(_, message: Message):
        replied = message.reply_to_message
        to_user = replied.forward_from
        msg_id = message.message_id
        if not to_user:
            if replied.forward_sender_name:
                try:
                    data = json.load(open(PATH))
                    user_id = data[0][str(replied.message_id)]
                    await ubot.forward_messages(user_id, message.chat.id, msg_id)
                except BadRequest:
                    return
                except:
                    await ubot.send_message(message.chat.id, "`You can't reply to old messages with if user's forward privacy is enabled`", del_in=10)
                    return
            else:
                return
        else:
            to_id = to_user.id
            await ubot.forward_messages(to_id, message.chat.id, msg_id)

# Based - https://github.com/UsergeTeam/Userge/.../gban.py

    @ubot.on_message(filters.user(Config.OWNER_ID) & filters.private & filters.incoming & filters.regex(pattern=r"\/ban(?: )(.+)"))
    async def bot_ban_(_, message: Message):
        """ ban a user from bot """
        start_ban = await ubot.send_message(message.chat.id, "`Banning...`")
        user_id, reason = extract_content(message)     # Ban by giving ID and Reason
        if not user_id:
            await start_ban.edit("User ID Not found", del_in=10)
            return
        if not reason:
            await ubot.send_message(message.chat.id, "Ban Aborted! provide a reason first!")
            return
        get_mem = await ubot.get_user_dict(user_id)
        firstname = get_mem['fname']
        user_id = get_mem['id']
        if user_id == Config.OWNER_ID:
            await start_ban.edit(r"I Can't Ban You My Master")
            return
        if user_id in Config.SUDO_USERS:
            await start_ban.edit(
                "That user is in my Sudo List, Hence I can't ban him from bot\n\n"
                "**Tip:** Remove them from Sudo List and try again.", del_in=5)
            return
        found = await BOT_BAN.find_one({'user_id': user_id})
        if found:
            await start_ban.edit(
                "**#Already_Banned From Bot PM**\n\nUser Already Exists in My Bot BAN List.\n"
                f"**Reason For Bot BAN:** `{found['reason']}`", del_in=5)
            return
        await asyncio.gather(
            BOT_BAN.insert_one(
                {'firstname': firstname, 'user_id': user_id, 'reason': reason}),
            await start_ban.edit(
                r"\\**#Banned From Bot PM_User**//"
                f"\n\n**First Name:** [{firstname}](tg://user?id={user_id})\n"
                f"**User ID:** `{user_id}`\n**Reason:** `{reason}`")
                
        )
        banned_msg = f"`You Have been Banned Forever`\n**Reason** : {reason}"
        await ubot.send_message(user_id, banned_msg)


    @ubot.on_message(allowForwardFilter & filters.user(Config.OWNER_ID) & filters.private & filters.command("broadcast"))
    async def broadcast_(_, message: Message):
        replied = message.reply_to_message
        if not replied:
            await ubot.send_message(message.chat.id, "Reply to a message for BROADCAST")
            return
        b_msg = replied.message_id
        error = []
        async for c in BOT_START.find():
            try:
                b_id = c['user_id']
                await ubot.send_message(b_id, "🔊 You received a **new** Broadcast.")
                await ubot.forward_messages(b_id, message.chat.id, b_msg)
            except FloodWait as e:
                await asyncio.sleep(e.x)
            except BadRequest:
                failed = f"Failed for ID : {b_id}"
                error.append(failed)
        if len(error) != 0:
            await CHANNEL.log('\n'.join(map(str, error)))
        b_info = "🔊 **Successfully Broadcasted This Message**"
        await ubot.send_message(message.chat.id, b_info)
            

async def dumper(a, b, update):
    if update:
        data = json.load(open(PATH))     # load
        data[0].update({a : b})          # Update
        json.dump(data, open(PATH,'w'))  # Dump 
    else:
        data = [{a : b}]
        json.dump(data, open(PATH,'w'))


def extract_content(msg):   # Modified a bound method
    id_reason = msg.matches[0].group(1)
    replied = msg.reply_to_message
    if replied:
        fwd = replied.forward_from
        if fwd and id_reason:
            user_id = fwd.id
            reason = id_reason
        if replied.forward_sender_name and id_reason:
            reason = id_reason
            try:
                data = json.load(open(PATH))
                user_id = data[0][str(replied.message_id)]
            except:
                user_id = None
    else:
        if id_reason:
            data = id_reason.split(maxsplit=1)
            # Grab First Word and Process it.
            if len(data) == 2:
                user, reason = data
            elif len(data) == 1:
                user = data[0]
                reason = None
            # if user id, convert it to integer
            if user.isdigit():
                user_id = int(user)
            elif msg.entities:
                # Extracting text mention entity and skipping if it's @ mention.
                for mention in msg.entities:
                    # Catch first text mention
                    if mention.type == "text_mention":
                        user_id = mention.user.id
                        break
            # User @ Mention.
            if user.startswith("@"):
                user_id = user
        else:  
            user_id = None  # just in case :p 
            reason = None
    return user_id, reason


@userge.on_cmd("bblist", about={
    'header': "Get a List of Bot Banned Users",
    'description': "Get Up-to-date list of users Bot Banned by you.",
    'examples': "{tr}bblist"},
    allow_channels=False)
async def list_bot_banned(message: Message):
    """ view Bot Banned users """
    msg = ''
    async for c in BOT_BAN.find():
        msg += ("**User** : " + str(c['firstname']) + "-> with **User ID** -> "
                + str(c['user_id']) + " is **Bot Banned for** : " + str(c['reason']) + "\n\n")
    await message.edit_or_send_as_file(
        f"**--Bot Banned Users List--**\n\n{msg}" if msg else "`bblist empty!`")


@userge.on_cmd("unbban", about={
    'header': "Unban an User from bot",
    'description': "Removes an user from your Bot Ban List",
    'examples': "{tr}unbban [userid]"},
    allow_channels=False, allow_bots=True)
async def ungban_user(message: Message):
    """ unban a user globally """
    await message.edit("`UN-BOT Banning ...`")
    user_id = int(message.input_str)
    if not user_id:
        await message.err("user-id not found")
        return
    try:
        get_mem = await message.client.get_user_dict(user_id)
        firstname = get_mem['fname']
        user_id = get_mem['id']
    except:
        await message.edit("`userid Invalid`", del_in=7)
        return
    found = await BOT_BAN.find_one({'user_id': user_id})
    if not found:
        await message.err("User Not Found in My Bot Ban List")
        return
    await asyncio.gather(
        BOT_BAN.delete_one({'firstname': firstname, 'user_id': user_id}),
        message.edit(
            r"\\**#UnBotbanned_User**//"
            f"\n\n**First Name:** [{firstname}](tg://user?id={user_id})\n"
            f"**User ID:** `{user_id}`"))
    

@userge.on_cmd("bot_forwards", about={
    'header': "Help regarding commands for bot forwards"})
async def bf_help(message: Message):
    cmd_ = Config.CMD_TRIGGER
    bot_forwards_help = f"""
        **Available Commands**

<i>works **only in** bot pm</i>
• `/ban` - Ban a User from Bot PM
e.g-
    /ban [reply to forwarded message with reason]
    /ban [user_id/user_name] reason

• `/broadcast` - Send a Broadcast Message
e.g-
    /broadcast [reply to a message]

<i>can work outside bot pm</i>
• `{cmd_}bblist` - Bot Ban List
e.g-
    {cmd_}bblist

• `{cmd_}unbban` - Un Bot Ban
e.g-
    {cmd_}unbban [user_id/user_name]
    Hint: Check bblist for banned users.

• `{cmd_}bot_fwd` - Enable / Disable bot Forwards
"""
    await userge.send_message(message.chat.id, bot_forwards_help, del_in=30)