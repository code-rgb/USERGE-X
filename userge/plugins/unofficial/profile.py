""" All Profile Settings for User """

# del_pfp by Phyco-Ninja
# rewrote poto by code-rgb

import asyncio
import os
from datetime import datetime

from pyrogram.errors import (
    AboutTooLong,
    BadRequest,
    FloodWait,
    UsernameNotOccupied,
    UsernameOccupied,
    VideoFileInvalid,
)
from pyrogram.types import InputMediaPhoto
from userge import Config, Message, userge
from userge.utils import progress

CHANNEL = userge.getCLogger(__name__)
PHOTO = Config.DOWN_PATH + "profile_pic.jpg"
USER_DATA = {}


@userge.on_cmd(
    "setname",
    about={
        "header": "Update first, last name and username",
        "flags": {
            "-fname": "update only first name",
            "-lname": "update only last name",
            "-dlname": "delete last name",
            "-uname": "update username",
            "-duname": "delete username",
        },
        "usage": "{tr}setname [flag] [name]\n" "{tr}setname [first name] | [last name]",
        "examples": [
            "{tr}setname -dlname",
            "{tr}setname -fname Joe",
            "{tr}setname -lname Mama",
            "{tr}setname Joe | Mama",
            "{tr}setname -uname username",
            "{tr}setname -duname",
        ],
    },
    allow_via_bot=False,
)
async def setname_(message: Message):
    """ set or delete profile name and username """
    if not message.input_str:
        await message.err("Need Text to Change Profile...")
        return
    if "-dlname" in message.flags:
        await userge.update_profile(last_name="")
        await message.edit("```Last Name is Successfully Removed ...```", del_in=3)
        return
    if "-duname" in message.flags:
        await userge.update_username(username="")
        await message.edit("```Username is successfully Removed ...```", del_in=3)
        return
    arg = message.filtered_input_str
    if not arg:
        await message.err("Need Text to Change Profile...")
        return
    if "-fname" in message.flags:
        await userge.update_profile(first_name=arg.strip())
        await message.edit("```First Name is Successfully Updated ...```", del_in=3)
    elif "-lname" in message.flags:
        await userge.update_profile(last_name=arg.strip())
        await message.edit("```Last Name is Successfully Updated ...```", del_in=3)
    elif "-uname" in message.flags:
        try:
            await userge.update_username(username=arg.strip())
        except UsernameOccupied:
            await message.err("Username is Not Available...")
        else:
            await message.edit("```Username is Successfully Updated ...```", del_in=3)
    elif "|" in message.input_str:
        fname, lname = message.input_str.split("|", maxsplit=1)
        if not lname:
            await message.err("Need Last Name to Update Profile...")
            return
        await userge.update_profile(first_name=fname.strip(), last_name=lname.strip())
        await message.edit(
            "```My Profile Name is Successfully Updated ...```", del_in=3
        )
    else:
        await message.err("Invalid Args, Exiting...")


@userge.on_cmd(
    "bio",
    about={
        "header": "Update bio, Maximum limit 70 characters",
        "flags": {"-delbio": "delete bio"},
        "usage": "{tr}bio [flag] \n" "{tr}bio [Bio]",
        "examples": ["{tr}bio -delbio", "{tr}bio  My name is krishna :-)"],
    },
    allow_via_bot=False,
)
async def bio_(message: Message):
    """ Set or delete profile bio """
    if not message.input_str:
        await message.err("Need Text to Change Bio...")
        return
    if "-delbio" in message.flags:
        await userge.update_profile(bio="")
        await message.edit("```Bio is Successfully Deleted ...```", del_in=3)
        return
    if message.input_str:
        try:
            await userge.update_profile(bio=message.input_str)
        except AboutTooLong:
            await message.err("Bio is More then 70 characters...")
        else:
            await message.edit(
                "```My Profile Bio is Successfully Updated ...```", del_in=3
            )


