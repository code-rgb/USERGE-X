import nekos
import asyncio
from userge import userge, Message


@userge.on_cmd("(neko|lewd|smug|tits|trap|anal|cuddle|hug|goose|waifu|gasm|slap|spank|feet|woof|baka)$", about={
    'header': "For pics",
    'usage': "{tr}neko or {tr}lewd etc.",
    'examples': "neko, lewd, smug, tits, trap, anal, cuddle, hug, goose, waifu, gasm, slap, spank, feet, woof, baka"},name="neko_pic")
async def neko_choices_(message: Message):
    """Gets you a pic"""
    neko_choice = message.matches[0].group(1).lower()
    edit_m = "<code>Getting you some pics for: </code>"
    edit_m += neko_choice
    await message.edit(edit_m, parse_mode='html')
    await asyncio.sleep(1)
    path = nekos.img(neko_choice)
    chat_id = message.chat.id
    message_id = None
    if message.reply_to_message:
        message_id = message.reply_to_message.message_id
    await message.delete()
    await message.client.send_photo(chat_id=chat_id,
                                    photo=path,
                                    reply_to_message_id=message_id)

@userge.on_cmd("(random_hentai_gif|solog|feetg|cum|les|ngif|tickle|feed|bj|nsfw_neko_gif|poke|anal|pussy|pwankg|classic|kuni|kiss|spank|cuddle|baka|hug)$", about={
    'header': "For gifs",
    'usage': "{tr}random_hentai_gif or {tr}poke etc.",
    'examples': "random_hentai_gif, solog, feetg, cum, les, ngif, tickle, feed, bj, nsfw_neko_gif, poke, anal, pussy, pwankg, classic, kuni, kiss, spank, cuddle, baka, hug"}, name="neko_gif")
async def neko_gif_(message: Message):
    """Gets you a gif"""
    neko_gchoice = message.matches[0].group(1).lower()
    edit_m = "<code>Getting you some Gif for: </code>"
    edit_m += neko_gchoice
    await message.edit(edit_m, parse_mode='html')
    await asyncio.sleep(1)
    path = nekos.img(neko_gchoice)
    chat_id = message.chat.id
    message_id = None
    if message.reply_to_message:
        message_id = message.reply_to_message.message_id
    await message.delete()
    await message.client.send_animation(chat_id=chat_id,
                                    animation=path,
                                    reply_to_message_id=message_id)




