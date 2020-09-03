# Copyright (C) 2020  BY- 𝚂𝚢𝚗𝚝𝚊𝚡 ░ Σrr♢r (https://github.com/code-rgb) [TG- @deleteduser420]


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

if not os.path.exists('userge/xcache'):
    os.mkdir('userge/xcache')
PATH = "userge/xcache/bot_forward.txt"

if Config.BOT_TOKEN and Config.OWNER_ID:
    if Config.HU_STRING_SESSION:
        ubot = userge.bot
    else:
        ubot = userge
    
    
    @ubot.on_message(~filters.user(Config.OWNER_ID) & (filters.private & filters.incoming))
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

    
    @ubot.on_message(filters.user(Config.OWNER_ID) & filters.private & filters.reply & ~filters.regex(pattern=r"\/.+\s.+")) 
    async def forward_bot(_, message: Message):
        replied = message.reply_to_message
        to_user = replied.forward_from
        msg_id = message.message_id
        if not to_user:
            if replied.forward_sender_name:
                try:
                    data = json.load(open(PATH))
                    user_id = data[0][str(replied.message_id)]
                    await ubot.forward_messages(user_id, message.chat.id, msg_id)
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
        user_id, reason = await extract(message)     # Ban by giving ID and Reason
        if not user_id:
            await start_ban.edit("INVALID", del_in=10)
            return
        get_mem = await ubot.get_user_dict(user_id)
        firstname = get_mem['fname']
        if not reason:
            await ubot.send_message(message.chat.id, "Ban Aborted! provide a reason first!")
            return
        user_id = get_mem['id']
        if user_id == Config.OWNER_ID:
            await start_ban.edit(r"I Can't Ban You My Master")
            return
        if user_id in Config.SUDO_USERS:
            await start_ban.edit(
                "That user is in my Sudo List, Hence I can't ban him.\n\n"
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
                f"**User ID:** `{user_id}`\n**Reason:** `{reason}`"))


    @ubot.on_message(filters.user(Config.OWNER_ID) & filters.command("broadcast"))
    async def broadcast_(_, message: Message):
        replied = message.reply_to_message
        if not replied:
            await ubot.send_message(message.chat.id, "Reply to a message for BROADCAST")
            return
        b_msg = replied.message_id
        error = []
        async for c in BOT_START.find():
            try:
                await ubot.forward_messages(c['user_id'], message.chat.id, b_msg)
            except Floodwait as e:
                await asyncio.sleep(e.x)
            except BadRequest:
                failed = f"Failed for ID : {c['user_id']}"
                error.append(failed)
                
        if len(error) != 0:
            await CHANNEL.log('\n'.join(map(str, error)))
            



async def dumper(a, b, update):
    if update:
        data = json.load(open(PATH))     # load
        data[0].update({a : b})          # Update
        json.dump(data, open(PATH,'w'))  # Dump 
    else:
        data = [{a : b}]
        json.dump(data, open(PATH,'w'))

# Modified a bound method
async def extract(msg):   
    input_text = msg.matches[0].group(1)
    replied = msg.reply_to_message
    if replied:
        fwd = replied.forward_from
        if fwd:
            user_e = fwd.id
            text = input_text if input_text else None
        if replied.forward_sender_name:
            try:
                data = json.load(open(PATH))
                user_e = data[0][str(replied.message_id)]
            except:
                ubot.send(msg.chat.id, text="No Record found for user, Ban by giving ID manualy")
                return
        else:
            await ubot.send(msg.chat.id, text="Invalid")
            return
    else:
        if input_text:
            data = input_text.split(maxsplit=1)
            # Grab First Word and Process it.
            if len(data) == 2:
                user, text = data
            elif len(data) == 1:
                user = data[0]
            # if user id, convert it to integer
            if user.isdigit():
                user_e = int(user)
            elif msg.entities:
                # Extracting text mention entity and skipping if it's @ mention.
                for mention in msg.entities:
                    # Catch first text mention
                    if mention.type == "text_mention":
                        user_e = mention.user.id
                        break
            # User @ Mention.
            if user.startswith("@"):
                user_e = user
    return user_e, text


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
    