@userge.on_cmd(
    "setpfp",
    about={"header": "Set profile picture", "usage": "{tr}setpfp [reply to any photo]"},
    allow_via_bot=False,
)
async def set_profile_picture(message: Message):
    """ Set Profile Picture """
    await message.edit("```processing ...```")

    replied = message.reply_to_message
    s_time = datetime.now()

    if (
        replied
        and replied.media
        and (
            replied.photo
            or (replied.document and "image" in replied.document.mime_type)
        )
    ):

        await userge.download_media(
            message=replied,
            file_name=PHOTO,
            progress=progress,
            progress_args=(message, "trying to download and set profile picture"),
        )

        await userge.set_profile_photo(photo=PHOTO)

        if os.path.exists(PHOTO):
            os.remove(PHOTO)
        e_time = datetime.now()
        t_time = (e_time - s_time).seconds
        await message.edit(f"`Profile picture set in {t_time} seconds.`")

    elif replied and replied.media and (replied.video or replied.animation):
        VIDEO = Config.DOWN_PATH + "profile_vid.mp4"
        await userge.download_media(
            message=replied,
            file_name=VIDEO,
            progress=progress,
            progress_args=(message, "trying to download and set profile picture"),
        )

        try:
            await userge.set_profile_photo(video=VIDEO)
        except VideoFileInvalid:
            await message.err("Video File is Invalid")
        else:
            e_time = datetime.now()
            t_time = (e_time - s_time).seconds

            await message.edit(f"`Profile picture set in {t_time} seconds.`")
    else:
        await message.err("Reply to any photo or video to set profile pic...")


@userge.on_cmd(
    "vpf",
    about={
        "header": "View Profile of any user",
        "flags": {
            "-fname": "Print only first name",
            "-lname": "Print only last name",
            "-flname": "Print full name",
            "-bio": "Print bio",
            "-uname": "Print username",
        },
        "usage": "{tr}vpf [flags]\n{tr}vpf [flags] [reply to any user]",
        "note": "<b> -> Use 'me' after flags to print own profile</b>\n"
        "<code>{tr}vpf [flags] me</code>",
    },
)
async def view_profile(message: Message):
    """ View Profile  """

    if not message.input_or_reply_str:
        await message.err("User id / Username not found...")
        return
    if message.reply_to_message:
        input_ = message.reply_to_message.from_user.id
    else:
        input_ = message.filtered_input_str
    if not input_:
        await message.err("User id / Username not found...")
        return
    if not message.flags:
        await message.err("Flags Required")
        return
    if "me" in message.filtered_input_str:
        user = await message.client.get_me()
        bio = (await message.client.get_chat("me")).bio
    else:
        try:
            user = await message.client.get_users(input_)
            bio = (await message.client.get_chat(input_)).bio
        except Exception:
            await message.err("invalid user_id!")
            return
    if "-fname" in message.flags:
        await message.edit("```checking, wait plox !...```", del_in=3)
        first_name = user.first_name
        await message.edit("<code>{}</code>".format(first_name), parse_mode="html")
    elif "-lname" in message.flags:
        if not user.last_name:
            await message.err("User not have last name...")
        else:
            await message.edit("```checking, wait plox !...```", del_in=3)
            last_name = user.last_name
            await message.edit("<code>{}</code>".format(last_name), parse_mode="html")
    elif "-flname" in message.flags:
        await message.edit("```checking, wait plox !...```", del_in=3)
        if not user.last_name:
            await message.edit(
                "<code>{}</code>".format(user.first_name), parse_mode="html"
            )
        else:
            full_name = user.first_name + " " + user.last_name
            await message.edit("<code>{}</code>".format(full_name), parse_mode="html")
    elif "-bio" in message.flags:
        if not bio:
            await message.err("User not have bio...")
        else:
            await message.edit("`checking, wait plox !...`", del_in=3)
            await message.edit("<code>{}</code>".format(bio), parse_mode="html")
    elif "-uname" in message.flags:
        if not user.username:
            await message.err("User not have username...")
        else:
            await message.edit("```checking, wait plox !...```", del_in=3)
            username = user.username
            await message.edit("<code>{}</code>".format(username), parse_mode="html")


