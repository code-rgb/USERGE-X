import time
from math import floor
from typing import Dict, Tuple

import userge
from userge.utils.tools import humanbytes, time_formatter

from .rawbotapi import xbot

_TASKS: Dict[str, Tuple[int, int]] = {}


async def inline_progress(
    current: int,
    total: int,
    message: "userge.Message",
    inline_id: str,
    ud_type: str,
    file_name: str = "",
    edit_type: str = "text",
    delay: int = userge.Config.EDIT_SLEEP_TIMEOUT,
) -> None:
    """ progress function """
    if message.process_is_canceled:
        await message.client.stop_transmission()
    task_id = f"{message.chat.id}.{message.message_id}"
    if current == total:
        if task_id not in _TASKS:
            return
        del _TASKS[task_id]
        if edit_type == "text":

            await xbot.edit_inline_text(
                inline_id, text="<code>Uploading to telegram...</code>"
            )

        else:

            await xbot.edit_inline_caption(
                inline_id, caption="<code>Uploading to telegram ...</code>"
            )

    now = time.time()
    if task_id not in _TASKS:
        _TASKS[task_id] = (now, now)
    start, last = _TASKS[task_id]
    elapsed_time = now - start
    if (now - last) >= delay:
        _TASKS[task_id] = (start, now)
        percentage = current * 100 / total
        speed = current / elapsed_time
        time_to_completion = time_formatter(int((total - current) / speed))
        progress_str = (
            "__{}__ : `{}`\n"
            + "```[{}{}]```\n"
            + "**Progress** : `{}%`\n"
            + "**Completed** : `{}`\n"
            + "**Total** : `{}`\n"
            + "**Speed** : `{}/s`\n"
            + "**ETA** : `{}`"
        )
        progress_str = progress_str.format(
            ud_type,
            file_name,
            "".join(
                (
                    userge.Config.FINISHED_PROGRESS_STR
                    for i in range(floor(percentage / 5))
                )
            ),
            "".join(
                (
                    userge.Config.UNFINISHED_PROGRESS_STR
                    for i in range(20 - floor(percentage / 5))
                )
            ),
            round(percentage, 2),
            humanbytes(current),
            humanbytes(total),
            humanbytes(speed),
            time_to_completion or "0 s",
        )

        if edit_type == "text":
            await xbot.edit_inline_text(inline_id, text=progress_str)
        else:
            await xbot.edit_inline_caption(inline_id, caption=progress_str)
