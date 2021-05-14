""" setup gban """

import asyncio
from typing import Union

import spamwatch
from pyrogram.errors import (
    ChannelInvalid,
    ChatAdminRequired,
    PeerIdInvalid,
    UserAdminInvalid,
)
from spamwatch.types import Ban

from userge import Config, Message, filters, get_collection, pool, userge
from userge.utils import get_response, mention_html

SAVED_SETTINGS = get_collection("CONFIGS")
GBAN_USER_BASE = get_collection("GBAN_USER")
WHITELIST = get_collection("WHITELIST_USER")
CHANNEL = userge.getCLogger(__name__)
LOG = userge.getLogger(__name__)


async def _init() -> None:
    s_o = await SAVED_SETTINGS.find_one({"_id": "ANTISPAM_ENABLED"})
    i_as = await SAVED_SETTINGS.find_one({"_id": "SPAM_PROTECTION"})
    if s_o:
        Config.ANTISPAM_SENTRY = s_o["data"]
    if i_as:
        Config.SPAM_PROTECTION = s_o["data"]


@userge.on_cmd(
    "antispam",
    about={
        "header": "enable / disable antispam",
        "description": "Toggle API Auto Bans, based on Combot Cas Api",
    },
    allow_channels=False,
)
async def antispam_(message: Message):
    """enable / disable antispam"""
    if Config.ANTISPAM_SENTRY:
        Config.ANTISPAM_SENTRY = False
        await message.edit("`antispam disabled !`", del_in=3)
    else:
        Config.ANTISPAM_SENTRY = True
        await message.edit("`antispam enabled !`", del_in=3)
    await SAVED_SETTINGS.update_one(
        {"_id": "ANTISPAM_ENABLED"},
        {"$set": {"data": Config.ANTISPAM_SENTRY}},
        upsert=True,
    )


@userge.on_cmd(
    "spamprotection",
    about={
        "header": "enable / disable Intellivoid spam protection",
        "description": "Toggle API Auto Bans, based on Intellivoid spam protection api",
    },
    allow_channels=False,
)
async def spam_protect_(message: Message):
    """enable / disable Intellivoid spam protection"""
    if Config.SPAM_PROTECTION:
        Config.SPAM_PROTECTION = False
        await message.edit("`Intellivoid Spam Protection disabled !`", del_in=3)
    else:
        Config.SPAM_PROTECTION = True
        await message.edit("`Intellivoid Spam Protection enabled !`", del_in=3)
    await SAVED_SETTINGS.update_one(
        {"_id": "SPAM_PROTECTION"},
        {"$set": {"data": Config.SPAM_PROTECTION}},
        upsert=True,
    )


@userge.on_cmd(
    "gban",
    about={
        "header": "Globally Ban A User",
        "description": "Adds User to your GBan List. "
        "Bans a Globally Banned user if they join or message. "
        "[NOTE: Works only in groups where you are admin.]",
        "examples": "{tr}gban [userid | reply] [reason for gban] (mandatory)",
    },
    allow_channels=False,
    allow_bots=False,
)
async def gban_user(message: Message):
    """ban a user globally"""
    await message.edit("`GBanning...`")
    user_id, reason = message.extract_user_and_text
    if not user_id:
        await message.edit(
            "`no valid user_id or message specified,`"
            "`don't do .help gban for more info. "
            "Coz no one's gonna help ya`(｡ŏ_ŏ) ⚠",
            del_in=0,
        )
        return
    get_mem = await message.client.get_user_dict(user_id)
    firstname = get_mem["fname"]
    if not reason:
        await message.edit(
            f"**#Aborted**\n\n**Gbanning** of {mention_html(user_id, firstname)} "
            "Aborted coz No reason of gban provided by banner",
            del_in=5,
        )
        return
    user_id = get_mem["id"]
    if user_id == (await message.client.get_me()).id:
        await message.edit(r"LoL. Why would I GBan myself ¯\(°_o)/¯")
        return
    if user_id in Config.SUDO_USERS:
        await message.edit(
            "That user is in my Sudo List, Hence I can't ban him.\n\n"
            "**Tip:** Remove them from Sudo List and try again. (¬_¬)",
            del_in=5,
        )
        return
    found = await GBAN_USER_BASE.find_one({"user_id": user_id})
    if found:
        await message.edit(
            "**#Already_GBanned**\n\nUser Already Exists in My Gban List.\n"
            f"**Reason For GBan:** `{found['reason']}`",
            del_in=5,
        )
        return
    await message.edit(
        r"\\**#GBanned_User**//"
        f"\n\n**First Name:** {mention_html(user_id, firstname)}\n"
        f"**User ID:** `{user_id}`\n**Reason:** `{reason}`"
    )
    # TODO: can we add something like "GBanned by {any_sudo_user_fname}"
    if message.client.is_bot:
        chats = [message.chat]
    else:
        chats = await message.client.get_common_chats(user_id)
    gbanned_chats = []
    for chat in chats:
        try:
            await chat.kick_member(user_id)
            gbanned_chats.append(chat.id)
            await CHANNEL.log(
                r"\\**#Antispam_Log**//"
                f"\n**User:** {mention_html(user_id, firstname)}\n"
                f"**User ID:** `{user_id}`\n"
                f"**Chat:** {chat.title}\n"
                f"**Chat ID:** `{chat.id}`\n"
                f"**Reason:** `{reason}`\n\n$GBAN #id{user_id}"
            )
        except (ChatAdminRequired, UserAdminInvalid, ChannelInvalid):
            pass
    await GBAN_USER_BASE.insert_one(
        {
            "firstname": firstname,
            "user_id": user_id,
            "reason": reason,
            "chat_ids": gbanned_chats,
        }
    )
    if message.reply_to_message:
        await CHANNEL.fwd_msg(message.reply_to_message)
        await CHANNEL.log(f"$GBAN #prid{user_id} ⬆️")
    LOG.info("G-Banned %s", str(user_id))


