"""Manage Voice Chat Settings"""

from functools import wraps
from random import randint, sample
from typing import List, Optional

from pyrogram.errors import Forbidden, PeerIdInvalid
from pyrogram.raw.functions.channels import GetFullChannel
from pyrogram.raw.functions.messages import GetFullChat
from pyrogram.raw.functions.phone import (
    CreateGroupCall,
    DiscardGroupCall,
    EditGroupCallParticipant,
    EditGroupCallTitle,
    GetGroupCall,
    InviteToGroupCall,
)
from pyrogram.raw.types import (
    InputGroupCall,
    InputPeerChannel,
    InputPeerChat,
    InputPeerUser,
)

from userge import Message, userge
from userge.utils import clean_obj

from ..tools.json import yamlify


def check_vc_perm(func):
    """ to check if can_manage_voice_chats=True  """

    @wraps(func)
    async def vc_perm(m: Message):
        if (
            m.chat.type in ["group", "supergroup"]
            and not (m.from_user.is_deleted or m.from_user.is_bot)
            and m.from_user.is_self
            and getattr(
                (await m.chat.get_member(m.from_user.id)),
                "can_manage_voice_chats",
                False,
            )
        ):
            await func(m)
        else:
            await m.err("You can't manage Voice Chats in this Chat !", del_in=10)

    return vc_perm


@userge.on_cmd(
    "vc_start",
    about={
        "header": "Create a voice chat",
        "examples": "{tr}vc_start",
    },
    allow_channels=False,
    allow_private=False,
    allow_via_bot=False,
    only_admins=True,
)
@check_vc_perm
async def start_vc_(message: Message):
    """Start voice chat"""
    chat_id = message.chat.id
    await userge.send(
        CreateGroupCall(
            peer=(await userge.resolve_peer(chat_id)),
            random_id=randint(10000, 999999999),
        )
    )
    await message.edit(
        f"Started Voice Chat in **Chat ID** : `{chat_id}`", del_in=5, log=__name__
    )


@userge.on_cmd(
    "vc_end",
    about={
        "header": "End a voice chat",
        "examples": "{tr}vc_end",
    },
    allow_channels=False,
    allow_private=False,
    allow_via_bot=False,
    only_admins=True,
)
@check_vc_perm
async def end_vc_(message: Message):
    """End voice chat"""
    chat_id = message.chat.id
    if not (
        group_call := (
            await get_group_call(message, err_msg=", Voice Chat already ended")
        )
    ):
        return
    await userge.send(DiscardGroupCall(call=group_call))
    await message.edit(
        f"Ended Voice Chat in **Chat ID** : `{chat_id}`", del_in=5, log=__name__
    )


@userge.on_cmd(
    "vc_inv",
    about={
        "header": "Invite to a voice chat",
        "examples": "{tr}vc_inv",
        "flags": {"-l": "randomly invite members"},
    },
    allow_channels=False,
    allow_private=False,
    allow_via_bot=False,
)
async def inv_vc_(message: Message):
    """invite to voice chat"""
    peer_list = None
    reply = message.reply_to_message
    limit_ = int(message.flags.get("-l", 0))
    await message.edit("`Inviting Members to Voice Chat ...`")
    if limit_ != 0:
        peer_list = (
            await get_peer_list(message, limit_)
            if limit_ > 0
            else await get_peer_list(message)
        )
    elif message.input_str:
        if "," in message.input_str:
            peer_list = await append_peer_user(
                [_.strip() for _ in message.input_str.split(",")]
            )
        else:
            peer_list = await append_peer_user([message.input_str.split()[0]])
    elif reply and reply.from_user and not reply.from_user.is_bot:
        peer_list = await append_peer_user([reply.from_user.id])
    if not peer_list:
        await message.err("No User Found to Invite !", del_in=5)
        return
    if not (
        group_call := (
            await get_group_call(message, err_msg=", first start by .startvc")
        )
    ):
        return
    if not await vc_member(message, group_call):
        return
    try:
        await userge.send(InviteToGroupCall(call=group_call, users=peer_list))
    except Forbidden:
        await message.err("Join Voice Chat First !", del_in=8)
    else:
        await message.edit("✅  Invited Successfully !", del_in=5)


@userge.on_cmd(
    "vc_info",
    about={
        "header": "Voice Chat info",
        "examples": "{tr}vc_info",
        "flags": {"-d": "Detailed User info"},
    },
    allow_channels=False,
    allow_private=False,
    allow_via_bot=False,
)
async def vcinfo_(message: Message):
    if not (group_call := (await get_group_call(message))):
        return
    gc_data = await userge.send(GetGroupCall(call=group_call))
    gc_info = {}
    gc_info["ℹ️ INFO"] = clean_obj(gc_data.call, convert=True)
    if len(gc_data.users) != 0:
        if "-d" in message.flags:
            gc_info["👥 Participants"] = [
                clean_obj(x, convert=True) for x in gc_data.participants
            ]
        else:
            gc_info["👥 Users"] = [
                {"Name": x.first_name, "ID": x.id} for x in gc_data.users
            ]
    await message.edit_or_send_as_file(
        text="🎙  **Voice Chat**\n\n" + yamlify(gc_info),
        filename="group_call.yaml",
        caption="Group_Call_Info",
    )


