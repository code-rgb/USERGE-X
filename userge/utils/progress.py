import asyncio
import time
from math import floor
from typing import Dict, Tuple

from pyrogram.errors import FloodWait
from pyrogram.types import CallbackQuery

import userge

from .tools import humanbytes, time_formatter

_TASKS: Dict[str, Tuple[int, int]] = {}


async def progress(
    current: int,
    total: int,
    message: "userge.Message",
    ud_type: str,
    file_name: str = "",
    c_q: CallbackQuery = None,
    delay: int = userge.Config.EDIT_SLEEP_TIMEOUT,
) -> None:
    """progress function"""
    if message.process_is_canceled:
        await message.client.stop_transmission()
    task_id = f"{message.chat.id}.{message.message_id}"
    if current == total:
        if task_id not in _TASKS:
            return
        del _TASKS[task_id]
        try:
            if c_q:
                await c_q.edit_message_text("`finalizing process ...`")
            else:
                await message.try_to_edit("`finalizing process ...`")
        except FloodWait as f_e:
            await asyncio.sleep(f_e.x)
        return
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
            time_to_completion if time_to_completion else "0 s",
        )
        try:
            if c_q:
                await c_q.edit_message_text(progress_str)
            else:
                await message.try_to_edit(progress_str)
        except FloodWait as f_e:
            await asyncio.sleep(f_e.x)