@userge.on_cmd(
    "ungban",
    about={
        "header": "Globally Unban an User",
        "description": "Removes an user from your Gban List",
        "examples": "{tr}ungban [userid | reply]",
    },
    allow_channels=False,
    allow_bots=False,
)
async def ungban_user(message: Message):
    """unban a user globally"""
    await message.edit("`UnGBanning...`")
    user_id, _ = message.extract_user_and_text
    if not user_id:
        await message.err("user-id not found")
        return
    try:
        get_mem = await message.client.get_user_dict(user_id)
    except PeerIdInvalid:
        await GBAN_USER_BASE.find_one_and_delete({"user_id": user_id})
        deleted_user_ = f"\nRemoved [Deleted Account !](tg://openmessage?user_id={user_id}) Successfully"
        return await message.edit(
            r"\\**#UnGbanned_User**//" + "\n" + deleted_user_, log=__name__
        )
    firstname = get_mem["fname"]
    user_id = get_mem["id"]
    found = await GBAN_USER_BASE.find_one_and_delete({"user_id": user_id})
    if not found:
        await message.err("User Not Found in My Gban List")
        return
    if "chat_ids" in found:
        for chat_id in found["chat_ids"]:
            try:
                await userge.unban_chat_member(chat_id, user_id)
                await CHANNEL.log(
                    r"\\**#Antispam_Log**//"
                    f"\n**User:** {mention_html(user_id, firstname)}\n"
                    f"**User ID:** `{user_id}`\n\n"
                    f"$UNGBAN #id{user_id}"
                )
            except (ChatAdminRequired, UserAdminInvalid, ChannelInvalid):
                pass
    await message.edit(
        r"\\**#UnGbanned_User**//"
        f"\n\n**First Name:** {mention_html(user_id, firstname)}\n"
        f"**User ID:** `{user_id}`"
    )
    LOG.info("UnGbanned %s", str(user_id))


@userge.on_cmd(
    "glist",
    about={
        "header": "Get a List of Gbanned Users",
        "description": "Get Up-to-date list of users Gbanned by you.",
        "examples": "Lol. Just type {tr}glist",
    },
    allow_channels=False,
)
async def list_gbanned(message: Message):
    """vies gbanned users"""
    msg = ""
    bad_users = ""
    async for c in GBAN_USER_BASE.find():
        try:
            msg += (
                "**User** : "
                + str(c["firstname"])
                + "-> with **User ID** -> "
                + str(c["user_id"])
                + " is **GBanned for** : "
                + str(c["reason"])
                + "\n\n"
            )
        except KeyError:
            await GBAN_USER_BASE.delete_one(c)
            bad_users += (
                "**User** : "
                + str(c["firstname"])
                + "-> with **User ID** -> "
                + str(c["user_id"])
            )

    await message.edit_or_send_as_file(
        f"**--Globally Banned Users List--**\n\n{msg}" if msg else "`glist empty!`"
    )
    if bad_users:
        await CHANNEL.log(
            "**These users are removed from gban list due to some errors in gban reason!"
            " you can ban them again manually**\n" + bad_users
        )


