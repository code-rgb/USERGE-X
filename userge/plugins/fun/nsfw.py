import os
import urllib
import requests
import asyncio
from asyncio import sleep
from userge import userge , Message, Config
from pyrogram.types import CallbackQuery, InputMediaPhoto
from pyrogram import filters
from userge.utils import get_file_id_and_ref



async def age_verification(msg):
    bot = await userge.bot.get_me()
    x = await userge.get_inline_bot_results(bot.username, "age_verification_alert")
    await msg.delete()
    await userge.send_inline_bot_result(
        chat_id=msg.chat.id,
        query_id=x.query_id,
        result_id=x.results[0].id
    )


@userge.on_cmd("boobs", about={
    'header': "Find some Bob",
    'usage': "{tr}boobs"})
async def boobs(message: Message):
    if not Config.ALLOW_NSFW:
        await age_verification(message)
        return
    if not os.path.isdir(Config.DOWN_PATH):
        os.makedirs(Config.DOWN_PATH)
    pic_loc = os.path.join(Config.DOWN_PATH, "bobs.jpg")
    await message.edit("`Finding some big bobs 🧐...`")
    await asyncio.sleep(0.5)
    await message.edit("`Sending some big bobs 🌚...`")
    nsfw = requests.get('http://api.oboobs.ru/noise/1').json()[0]["preview"]
    urllib.request.urlretrieve("http://media.oboobs.ru/{}".format(nsfw), pic_loc)
    await message.client.send_photo(message.chat.id, photo=pic_loc)
    os.remove(pic_loc)
    await message.delete()

@userge.on_cmd("butts", about={
    'header': "Find some Butts",
    'usage': "{tr}butts"})
async def butts(message: Message):
    if not Config.ALLOW_NSFW:
        await age_verification(message)
        return
    if not os.path.isdir(Config.DOWN_PATH):
        os.makedirs(Config.DOWN_PATH)
    pic_loc = os.path.join(Config.DOWN_PATH, "bobs.jpg")
    await message.edit("`Finding some beautiful butts 🧐...`")
    await asyncio.sleep(0.5)
    await message.edit("`Sending some beautiful butts 🌚...`")
    nsfw = requests.get('http://api.obutts.ru/noise/1').json()[0]["preview"]
    urllib.request.urlretrieve("http://media.obutts.ru/{}".format(nsfw), pic_loc)
    await message.client.send_photo(message.chat.id, photo=pic_loc)
    os.remove(pic_loc)
    await message.delete()


if Config.BOT_TOKEN and Config.OWNER_ID:
    if Config.HU_STRING_SESSION:
        ubot = userge.bot
    else:
        ubot = userge

       
    @ubot.on_callback_query(filters.regex(pattern=r"^age_verification_true"))
    async def alive_callback(_, c_q: CallbackQuery):
        u_id = c_q.from_user.id
        if not (u_id == Config.OWNER_ID or u_id in Config.SUDO_USERS):
            return await c_q.answer("Given That It\'s A Stupid-Ass Decision, I\'ve Elected To Ignore It.", show_alert=True)
        await c_q.answer("I Have Had It With These Motherf*Cking Snakes On This Motherf*Cking Plane!", show_alert=False)
        msg = await ubot.get_messages('useless_x' , 19)
        f_id, f_ref = get_file_id_and_ref(msg)
        await c_q.edit_message_media(
            media=InputMediaPhoto(
                        media=f_id,
                        file_ref=f_ref,
                        caption="Set <code>ALLOW_NSFW</code> = true in Heroku Vars"
                    )
        )

    @ubot.on_callback_query(filters.regex(pattern=r"^age_verification_false"))
    async def alive_callback(_, c_q: CallbackQuery):
        u_id = c_q.from_user.id
        if not (u_id == Config.OWNER_ID or u_id in Config.SUDO_USERS):
            return await c_q.answer("Given That It\'s A Stupid-Ass Decision, I\'ve Elected To Ignore It.", show_alert=True)
        await c_q.answer("I Have Had It With These Motherf*Cking Snakes On This Motherf*Cking Plane!", show_alert=False)
        msg = await ubot.get_messages('useless_x' , 18)
        f_id, f_ref = get_file_id_and_ref(msg)
        img_text="Samuel L. Jackson Says GO AWAY KID !"
        await c_q.edit_message_media(
            media=InputMediaPhoto(
                        media=f_id,
                        file_ref=f_ref,
                        caption=img_text
                    )
        )
        