@userge.on_cmd(
    "delpfp",
    about={
        "header": "Delete Profile Pics",
        "description": "Delete profile pic in one blow" " [NOTE: May Cause Flood Wait]",
        "usage": "{tr}delpfp [pfp count]",
    },
    allow_via_bot=False,
)
async def del_pfp(message: Message):
    """ delete profile pics """
    if message.input_str:
        try:
            del_c = int(message.input_str)
        except ValueError as v_e:
            await message.err(v_e)
            return
        await message.edit(f"```Deleting first {del_c} Profile Photos ...```")
        start = datetime.now()
        ctr = 0
        async for photo in userge.iter_profile_photos("me", limit=del_c):
            await userge.delete_profile_photos(photo.file_id)
            ctr += 1
        end = datetime.now()
        difff = (end - start).seconds
        await message.edit(f"Deleted {ctr} Profile Pics in {difff} seconds!")
    else:
        await message.err("What am i supposed to delete nothing!...")
        await message.reply_sticker(sticker="CAADAQAD0wAD976IR_CYoqvCwXhyFgQ")


@userge.on_cmd(
    "clone",
    about={
        "header": "Clone first name, last name, bio and profile picture of any user",
        "flags": {
            "-fname": "Clone only first name",
            "-lname": "Clone only last name",
            "-bio": "Clone only bio",
            "-pp": "Clone only profile picture",
        },
        "usage": "{tr}clone [flag] [username | reply to any user]\n"
        "{tr}clone [username | reply to any user]",
        "examples": [
            "{tr}clone -fname username",
            "{tr}clone -lname username",
            "{tr}clone -pp username",
            "{tr}clone -bio username",
            "{tr}clone username",
        ],
        "note": "<code>● Use revert after clone to get original profile</code>\n"
        "<code>● Don't use @ while giving username</code>",
    },
    allow_via_bot=False,
)
async def clone_(message: Message):
    """ Clone first name, last name, bio and profile picture """
    if message.reply_to_message:
        input_ = message.reply_to_message.from_user.id
    else:
        input_ = message.filtered_input_str

    if not input_:
        await message.err("User id / Username not found!...")
        return

    await message.edit("`clonning...`")

    try:
        chat = await userge.get_chat(input_)
        user = await userge.get_users(input_)
    except UsernameNotOccupied:
        await message.err("Don't know that User!...")
        return
    me = await userge.get_me()

    if "-fname" in message.flags:
        if "first_name" in USER_DATA:
            await message.err("First Revert!...")
            return
        USER_DATA["first_name"] = me.first_name or ""
        await userge.update_profile(first_name=user.first_name or "")
        await message.edit("```First Name is Successfully cloned ...```", del_in=3)
    elif "-lname" in message.flags:
        if "last_name" in USER_DATA:
            await message.err("First Revert!...")
            return
        USER_DATA["last_name"] = me.last_name or ""
        await userge.update_profile(last_name=user.last_name or "")
        await message.edit("```Last name is successfully cloned ...```", del_in=3)
    elif "-bio" in message.flags:
        if "bio" in USER_DATA:
            await message.err("First Revert!...")
            return
        mychat = await userge.get_chat(me.id)
        USER_DATA["bio"] = mychat.bio or ""
        await userge.update_profile(
            bio=(chat.bio or "")[:69]
        )  # 70 is the max bio limit
        await message.edit("```Bio is Successfully Cloned ...```", del_in=3)
    elif "-pp" in message.flags:
        if os.path.exists(PHOTO):
            await message.err("First Revert!...")
            return
        if not user.photo:
            await message.err("User not have any profile pic...")
            return
        await userge.download_media(user.photo.big_file_id, file_name=PHOTO)
        await userge.set_profile_photo(photo=PHOTO)
        await message.edit("```Profile photo is Successfully Cloned ...```", del_in=3)
    else:
        if USER_DATA or os.path.exists(PHOTO):
            await message.err("First Revert!...")
            return
        mychat = await userge.get_chat(me.id)
        USER_DATA.update(
            {
                "first_name": me.first_name or "",
                "last_name": me.last_name or "",
                "bio": mychat.bio or "",
            }
        )
        await userge.update_profile(
            first_name=user.first_name or "",
            last_name=user.last_name or "",
            bio=(chat.bio or "")[:69],
        )
        if not user.photo:
            await message.edit(
                "`User not have profile photo, Cloned Name and bio...`", del_in=5
            )
            return
        await userge.download_media(user.photo.big_file_id, file_name=PHOTO)
        await userge.set_profile_photo(photo=PHOTO)
        await message.edit("```Profile is Successfully Cloned ...```", del_in=3)


