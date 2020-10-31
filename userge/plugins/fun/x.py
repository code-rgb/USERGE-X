# Source: https://gist.github.com/weihanglo/1e754ec47fdd683a42fdf6a272904535

#  Author 2020 𝚂𝚢𝚗𝚝𝚊𝚡 ░ Σrr♢r <https://github.com/code-rgb>
# For USERGE-X

import os
import random

from PIL import Image, ImageDraw

from userge import Config, Message, userge


@userge.on_cmd(
    "x",
    about={
        "header": "USERGE-X",
        "flags": {"-alt": "To get inverted X", "-ghost": "spooky ghost"},
    },
    check_downpath=True,
)
async def usx_(message: Message):
    if "-alt" in message.flags:
        path = "resources/logo_alt.png"
    elif "-ghost" in message.flags:
        path = "resources/ghosts.png"
    else:
        path = "resources/logo.png"

    replied = message.reply_to_message
    await message.edit("𝐗")
    a = []
    for _ in range(2):
        r = random.randint(0, 255)
        g = random.randint(0, 255)
        b = random.randint(0, 255)
        rgb = (r, g, b)
        a.append(rgb)

    im = Image.open(path)
    gradient = Image.new("RGBA", im.size, color=0)
    draw = ImageDraw.Draw(gradient)

    f_co = a[0]
    t_co = a[1]

    for i, color in enumerate(interpolate(f_co, t_co, im.width * 2)):
        draw.line([(i, 0), (0, i)], tuple(color), width=1)

    # gradient = gradient.resize(im.size)   no need for that
    im_composite = Image.alpha_composite(gradient, im)
    im_composite = im_composite.resize(im_composite.size, Image.ANTIALIAS)
    image_name = "grad_x.webp"
    webp_file = os.path.join(Config.DOWN_PATH, image_name)
    im_composite.save(webp_file, "WebP")
    await message.delete()
    message_id = replied.message_id if replied else None
    await message.client.send_sticker(
        chat_id=message.chat.id, sticker=webp_file, reply_to_message_id=message_id
    )


def interpolate(f_co, t_co, interval):
    det_co = [(t - f) / interval for f, t in zip(f_co, t_co)]
    for i in range(interval):
        yield [round(f + det * i) for f, det in zip(f_co, det_co)]
