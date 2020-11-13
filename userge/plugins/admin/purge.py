import time

from userge import Message, userge
from userge.utils import time_formatter


@userge.on_cmd(
    "purge",
    about={
        "header": "purge messages from user",
        "flags": {
            "-u": "get user_id from replied message",
            "-l": "message limit : max 100",
        },
        "usage": "reply {tr}purge to the start message to purge.\n"
        "use {tr}purge [user_id | user_name] to purge messages from that user or use flags",
        "examples": ["{tr}purge", "{tr}purge -u", "{tr}purge [user_id | user_name]"],
    },
    allow_bots=False,
    del_pre=True,
)
async def purge_(message: Message):
    """purge from replied message"""
    await message.edit("`purging ...`")
    from_user_id = None
    if message.filtered_input_str:
        from_user_id = (await message.client.get_users(message.filtered_input_str)).id
    start_message = 0
    if "l" in message.flags:
        limit = int(message.flags["l"])
        limit = min(limit, 100)
        start_message = message.message_id - limit
    if message.reply_to_message:
        start_message = message.reply_to_message.message_id
        if "u" in message.flags:
            from_user_id = message.reply_to_message.from_user.id
    if not start_message:
        await message.err("invalid start message!")
        return
    list_of_messages = []
    purged_messages_count = 0

    async def handle_msg(a_message):
        nonlocal list_of_messages, purged_messages_count
        if (
            from_user_id
            and a_message
            and a_message.from_user
            and a_message.from_user.id == from_user_id
        ):
            list_of_messages.append(a_message.message_id)
        if not from_user_id:
            list_of_messages.append(a_message.message_id)
        if len(list_of_messages) >= 100:
            await message.client.delete_messages(
                chat_id=message.chat.id, message_ids=list_of_messages
            )
            purged_messages_count += len(list_of_messages)
            list_of_messages = []

    start_t = time.time()
    if message.client.is_bot:
        for a_message in await message.client.get_messages(
            chat_id=message.chat.id,
            replies=0,
            message_ids=range(start_message, message.message_id),
        ):
            await handle_msg(a_message)
    else:
        async for a_message in message.client.iter_history(
            chat_id=message.chat.id, limit=None, offset_id=start_message, reverse=True
        ):
            await handle_msg(a_message)
    if list_of_messages:
        await message.client.delete_messages(
            chat_id=message.chat.id, message_ids=list_of_messages
        )
        purged_messages_count += len(list_of_messages)
    end_t = time.time()
    out = f"<u>purged</u> {purged_messages_count} messages in {time_formatter(end_t - start_t)}."
    await message.edit(out, del_in=3)


@userge.on_cmd(
    "purgeme",
    about={
        "header": "purge messages from yourself",
        "usage": "{tr}purgeme [number]",
        "examples": ["{tr}purgeme 10"],
    },
    allow_bots=False,
    allow_channels=False,
    allow_via_bot=False,
)
async def purgeme_(message: Message):
    """purge given no. of your messages"""
    await message.edit("`purging ...`")
    if not (message.input_str and message.input_str.isdigit()):
        return await message.err(
            "Provide a valid number of message to delete", del_in=3
        )
    start_t = time.time()
    number = min(int(message.input_str), 100)
    msg_list = []
    async for msg in userge.search_messages(
        message.chat.id, "", limit=number, from_user="me"
    ):
        msg_list.append(msg.message_id)
    await userge.delete_messages(message.chat.id, message_ids=msg_list)
    end_t = time.time()
    out = (
        f"<u>purged</u> {len(msg_list)} messages in {time_formatter(end_t - start_t)}."
    )
    await message.edit(out, del_in=3, log=__name__)
