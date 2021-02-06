"""MergeMedia"""
#  Copyright (C) 2020 BY USERGE-X
#  All rights reserved.
#
#  Author: https://github.com/midnightmadwalk [TG: @midnightmadwalk]

import codecs
import os
import re
import shutil
from pathlib import Path

from hachoir.stream.input import InputStreamError, NullStreamError
from userge import Message, userge
from userge.plugins.misc.upload import upload
from userge.utils import progress, runcmd, safe_filename


@userge.on_cmd(
    "mergesave",
    about={
        "header": "save file for {tr}merge",
        "usage": "{tr} reply to [media] for saving it ",
    },
)
async def mergesave_(message: Message):
    """Save Media"""
    # saving files in a separate folder.
    r = message.reply_to_message
    if not r:
        await message.err("Reply To Media, dear.")
    if not (r.audio or r.document or r.video or r.video_note or r.voice):
        await message.err("Not Supported Extension")
    else:
        replied_media = await message.client.download_media(
            message=message.reply_to_message,
            file_name="userge/xcache/merge/",
            progress=progress,
            progress_args=(message, "`Saving for further merge !`"),
        )
        await message.edit(f"Saved in {safe_filename(replied_media)}")


@userge.on_cmd(
    "merge",
    about={
        "header": "Merge Media.",
        "usage": "perform {tr}merge after saving videos with {tr}mergesave",
    },
)
async def merge_(message: Message):
    """Merge Media."""
    name_ = message.input_str
    # preparing text file.
    await message.edit("`🙂🙃 Preparing text file ...`")
    txt_file = codecs.open("merge.txt", "w+", "utf-8")
    for media in os.listdir("userge/xcache/merge"):
        data_ = "file" + " " + "'" + "userge/xcache/merge/" + media + "'" + "\n"
        txt_file.write(data_)
    txt_file.close()
    # detecting extension.
    await message.edit("`😎🥲 detecting extension ...`")
    for ext in os.listdir("userge/xcache/merge")[:1]:
        rege_x = re.findall("[^.]*$", ext)[0]
        await message.edit(f"detected extension is .{rege_x}")
    # custom name.
    if name_:
        output_path = "userge/xcache/merge/" + name_ + "." + rege_x
    else:
        output_path = "userge/xcache/merge/output." + rege_x
    # ffmpeg.
    await message.edit("`🏃️🏃🏃 ffmpeg ...`")
    logs_ = await runcmd(
        f"""ffmpeg -f concat -safe 0 -i merge.txt -map 0 -c copy -scodec copy {output_path}"""
    )
    # upload.
    try:
        await upload(message, Path(output_path))
    except (NullStreamError, InputStreamError):
        await message.err("Something went south generating ffmpeg log file.")
        await message.reply(logs_)
    else:
        await message.edit("`successfully merged ...`")
    # cleanup.
    await message.edit("`🤯😪 cleaning mess ...`", del_in=10)
    shutil.rmtree("userge/xcache/merge")
    os.remove("merge.txt")


@userge.on_cmd(
    "mergeclear",
    about={
        "header": "Incase you saved wrong media",
        "usage": "{tr}mergeclear",
    },
)
async def mergeclear_(message: Message):
    """Clear Saved."""
    try:
        shutil.rmtree("userge/xcache/merge", ignore_errors=True)
    except FileNotFoundError:
        await message.err("already cleared")
    else:
        await message.edit("`cleared ...`", del_in=6)
