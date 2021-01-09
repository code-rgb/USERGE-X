import asyncio

from pyrogram.errors import YouBlockedUser

from userge import Message, userge


@userge.on_cmd(
    "q",
    about={
        "header": "Quote a message",
        "flags": {"-l": "limit, for multiple messages"},
        "usage": "Reply {tr}q -l[message limit]",
        "examples": ["{tr}q", "{tr}q -l3"],
    },
    allow_via_bot=False,
    del_pre=True,
)
async def quotecmd(message: Message):
    """quotecmd"""
    quote_list = []
    replied = message.reply_to_message
    if replied and "l" in message.flags and not message.filtered_input_str:
        args = ""
        limit = message.flags.get("l", 1)
        if limit.isdigit():
            limit = int(limit)
        else:
            return await message.err("give valid no. of message to quote", del_in=3)
        num = min(limit, 24)
        async for msg in userge.iter_history(
            message.chat.id, limit=num, offset_id=replied.message_id, reverse=True
        ):
            if msg.message_id != message.message_id:
                quote_list.append(msg.message_id)
    else:
        args = message.input_str
        quote_list.append(replied.message_id)
    asyncio.get_event_loop().create_task(message.delete())

    async with userge.conversation("QuotLyBot") as conv:
        try:
            if quote_list and not args:
                await userge.forward_messages("QuotLyBot", message.chat.id, quote_list)
            else:
                if not args:
                    await message.err("input not found!")
                    return
                await conv.send_message(args)
        except YouBlockedUser:
            await message.edit("first **unblock** @QuotLyBot")
            return
        quote = await conv.get_response(mark_read=True)
        if not (quote.sticker or quote.document):
            await message.err("something went wrong!")
        else:
            message_id = replied.message_id if replied else None
            if quote.sticker:
                await userge.send_sticker(
                    chat_id=message.chat.id,
                    sticker=quote.sticker.file_id,
                    reply_to_message_id=message_id,
                )
            else:
                await userge.send_document(
                    chat_id=message.chat.id,
                    document=quote.document.file_id,
                    reply_to_message_id=message_id,
                )