@userge.on_cmd(
    "vc_title",
    about={
        "header": "Change title of voice chat",
        "examples": "{tr}vc_title [New title]",
    },
    allow_channels=False,
    allow_private=False,
    allow_via_bot=False,
    only_admins=True,
)
@check_vc_perm
async def vc_title(message: Message):
    """Change title of voice chat"""
    title = message.input_str
    if not title:
        return await message.err("No Input Found !", del_in=10)

    if not (group_call := (await get_group_call(message))):
        return
    if await userge.send(EditGroupCallTitle(call=group_call, title=title.strip())):
        await message.edit(f"**Successfully** Changed VC Title to `{title}`", del_in=5)
    else:
        await message.edit("Oops 😬, Something Went Wrong !", del_in=5)


@userge.on_cmd(
    "vc_unmute",
    about={
        "header": "unmute a person in voice chat",
        "examples": "{tr}vc_unmute 519198181",
        "flags": {"-all": "unmute all"},
    },
    allow_channels=False,
    allow_private=False,
    allow_via_bot=False,
    only_admins=True,
)
@check_vc_perm
async def unmute_vc_(message: Message):
    """Unmute a member in voice chat"""
    await manage_vcmember(message, to_mute=False)


@userge.on_cmd(
    "vc_mute",
    about={
        "header": "mute a person in voice chat",
        "examples": "{tr}vc_mute 519198181",
        "flags": {"-all": "mute all"},
    },
    allow_channels=False,
    allow_private=False,
    allow_via_bot=False,
    only_admins=True,
)
@check_vc_perm
async def mute_vc_(message: Message):
    """Mute a member in voice chat"""
    await manage_vcmember(message, to_mute=True)


async def manage_vcmember(message: Message, to_mute: bool):
    if not (group_call := (await get_group_call(message))):
        return
    peer_ = None
    if not await vc_member(message, group_call):
        return
    if message.input_str:
        peer_ = message.input_str.strip()
    elif message.reply_to_message and message.reply_to_message.text:
        peer_ = message.reply_to_message.text
    if peer_ and (user_ := (await append_peer_user([peer_]))):
        await userge.send(
            EditGroupCallParticipant(call=group_call, user_id=user_[0], muted=to_mute)
        )
        await message.edit(
            str(user_[0].user_id)
            + (" **Muted** " if to_mute else " **Unmuted** ")
            + "succesfully",
            del_in=5,
        )


async def get_group_call(
    message: Message, err_msg: str = ""
) -> Optional[InputGroupCall]:
    chat_peer = await userge.resolve_peer(message.chat.id)
    if isinstance(chat_peer, (InputPeerChannel, InputPeerChat)):
        if isinstance(chat_peer, InputPeerChannel):
            full_chat = (await userge.send(GetFullChannel(channel=chat_peer))).full_chat
        elif isinstance(chat_peer, InputPeerChat):
            full_chat = (
                await userge.send(GetFullChat(chat_id=chat_peer.chat_id))
            ).full_chat
        if full_chat is not None:
            return full_chat.call
    await message.err(f"**No Voice Chat Found** !{err_msg}", del_in=8)
    return False


async def get_peer_list(message: Message, limit: int = 10) -> Optional[List]:
    chat_id = message.chat.id
    user_ids = [
        member.user.id
        async for member in userge.iter_chat_members(chat_id, limit=100)
        if not (
            member.user.is_bot
            or member.user.is_deleted
            or member.user.id == message.from_user.id
        )
    ]
    return await append_peer_user(user_ids, limit)


async def append_peer_user(user_ids: List, limit: int = None) -> Optional[List]:
    peer_list = []
    for uid in user_ids:
        try:
            peer_ = await userge.resolve_peer(uid)
        except PeerIdInvalid:
            pass
        else:
            if isinstance(peer_, InputPeerUser):
                peer_list.append(peer_)
    if len(peer_list) != 0:
        return sample(peer_list, min(len(peer_list), limit)) if limit else peer_list


async def vc_member(m: Message, gc: InputGroupCall) -> bool:
    if p := getattr(gc, "participants", None):
        for x in p:
            if x.peer.user_id == m.from_user.id:
                return True
    await m.err("Join Voice Chat Manually First !", del_in=7)
    return False
