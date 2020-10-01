"""Generate Memes"""

# Copyright (C) 2020 By - USERGE-X
# All rights reserved.
# Author - @iTz_Black007 // blacky 
# Impoved by - Github/code-rgb


import asyncio
import json
import requests
from userge import userge, Message, Config
from userge.utils import rand_array


URL = 'https://api.imgflip.com/caption_image'
PATH = 'resources/meme_data.txt'


@userge.on_cmd("gm", about={
    'header': "Get Customized memes",
    'flags': {
        '-m': "To choose a meme template"
    },
    'usage': "{tr}gm -m[number] text1 ; text2\n"
             "{tr}gm text1 ; text2",
    'examples': [
        "{tr}gm Hi ; Hello",
        "{tr}gm [flags] Hi ; Hello"],
    'Memes': "<a href='https://telegra.ph/Meme-Choices-10-01'><b>See MEME List</b></a>"})
async def gen_meme(message: Message):
    """ Memesss Generator """
    if not (Config.IMGFLIP_ID or Config.IMGFLIP_PASS):
        return await message.edit('First get `IMGFLIP_ID` and `IMGFLIP_ID` via **https://imgflip.com/**')
    text = message.filtered_input_str
    if not text:
        await message.err("No input found!", del_in=5)
        return
    if ";" in text:
        text1, text2 = text.split(";", 1)
    else: 
        await message.err("Invalid Input! Check help for more info!", del_in=5)
        return
    view_data = json.load(open(PATH))
    if '-m' in message.flags:
        meme_choice = view_data[int(message.flags['-m'])]
        choice_id  = meme_choice['id']
    else:
        meme_choice = eval(rand_array(view_data))
        choice_id = meme_choice['id']
    await message.edit(f"<code>Generating a meme for ...</code>\n{meme_choice['name']}")
    await asyncio.sleep(3)
    username = Config.IMGFLIP_ID
    password = Config.IMGFLIP_PASS
    reply = message.reply_to_message
    reply_id = reply.message_id if reply else None
    params = {
            'username': username,
            'password': password,
            'template_id': choice_id,
            'text0': text1,
            'text1': text2
            }
    response = requests.request('POST',URL,params=params).json()
    meme_image = response['data']['url']
    if not response['success']:
        return await message.err(f"<code>{response['error_message']}</code>", del_in=5)
    await message.delete()
    await message.client.send_photo(
        chat_id=message.chat.id,
        photo=meme_image,
        reply_to_message_id=reply_id
    )