@userge.on_cmd(
    "whitelist",
    about={
        "header": "Whitelist a User",
        "description": "Use whitelist to add users to bypass API Bans",
        "useage": "{tr}whitelist [userid | reply to user]",
        "examples": "{tr}whitelist 5231147869",
    },
    allow_channels=False,
    allow_bots=False,
)
async def whitelist(message: Message):
    """add user to whitelist"""
    user_id, _ = message.extract_user_and_text
    if not user_id:
        await message.err("user-id not found")
        return
    get_mem = await message.client.get_user_dict(user_id)
    firstname = get_mem["fname"]
    user_id = get_mem["id"]
    found = await WHITELIST.find_one({"user_id": user_id})
    if found:
        await message.err("User Already in My WhiteList")
        return
    await asyncio.gather(
        WHITELIST.insert_one({"firstname": firstname, "user_id": user_id}),
        message.edit(
            r"\\**#Whitelisted_User**//"
            f"\n\n**First Name:** {mention_html(user_id, firstname)}\n"
            f"**User ID:** `{user_id}`"
        ),
        CHANNEL.log(
            r"\\**#Antispam_Log**//"
            f"\n**User:** {mention_html(user_id, firstname)}\n"
            f"**User ID:** `{user_id}`\n"
            f"**Chat:** {message.chat.title}\n"
            f"**Chat ID:** `{message.chat.id}`\n\n$WHITELISTED #id{user_id}"
        ),
    )
    LOG.info("WhiteListed %s", str(user_id))


@userge.on_cmd(
    "rmwhite",
    about={
        "header": "Removes a User from Whitelist",
        "description": "Use it to remove users from WhiteList",
        "useage": "{tr}rmwhite [userid | reply to user]",
        "examples": "{tr}rmwhite 5231147869",
    },
    allow_channels=False,
    allow_bots=False,
)
async def rmwhitelist(message: Message):
    """remove a user from whitelist"""
    user_id, _ = message.extract_user_and_text
    if not user_id:
        await message.err("user-id not found")
        return
    get_mem = await message.client.get_user_dict(user_id)
    firstname = get_mem["fname"]
    user_id = get_mem["id"]
    found = await WHITELIST.find_one({"user_id": user_id})
    if not found:
        await message.err("User Not Found in My WhiteList")
        return
    await asyncio.gather(
        WHITELIST.delete_one({"firstname": firstname, "user_id": user_id}),
        message.edit(
            r"\\**#Removed_Whitelisted_User**//"
            f"\n\n**First Name:** {mention_html(user_id, firstname)}\n"
            f"**User ID:** `{user_id}`"
        ),
        CHANNEL.log(
            r"\\**#Antispam_Log**//"
            f"\n**User:** {mention_html(user_id, firstname)}\n"
            f"**User ID:** `{user_id}`\n"
            f"**Chat:** {message.chat.title}\n"
            f"**Chat ID:** `{message.chat.id}`\n\n$RMWHITELISTED #id{user_id}"
        ),
    )
    LOG.info("WhiteListed %s", str(user_id))


@userge.on_cmd(
    "listwhite",
    about={
        "header": "Get a List of Whitelisted Users",
        "description": "Get Up-to-date list of users WhiteListed by you.",
        "examples": "Lol. Just type {tr}listwhite",
    },
    allow_channels=False,
)
async def list_white(message: Message):
    """list whitelist"""
    msg = ""
    async for c in WHITELIST.find():
        msg += (
            "**User** : "
            + str(c["firstname"])
            + "-> with **User ID** -> "
            + str(c["user_id"])
            + "\n\n"
        )

    await message.edit_or_send_as_file(
        f"**--Whitelisted Users List--**\n\n{msg}" if msg else "`whitelist empty!`"
    )


