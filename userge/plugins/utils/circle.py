"""Make a video note"""

# by GitHub.com/code-rgb [TG- @DeletedUser420]


import os
from shutil import rmtree

from pymediainfo import MediaInfo

from userge import Message, userge
from userge.utils import runcmd, thumb_from_audio

CACHE = "userge/xcache/circle"
PATH = os.path.join(CACHE, "temp_vid.mp4")


@userge.on_cmd(
    "circle",
    about={
        "header": "Convert video / gif / audio to video note",
        "usage": "{tr}circle [reply to media]",
    },
)
async def video_note(message: Message):
    """ Covert to video note """
    reply = message.reply_to_message
    if not reply:
        await message.err("Reply to supported media", del_in=10)
        return
    if not (reply.video or reply.animation or reply.audio):
        await message.err("Only videos, gifs and audio are Supported", del_in=10)
        return
    if os.path.exists(CACHE):
        rmtree(CACHE, ignore_errors=True)
    os.mkdir(CACHE)
    await message.edit("`Processing ...`")
    if reply.video or reply.animation:
        note = await reply.download()
        await crop_vid(note, PATH)
    else:
        thumb_loc = os.path.join(CACHE, "thumb.jpg")
        audio_loc = os.path.join(CACHE, "music.mp3")
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
            f"""ffmpeg -loop 1 -i {thumb_loc} -i {audio_loc} -c:v libx264 -tune stillimage -c:a aac -b:a 192k -vf \"scale=\'iw-mod (iw,2)\':\'ih-mod(ih,2)\',format=yuv420p\" -shortest -movflags +faststart {PATH}"""
        )
    if os.path.exists(PATH):
        await message.client.send_video_note(message.chat.id, PATH)
    await message.delete()
    rmtree(CACHE, ignore_errors=True)


async def crop_vid(input_vid: str, final_path: str):
    media_info = MediaInfo.parse(input_vid)
    for track in media_info.tracks:
        if track.track_type == "Video":
            aspect_ratio = track.display_aspect_ratio
            height = track.height
            width = track.width
    if aspect_ratio != 1:
        crop_by = width if (height > width) else height
        await runcmd(
            f"""ffmpeg -i {input_vid} -vf \"crop={crop_by}:{crop_by}\" {final_path}"""
        )
        os.remove(input_vid)
    else:
        os.rename(input_vid, final_path)