@userge.on_cmd(
    "revert",
    about={"header": "Returns original profile", "usage": "{tr}revert"},
    allow_via_bot=False,
)
async def revert_(message: Message):
    """ Returns Original Profile """
    if not (USER_DATA or os.path.exists(PHOTO)):
        await message.err("Already Reverted!...")
        return
    if USER_DATA:
        await userge.update_profile(**USER_DATA)
        USER_DATA.clear()
    if os.path.exists(PHOTO):
        me = await userge.get_me()
        photo = (await userge.get_profile_photos(me.id, limit=1))[0]
        await userge.delete_profile_photos(photo.file_id)
        os.remove(PHOTO)
    await message.edit("```Profile is Successfully Reverted...```", del_in=3)


async def chat_type_(message: Message, input_chat):
    try:
        chat_ = await message.client.get_chat(input_chat)
    except (BadRequest, IndexError) as e:
        return str(e), 0, 0
    return chat_.type, chat_.id, chat_.photo.big_file_id


async def send_single(message: Message, peer_id, pos, reply_id):
    pic_ = await message.client.get_profile_photos(peer_id, limit=min(pos, 100))
    if len(pic_) != 0:
        await message.client.send_photo(
            message.chat.id, photo=pic_.pop().file_id, reply_to_message_id=reply_id
        )


# photo grabber
@userge.on_cmd(
    "poto",
    about={
        "header": "use this plugin to get photos of user or chat",
        "description": "fetches upto 100 photos of a user or chat",
        "flags": {"-l": "limit, max. 100", "-p": "for photo at particular postion"},
        "examples": [
            "{tr}poto",
            "{tr}poto [reply to chat message]",
            "{tr}poto @midnightmadwalk -p5\n    (i.e sends photo at position 5)",
            "{tr}poto @midnightmadwalk -l5\n    (i.e sends an album of first 5 photos)",
        ],
    },
)
async def poto_x(message: Message):
    chat_id = message.chat.id
    reply = message.reply_to_message
    reply_id = reply.message_id if reply else None
    await message.edit("`Fetching photos ...`")
    if reply:
        input_ = reply.from_user.id
    elif message.filtered_input_str:
        input_ = message.filtered_input_str.strip()
        if len(input_.split()) != 1:
            await message.err("provide a valid ID or username", del_in=5)
            return
    else:
        input_ = chat_id
    type_, peer_id, f_id = await chat_type_(message, input_)
    if peer_id == 0:
        await message.err(type_, del_in=7)
        return
    if type_ in ("group", "supergroup", "channel") and message.client.is_bot:
        photo_ = await userge.bot.download_media(f_id)
        await userge.bot.send_photo(chat_id, photo_, reply_to_message_id=reply_id)
        os.remove(photo_)
        await message.delete()
        return
    flags_ = message.flags
    if "-p" in flags_:
        pos_ = flags_.get("-p", 0)
        if not str(pos_).isdigit():
            await message.err('"-p" Flag only takes integers', del_in=5)
            return
        await send_single(message, peer_id=peer_id, pos=int(pos_), reply_id=reply_id)
    elif "-l" in flags_:
        get_l = flags_.get("-l", 0)
        if not str(get_l).isdigit():
            await message.err('"-l" Flag only takes integers', del_in=5)
            return
        media, media_group = [], []
        async for photo_ in message.client.iter_profile_photos(
            peer_id, limit=min(int(get_l), 100)
        ):
            media.append(InputMediaPhoto(photo_.file_id))
            if len(media) == 10:
                media_group.append(media)
                media = []
        if len(media) != 0:
            media_group.append(media)
        if len(media_group) == 0:
            # Happens if bot doesn't know the user
            await message.delete()
            return
        try:
            for poto_ in media_group:
                await userge.send_media_group(chat_id, media=poto_)
                await asyncio.sleep(2)
        except FloodWait as e:
            await asyncio.sleep(e.x + 3)
        except Exception as err:
            await CHANNEL.log(f"**ERROR:** `{str(err)}`")
    else:
        await send_single(message, peer_id=peer_id, pos=1, reply_id=reply_id)
    await message.delete()