@userge.on_filters(
    filters.group & filters.new_chat_members, group=1, check_restrict_perm=True
)
async def gban_at_entry(message: Message):
    """handle gbans"""
    chat_id = message.chat.id
    for user in message.new_chat_members:
        user_id = user.id
        firstname = user.first_name
        if await WHITELIST.find_one({"user_id": user_id}):
            continue
        gbanned = await GBAN_USER_BASE.find_one({"user_id": user_id})
        if gbanned:
            if "chat_ids" in gbanned:
                chat_ids = gbanned["chat_ids"]
                chat_ids.append(chat_id)
            else:
                chat_ids = [chat_id]
            await asyncio.gather(
                message.client.kick_chat_member(chat_id, user_id),
                message.reply(
                    r"\\**#𝑿_Antispam**//"
                    "\n\nGlobally Banned User Detected in this Chat.\n\n"
                    f"**User:** {mention_html(user_id, firstname)}\n"
                    f"**ID:** `{user_id}`\n**Reason:** `{gbanned['reason']}`\n\n"
                    "**Quick Action:** Banned",
                    del_in=10,
                ),
                CHANNEL.log(
                    r"\\**#Antispam_Log**//"
                    "\n\n**GBanned User $SPOTTED**\n"
                    f"**User:** {mention_html(user_id, firstname)}\n"
                    f"**ID:** `{user_id}`\n**Reason:** {gbanned['reason']}\n**Quick Action:** "
                    f"Banned in {message.chat.title}"
                ),
                GBAN_USER_BASE.update_one(
                    {"user_id": user_id, "firstname": firstname},
                    {"$set": {"chat_ids": chat_ids}},
                    upsert=True,
                ),
            )
        elif Config.ANTISPAM_SENTRY:
            try:
                res = await get_response.json(
                    f"https://api.cas.chat/check?user_id={user_id}"
                )
            except ValueError:  # api down
                pass
            else:
                if res and (res["ok"]):
                    reason = (
                        " | ".join(res["result"]["messages"])
                        if "result" in res
                        else None
                    )
                    await asyncio.gather(
                        message.client.kick_chat_member(chat_id, user_id),
                        message.reply(
                            r"\\**#𝑿_Antispam**//"
                            "\n\nGlobally Banned User Detected in this Chat.\n\n"
                            "**$SENTRY CAS Federation Ban**\n"
                            f"**User:** {mention_html(user_id, firstname)}\n"
                            f"**ID:** `{user_id}`\n**Reason:** `{reason}`\n\n"
                            "**Quick Action:** Banned",
                            del_in=10,
                        ),
                        CHANNEL.log(
                            r"\\**#Antispam_Log**//"
                            "\n\n**GBanned User $SPOTTED**\n"
                            "**$SENRTY #CAS BAN**"
                            f"\n**User:** {mention_html(user_id, firstname)}\n"
                            f"**ID:** `{user_id}`\n**Reason:** `{reason}`\n**Quick Action:**"
                            f" Banned in {message.chat.title}\n\n$AUTOBAN #id{user_id}"
                        ),
                    )
        elif Config.SPAM_PROTECTION:
            try:
                iv = await get_response.json(
                    "https://api.intellivoid.net/spamprotection/v1/lookup?query="
                    + str(user_id)
                )
            except ValueError:
                pass
            else:
                if iv and (
                    iv["success"]
                    and iv["results"]["attributes"]["is_blacklisted"] is True
                ):
                    reason = iv["results"]["attributes"]["blacklist_reason"]
                    await asyncio.gather(
                        message.client.kick_chat_member(chat_id, user_id),
                        message.reply(
                            r"\\**#𝑿_Antispam**//"
                            "\n\nGlobally Banned User Detected in this Chat.\n\n"
                            "**$Intellivoid Spam Protection**"
                            f"\n**User:** {mention_html(user_id, firstname)}\n"
                            f"**ID:** `{user_id}`\n**Reason:** `{reason}`\n\n"
                            "**Quick Action:** Banned",
                            del_in=10,
                        ),
                        CHANNEL.log(
                            r"\\**#Antispam_Log**//"
                            "\n\n**GBanned User $SPOTTED**\n"
                            "**$Intellivoid Spam Protection**"
                            f"\n**User:** {mention_html(user_id, firstname)}\n"
                            f"**ID:** `{user_id}`\n**Reason:** `{reason}`\n**Quick Action:**"
                            f" Banned in {message.chat.title}\n\n$AUTOBAN #id{user_id}"
                        ),
                    )
        elif Config.SPAM_WATCH_API:
            try:
                intruder = await _get_spamwatch_data(user_id)
            except spamwatch.errors.Error as err:
                LOG.error(str(err))
            else:
                if intruder:
                    await asyncio.gather(
                        message.client.kick_chat_member(chat_id, user_id),
                        message.reply(
                            r"\\**#𝑿_Antispam**//"
                            "\n\nGlobally Banned User Detected in this Chat.\n\n"
                            "**$SENTRY SpamWatch Federation Ban**\n"
                            f"**User:** {mention_html(user_id, firstname)}\n"
                            f"**ID:** `{user_id}`\n**Reason:** `{intruder.reason}`\n\n"
                            "**Quick Action:** Banned",
                            del_in=10,
                        ),
                        CHANNEL.log(
                            r"\\**#Antispam_Log**//"
                            "\n\n**GBanned User $SPOTTED**\n"
                            "**$SENRTY #SPAMWATCH_API BAN**"
                            f"\n**User:** {mention_html(user_id, firstname)}\n"
                            f"**ID:** `{user_id}`\n**Reason:** `{intruder.reason}`\n"
                            f"**Quick Action:** Banned in {message.chat.title}\n\n"
                            f"$AUTOBAN #id{user_id}"
                        ),
                    )
    message.continue_propagation()


@pool.run_in_thread
def _get_spamwatch_data(user_id: int) -> Union[Ban, bool]:
    return spamwatch.Client(Config.SPAM_WATCH_API).get_ban(user_id)
