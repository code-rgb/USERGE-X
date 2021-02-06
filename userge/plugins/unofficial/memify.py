import os
import textwrap

from PIL import Image, ImageDraw, ImageFont
from userge import Config, Message, userge
from userge.utils import media_to_image


@userge.on_cmd(
    "mmf",
    about={
        "header": "Memify aka Geyify (๑¯ω¯๑)",
        "description": "Write text on any gif/sticker/image. "
        "Top and bottom text are separated by ; \n Naw gu Awey",
        "usage": "{tr}mmf [text on top] ; [text on bottom] as a reply.",
        "examples": "Gwad who needs examples for this",
    },
)
async def memify(message: Message):
    replied = message.reply_to_message
    if not replied:
        await message.err(
            "LMAO no one's gonna help you, if u use .help now then u **Gey**"
        )
        await message.client.send_sticker(
            sticker="CAADAQADhAAD3gkwRviGxMVn5813FgQ", chat_id=message.chat.id
        )
        return

    # Here the Magic happens
    dls_loc = await media_to_image(message)
    # UWU
    if dls_loc:
        webp_file = await draw_meme_text(dls_loc, message.input_str)
        await message.client.send_sticker(
            chat_id=message.chat.id,
            sticker=webp_file,
            reply_to_message_id=replied.message_id,
        )
        await message.delete()
        os.remove(webp_file)


async def draw_meme_text(image_path, text):
    img = Image.open(image_path)
    os.remove(image_path)
    i_width, i_height = img.size
    m_font = ImageFont.truetype(
        "resources/MutantAcademyStyle.ttf", int((70 / 640) * i_width)
    )
    if ";" in text:
        upper_text, lower_text = text.split(";")
    else:
        upper_text = text
        lower_text = ""
    draw = ImageDraw.Draw(img)
    current_h, pad = 10, 5
    if upper_text:
        for u_text in textwrap.wrap(upper_text, width=15):
            u_width, u_height = draw.textsize(u_text, font=m_font)

            draw.text(
                xy=(((i_width - u_width) / 2) - 1, int((current_h / 640) * i_width)),
                text=u_text,
                font=m_font,
                fill=(0, 0, 0),
            )
            draw.text(
                xy=(((i_width - u_width) / 2) + 1, int((current_h / 640) * i_width)),
                text=u_text,
                font=m_font,
                fill=(0, 0, 0),
            )
            draw.text(
                xy=((i_width - u_width) / 2, int(((current_h / 640) * i_width)) - 1),
                text=u_text,
                font=m_font,
                fill=(0, 0, 0),
            )
            draw.text(
                xy=(((i_width - u_width) / 2), int(((current_h / 640) * i_width)) + 1),
                text=u_text,
                font=m_font,
                fill=(0, 0, 0),
            )

            draw.text(
                xy=((i_width - u_width) / 2, int((current_h / 640) * i_width)),
                text=u_text,
                font=m_font,
                fill=(255, 255, 255),
            )
            current_h += u_height + pad
    if lower_text:
        for l_text in textwrap.wrap(lower_text, width=15):
            u_width, u_height = draw.textsize(l_text, font=m_font)

            draw.text(
                xy=(
                    ((i_width - u_width) / 2) - 1,
                    i_height - u_height - int((20 / 640) * i_width),
                ),
                text=l_text,
                font=m_font,
                fill=(0, 0, 0),
            )
            draw.text(
                xy=(
                    ((i_width - u_width) / 2) + 1,
                    i_height - u_height - int((20 / 640) * i_width),
                ),
                text=l_text,
                font=m_font,
                fill=(0, 0, 0),
            )
            draw.text(
                xy=(
                    (i_width - u_width) / 2,
                    (i_height - u_height - int((20 / 640) * i_width)) - 1,
                ),
                text=l_text,
                font=m_font,
                fill=(0, 0, 0),
            )
            draw.text(
                xy=(
                    (i_width - u_width) / 2,
                    (i_height - u_height - int((20 / 640) * i_width)) + 1,
                ),
                text=l_text,
                font=m_font,
                fill=(0, 0, 0),
            )

            draw.text(
                xy=(
                    (i_width - u_width) / 2,
                    i_height - u_height - int((20 / 640) * i_width),
                ),
                text=l_text,
                font=m_font,
                fill=(255, 255, 255),
            )
            current_h += u_height + pad

    image_name = "memify.webp"
    webp_file = os.path.join(Config.DOWN_PATH, image_name)
    img.save(webp_file, "WebP")
    return webp_file
