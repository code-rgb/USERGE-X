"""Make a video note"""

# by GitHub.com/code-rgb [TG- @DeletedUser420]


import os
from shutil import rmtree

import ujson

from userge import Message, userge
from userge.utils import runcmd, safe_filename, thumb_from_audio

LOG = userge.getLogger(__name__)


@userge.on_cmd(
    "circle",
    about={
        "header": "Convert video / gif / audio to video note",
        "usage": "{tr}circle [reply to media]",
    },
)
async def video_note(message: Message):
    """Covert to video note"""
    _cache_path = "userge/xcache/circle"
    _vid_path = _cache_path + "/temp_vid.mp4"
    reply = message.reply_to_message
    if not reply:
        await message.err("Reply to supported media", del_in=10)
        return
    if not (reply.video or reply.animation or reply.audio):
        await message.err("Only videos, gifs and audio are Supported", del_in=10)
        return
    if os.path.exists(_cache_path):
        rmtree(_cache_path, ignore_errors=True)
    os.mkdir(_cache_path)
    await message.edit("`Processing ...`")
    if reply.video or reply.animation:
        note = safe_filename(await reply.download())
        await crop_vid(note, _vid_path)
    else:
        thumb_loc = _cache_path + "/thumb.jpg"
        audio_loc = _cache_path + "/music.mp3"
        if reply.audio.thumbs:
            audio_thumb = reply.audio.thumbs[0].file_id
            thumb = await userge.download_media(audio_thumb)
        else:
            thumb = None
        music = await reply.download()
        os.rename(music, audio_loc)
        if thumb:
            os.rename(thumb, thumb_loc)
        else:
            await thumb_from_audio(audio_loc, thumb_loc)
        await runcmd(
            f"""ffmpeg -loop 1 -i {thumb_loc} -i {audio_loc} -c:v libx264 -tune stillimage -c:a aac -b:a 192k -vf \"scale=\'iw-mod (iw,2)\':\'ih-mod(ih,2)\',format=yuv420p\" -shortest -movflags +faststart {_vid_path}"""
        )
    if os.path.exists(_vid_path):
        await message.client.send_video_note(message.chat.id, _vid_path)
    await message.delete()
    rmtree(_cache_path, ignore_errors=True)


async def crop_vid(input_vid: str, final_path: str):
    stdout = (await runcmd(f'mediainfo --Output=JSON "{input_vid}"'))[0]
    if stdout is None:
        return
    try:
        out = ujson.loads(stdout)
    except Exception as e:
        LOG.error(str(e))
        return
    correct_aspect = True
    vid_valid = False
    if not (out and out.get("media") and out["media"].get("track")):
        return
    for stream in out["media"].get("track"):
        if stream["@type"] == "Video":
            vid_valid = True
            height_ = int(stream.get("Height", 0))
            width_ = int(stream.get("Width", 0))
            aspect_ratio_ = stream.get("DisplayAspectRatio")
            if aspect_ratio_:
                if aspect_ratio_ == "1":
                    correct_aspect = False
            elif width_ and height_:
                if width_ == height_ != 0:
                    correct_aspect = False
            else:
                return
            break
    if vid_valid:
        if correct_aspect:
            crop_by = min(width_, height_)
            await runcmd(
                f"""ffmpeg -i \'{input_vid}\' -vf \"crop={crop_by}:{crop_by}\" {final_path}"""
            )
            os.remove(input_vid)
        else:
            os.rename(input_vid, final_path)
