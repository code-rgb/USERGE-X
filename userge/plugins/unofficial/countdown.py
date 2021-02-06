# Idea by @Decage
# Plugin By Github.com/code-rgb [ TG - @DeletedUser420 ]

""" Start a Real-Time CountDown """

import re

from userge import Message, userge


@userge.on_cmd(
    "cdown",
    about={
        "header": "Creates Count Down",
        "usage": "{tr}cdown [text] %%day-hour-min.%% [more text]",
        "examples": ["{tr}cdown Bomb Blast in %%10-25-45%% , Run For Life !"],
    },
    allow_via_bot=False,
)
async def count_it_down(message: Message):
    """ Start A CountDown """
    reply = message.reply_to_message
    args = message.input_str
    if args:
        text = args
    else:
        return await message.err("Input not found!", del_in=5)
    pattern = r"%%(?:[0-9]{2}-[0-9]{2}-[0-9]{2})%%"  # Checking if format is Valid
    match = re.search(pattern, args)
    if not match:
        return await message.err("Format Invalid ! See Help For More Info !", del_in=5)
    reply_id = reply.message_id if reply else None
    await message.delete()
    try:
        inline_msg = await userge.get_inline_bot_results("CountdownMeBot", text)
        reply.message_id if reply else None
        await userge.send_inline_bot_result(
            chat_id=message.chat.id,
            query_id=inline_msg.query_id,
            result_id=inline_msg.results[0].id,
            reply_to_message_id=reply_id,
        )
    except IndexError:
        await message.err("List index out of range")
