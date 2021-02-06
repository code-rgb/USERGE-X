""" Invert, flip/mirror, rotate or spin"""

#  Copyright (C) 2020 BY USERGE-X
#  All rights reserved.
#
#  Authors: 1. https://github.com/code-rgb [TG: @DeletedUser420]
#           2. https://github.com/midnightmadwalk [TG: @MidnightMadwalk] for 🌀 Spin


import os
from shutil import rmtree

from PIL import Image, ImageOps
from userge import Config, Message, userge
from userge.plugins.utils.circle import crop_vid
from userge.utils import media_to_image, runcmd, safe_filename


@userge.on_cmd(
    "(invert|mirror|flip)$",
    about={
        "header": "Invert, Mirror or Flip any media",
        "usage": "{tr}invert [reply to any media]\n"
        "{tr}mirror [reply to any media]\n"
        "{tr}flip [reply to any media]",
    },
    name="transform",
)
async def transform(message: Message):
    replied = message.reply_to_message
    if not replied:
        await message.err("<code>Give Me Something to transform (¬_¬)</code>")
        await message.client.send_sticker(
            sticker="CAADAQADhgADwKwII4f61VT65CNGFgQ", chat_id=message.chat.id
        )
        return
    transform_choice = message.matches[0].group(1).lower()
    choice_string = transform_choice.capitalize()
    await message.edit(f"<code>{choice_string}ing Media!...</code>")
    dls_loc = await media_to_image(message)
    if not dls_loc:
        return
    webp_file = await transform_media(dls_loc, transform_choice)
    await message.client.send_sticker(
        chat_id=message.chat.id,
        sticker=webp_file,
        reply_to_message_id=replied.message_id,
    )
    await message.delete()
    os.remove(webp_file)


async def transform_media(image_path, transform_choice):
    im = Image.open(image_path)
    os.remove(image_path)
    if im.mode != "RGB":
        im = im.convert("RGB")
    if transform_choice == "flip":
        out = ImageOps.flip(im)
    elif transform_choice == "invert":
        out = ImageOps.invert(im)
    else:
        out = im.transpose(Image.FLIP_LEFT_RIGHT)
    image_name = "invert.webp"
    webp_file = os.path.join(Config.DOWN_PATH, image_name)
    out.save(webp_file, "WebP")
    return webp_file


@userge.on_cmd(
    "rotate",
    about={
        "header": "Rotate any media",
        "usage": "{tr}rotate [angle to rotate] [reply to media]\n"
        "angle = 0 to 360(default is 90)",
    },
)
async def rotate_(message: Message):
    """Rotate any media"""
    replied = message.reply_to_message
    if not replied:
        await message.err("<code>Give Me Something to Rotate (¬_¬)</code>")
        await message.client.send_sticker(
            sticker="CAADAQADhgADwKwII4f61VT65CNGFgQ", chat_id=message.chat.id
        )
        return
    if message.input_str:
        input_ = int(message.input_str)
        if not message.input_str.isdigit():
            await message.err("```You input is invalid, check help...```", del_in=5)
            return
        if not 0 < input_ < 360:
            await message.err("```Invalid Angle...```", del_in=5)
            return
        args = input_
    else:
        args = 90
    await message.edit(f"<code>Rotating Media by {args}°...</code>")
    dls_loc = await media_to_image(message)
    if not dls_loc:
        return
    webp_file = await rotate_media(dls_loc, args)
    await message.client.send_sticker(
        chat_id=message.chat.id,
        sticker=webp_file,
        reply_to_message_id=replied.message_id,
    )
    await message.delete()
    os.remove(webp_file)


@userge.on_cmd(
    "spin",
    about={
        "header": "Brr... 🌀",
        "flags": {
            "-s": "Speed -> 1-6",
            "-c": "Spin Clockwise",
            "-r": "for round video",
        },
        "description": "Reply to any media to spin",
        "usage": "{tr}spin [flags] [reply to media]",
        "examples": [
            "{tr}spin",
            "{tr}spin -s4 -c -r",
        ],
    },
)
async def spinn(message: Message):
    """Spin any media"""
    reply = message.reply_to_message
    if not reply:
        return await message.err("Reply To Media First !", del_in=5)
    if (
        message.chat.type in ["group", "supergroup"]
        and not message.chat.permissions.can_send_animations
    ):
        return await message.err(
            "can't send gif in this chat, Permission Denied !", del_in=5
        )
    # to choose no. of frames i.e step_dict[6] or 60 => 360 / 60 = 6 frames
    step_dict = {"1": 1, "2": 3, "3": 6, "4": 12, "5": 24, "6": 60}
    if "-s" in message.flags:
        step = step_dict.get(message.flags["-s"])
        if not step:
            return await message.err("Not valid value for flag '-s'", del_in=5)
    else:
        step = 1
    # Haha USERGE-X custom function
    pic_loc = safe_filename(await media_to_image(message))
    if not pic_loc:
        return await message.err("Reply to a valid media first", del_in=5)
    await message.edit("🌀 `Tighten your seatbelts, sh*t is about to get wild ...`")
    # direction of rotation
    spin_dir = -1 if "-c" in message.flags else 1
    path = "userge/xcache/rotate-disc/"
    if os.path.exists(path):
        rmtree(path, ignore_errors=True)
    os.mkdir(path)
    # Converting RGBA to RGB
    im = Image.open(pic_loc)
    if im.mode != "RGB":
        im = im.convert("RGB")
    # Rotating pic by given angle and saving
    for k, nums in enumerate(range(1, 360, step), start=0):
        y = im.rotate(nums * spin_dir)
        y.save(os.path.join(path, "spinx%s.jpg" % k))

    output_vid = os.path.join(path, "out.mp4")
    # ;__; Maths lol, y = mx + c
    frate = int(((90 / 59) * step) + (1680 / 59))
    # https://stackoverflow.com/questions/20847674/ffmpeg-libx264-height-not-divisible-by-2
    await runcmd(
        f'ffmpeg -framerate {frate} -i {path}spinx%d.jpg -c:v libx264 -preset ultrafast -vf "crop=trunc(iw/2)*2:trunc(ih/2)*2" -pix_fmt yuv420p {output_vid}'
    )
    if os.path.exists(output_vid):
        reply_id = reply.message_id if reply else None
        if "-r" in message.flags:
            round_vid = os.path.join(path, "out_round.mp4")
            # aspect ratio = 1:1
            await crop_vid(output_vid, round_vid)
            await message.client.send_video_note(
                message.chat.id, round_vid, reply_to_message_id=reply_id
            )
        else:
            await message.client.send_animation(
                message.chat.id,
                output_vid,
                unsave=(not message.client.is_bot),
                reply_to_message_id=reply_id,
            )
        await message.delete()
    # Clean up
    os.remove(pic_loc)
    rmtree(path, ignore_errors=True)


async def rotate_media(image_path, args):
    im = Image.open(image_path)
    os.remove(image_path)
    if im.mode != "RGB":
        im = im.convert("RGB")
    angle = args
    out = im.rotate(angle, expand=True)
    image_name = "rotated.webp"
    webp_file = os.path.join(Config.DOWN_PATH, image_name)
    out.save(webp_file, "WebP")
    return webp_file
