# Copyright (C) 2020 BY - GitHub.com/code-rgb [TG - @deleteduser420]
# All rights reserved.


import time

from prettytable import PrettyTable
from userge import Message, userge
from userge.utils import humanbytes, mention_html, time_formatter

TYPES = [
    "photo",
    "video",
    "video_note",
    "document",
    "animation",
    "voice",
    "audio",
    "sticker",
]


@userge.on_cmd(
    "media_h",
    about={
        "header": "Find media history of a User",
        "usage": "reply {tr}media_h to any message",
    },
)
async def media_h(message: Message):
    reply = message.reply_to_message
    if not reply:
        return await message.err("reply to a User")
    start = time.time()
    await message.edit(
        'This process takes soo much F*ing Time 😂 so here\'s a quote 🙆‍♀️\n\n`"All you gotta do is chill out... Let go of control and chill out... Let it be, Trust."`\n- **Esther Hicks**'
    )
    x = PrettyTable()
    media_dict = {}
    # Generate json
    for m in TYPES:
        media_dict[m] = {}
        media_dict[m]["file_size"] = 0
        media_dict[m]["count"] = 0
        media_dict[m]["max_size"] = 0
        media_dict[m]["max_file_link"] = ""
    # Count
    msg_count = 0
    x.title = "File Summary:"
    x.field_names = ["Media", "Count", "File size"]
    largest = "   <b>Largest Size</b>\n"
    u_mention = mention_html(reply.from_user.id, reply.from_user.first_name)
    async for msg in userge.search_messages(
        message.chat.id, "", from_user=reply.from_user.id
    ):
        msg_count += 1
        for media in TYPES:
            if msg[media]:
                media_dict[media]["file_size"] += msg[media].file_size
                media_dict[media]["count"] += 1
                if msg[media].file_size > media_dict[media]["max_size"]:
                    media_dict[media]["max_size"] = msg[media].file_size
                    media_dict[media]["max_file_link"] = msg.link

    for mediax in TYPES:
        x.add_row(
            [
                mediax,
                media_dict[mediax]["count"],
                humanbytes(media_dict[mediax]["file_size"]),
            ]
        )
        if media_dict[mediax]["count"] != 0:
            largest += f"•  [{mediax}]({media_dict[mediax]['max_file_link']}) : <code>{humanbytes(media_dict[mediax]['max_size'])}</code>\n"

    result = f"<b>{message.chat.title}</b>\n"
    result += f"👤 <b>User</b> : {u_mention}\n"
    result += f"<code>Total Messages: {msg_count}</code>\n"
    result += f"```{str(x)}```\n"
    result += f"{largest}\n"
    end = time.time()
    result += f"⏳ <code>Process took: {time_formatter(end - start)}</code>."
    await message.edit(result, disable_web_page_preview=True)
