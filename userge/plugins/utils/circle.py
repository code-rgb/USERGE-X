import os
from pymediainfo import MediaInfo
from userge import userge, Message

PATH = 'downloads/temp_vid.mp4'

@userge.on_cmd("circle", about={
    'header': "Convert media to video note",
    'usage': "{tr}circle [reply to video / gif]"})
async def video_note(message: Message):
    """ Covert to video note """
    reply = message.reply_to_message
    if not reply:
        await message.err('Reply to supported media', del_in=10)
        return
    if not (reply.video or reply.animation):
        await message.err('Only videos and gifs are Supported', del_in=10)
        return
    process = await message.reply('`Processing ...`')
    note = await reply.download()
    media_info = MediaInfo.parse(note)
    for track in media_info.tracks:
        if track.track_type == 'Video':
            aspect_ratio = track.display_aspect_ratio
            height = track.height
            width = track.width
    if not aspect_ratio == 1:
        crop_by = width if (height > width) else height
        os.system(f'ffmpeg -i {note} -vf "crop={crop_by}:{crop_by}" {PATH}')
        os.remove(note)
    else:
        os.rename(note, PATH) 
    if os.path.exists(PATH):
        is_video = await message.reply_video_note(PATH)
        if is_video.video:
            await message.reply("Media size is greater than allowed video note size")
        os.remove(PATH)
        await process.delete()