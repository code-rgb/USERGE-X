import os

from anekos import NekosLifeClient, NSFWImageTags, SFWImageTags
from pyrogram.errors import MediaEmpty
from wget import download

from userge import Message, userge

from .nsfw import age_verification

client = NekosLifeClient()


neko_help = "<b>NSFW</b> :  "
for i in NSFWImageTags.to_list():
    neko_help += f"<code>{i}</code>   "
neko_help += "\n\n<b>SFW</b> :  "
for m in SFWImageTags.to_list():
    neko_help += f"<code>{m}</code>   "


@userge.on_cmd(
    "nekos",
    about={
        "header": "Get NSFW / SFW stuff from nekos.life",
        "flags": {"nsfw": "For random NSFW"},
        "usage": "{tr}nekos\n{tr}nekos -nsfw\n{tr}nekos [Choice]",
        "Choice": neko_help,
    },
)
async def neko_life(message: Message):
    choice = message.input_str
    if "-nsfw" in message.flags:
        if await age_verification(message):
            return
        link = (await client.random_image(nsfw=True)).url
    elif choice:
        input_choice = choice.strip()
        if input_choice in SFWImageTags.to_list():
            link = (await client.image(SFWImageTags[input_choice.upper()])).url
        elif input_choice in NSFWImageTags.to_list():
            link = (await client.image(NSFWImageTags[input_choice.upper()])).url
        else:
            await message.err(
                "Choose a valid Input !, See Help for more info.", del_in=5
            )
            return
    else:
        link = (await client.random_image()).url

    await message.delete()

    try:
        await send_nekos(message, link)
    except MediaEmpty:
        link = download(link)
        await send_nekos(message, link)
        os.remove(link)


async def send_nekos(message: Message, link: str):
    reply = message.reply_to_message
    reply_id = reply.message_id if reply else None
    if link.endswith(".gif"):
        #  Bots can't use "unsave=True"
        bool_unsave = not message.client.is_bot
        await message.client.send_animation(
            chat_id=message.chat.id,
            animation=link,
            unsave=bool_unsave,
            reply_to_message_id=reply_id,
        )
    else:
        await message.client.send_photo(
            chat_id=message.chat.id, photo=link, reply_to_message_id=reply_id
        )
