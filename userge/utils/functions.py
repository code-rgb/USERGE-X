import asyncio
import html
import os
import random
import re
from uuid import uuid4

from pyrogram import emoji
from pyrogram.errors import FloodWait, MessageNotModified
from pyrogram.types import CallbackQuery

from ..config import Config
from .progress import progress
from .tools import runcmd, take_screen_shot

_EMOJI_REGEXP = None

# For Downloading & Checking Media then Converting to Image.
# RETURNS an "Image".


async def media_to_image(message):
    replied = message.reply_to_message
    if not (
        replied.photo
        or replied.sticker
        or replied.animation
        or replied.video
        or replied.audio
    ):
        await message.err("`Media Type Is Invalid ! See HELP.`")
        return
    if not os.path.isdir(Config.DOWN_PATH):
        os.makedirs(Config.DOWN_PATH)
    await message.edit("`Ah Shit, Here We Go Again ...`")
    dls = await message.client.download_media(
        message=message.reply_to_message,
        file_name=Config.DOWN_PATH,
        progress=progress,
        progress_args=(message, "`Trying to Posses given content`"),
    )
    dls_loc = os.path.join(Config.DOWN_PATH, os.path.basename(dls))
    if replied.sticker and replied.sticker.file_name.endswith(".tgs"):
        await message.edit("Converting Animated Sticker To Image...")
        png_file = os.path.join(Config.DOWN_PATH, "image.png")
        cmd = f"lottie_convert.py --frame 0 -if lottie -of png {dls_loc} {png_file}"
        stdout, stderr = (await runcmd(cmd))[:2]
        os.remove(dls_loc)
        if not os.path.lexists(png_file):
            await message.err("This sticker is Gey, Task Failed Successfully ≧ω≦")
            raise Exception(stdout + stderr)
        dls_loc = png_file
    elif replied.sticker and replied.sticker.file_name.endswith(".webp"):
        stkr_file = os.path.join(Config.DOWN_PATH, "stkr.png")
        os.rename(dls_loc, stkr_file)
        if not os.path.lexists(stkr_file):
            await message.err("```Sticker not found...```")
            return
        dls_loc = stkr_file
    elif replied.animation or replied.video:
        await message.edit("`Converting Media To Image ...`")
        jpg_file = os.path.join(Config.DOWN_PATH, "image.jpg")
        await take_screen_shot(dls_loc, 0, jpg_file)
        os.remove(dls_loc)
        if not os.path.lexists(jpg_file):
            await message.err("This Gif is Gey (｡ì _ í｡), Task Failed Successfully !")
            return
        dls_loc = jpg_file
    elif replied.audio:
        await message.edit("`Trying to Get thumb from the audio ...`")
        jpg_file = os.path.join(Config.DOWN_PATH, "image.jpg")
        song_file = os.path.join(Config.DOWN_PATH, "song.mp3")
        os.rename(dls_loc, song_file)
        await thumb_from_audio(song_file, jpg_file)
        os.remove(song_file)
        if not os.path.lexists(jpg_file):
            await message.err(
                "`This Audio has no thumbnail, Task Failed Successfully ...`"
            )
            return
        dls_loc = jpg_file
    await message.edit("`Almost Done ...`")
    return dls_loc


# https://github.com/carpedm20/emoji/blob/master/emoji/core.py
def get_emoji_regex():
    global _EMOJI_REGEXP
    if not _EMOJI_REGEXP:
        e_list = [
            getattr(emoji, _).encode("unicode-escape").decode("ASCII")
            for _ in dir(emoji)
            if not _.startswith("__")
        ]
        # to avoid re.error excluding char that start with '*'
        e_sort = sorted([__ for __ in e_list if not __.startswith("*")], reverse=True)
        # Sort emojis by length to make sure multi-character emojis are
        # matched first
        pattern_ = "(" + "|".join(e_sort) + ")"
        _EMOJI_REGEXP = re.compile(pattern_)
    return _EMOJI_REGEXP


# Removes Emoji From Text
# RETURNS a "string"
EMOJI_PATTERN = get_emoji_regex()


def deEmojify(inputString: str) -> str:
    """Remove emojis and other non-safe characters from string"""
    return re.sub(EMOJI_PATTERN, "", inputString)


def cleanhtml(raw_html):
    cleanr = re.compile("<.*?>")
    return re.sub(cleanr, "", raw_html)


def escape_markdown(text):
    """Helper function to escape telegram markup symbols."""
    escape_chars = r"\*_`\["
    return re.sub(r"([%s])" % escape_chars, r"\\\1", text)


def mention_html(user_id, name):
    return '<a href="tg://user?id={}">{}</a>'.format(user_id, html.escape(name))


def mention_markdown(user_id, name):
    return "[{}](tg://user?id={})".format(escape_markdown(name), user_id)


async def thumb_from_audio(audio_path, output):
    await runcmd(f"ffmpeg -i {audio_path} -filter:v scale=500:500 -an {output}")


def rand_array(array: list, string: bool = True):
    random_num = random.choice(array)
    return str(random_num) if string else random_num


def rand_key():
    return str(uuid4())[:8]


def check_owner(func):
    async def wrapper(_, c_q: CallbackQuery):
        if c_q.from_user and (
            c_q.from_user.id in Config.OWNER_ID or c_q.from_user.id in Config.SUDO_USERS
        ):
            try:
                await func(c_q)
            except FloodWait as e:
                await asyncio.sleep(e.x + 5)
            except MessageNotModified:
                pass
        else:
            await c_q.answer(
                "Only My Master can Access This !!\n\n     𝘿𝙚𝙥𝙡𝙤𝙮 𝙮𝙤𝙪𝙧 𝙤𝙬𝙣 𝙐𝙎𝙀𝙍𝙂𝙀-𝙓",
                show_alert=True,
            )

    return wrapper


# Make dict keys attribute
class AttributeDict(dict):
    def __getattr__(self, attr):
        return self[attr]

    def __setattr__(self, attr, value):
        self[attr] = value
