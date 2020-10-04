import os
import urllib
import requests
import asyncio
from asyncio import sleep
from userge import userge , Message, Config
from pyrogram.types import CallbackQuery, InputMedia
from pyrogram import filters


async def age_verification(msg):
    bot = await userge.bot.get_me()
    x = await userge.get_inline_bot_results(bot.username, "age_verification_alert")
    await mesg.delete()
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

       
    @ubot.on_callback_query(filters.regex(pattern=r"^age_verification_(.*)"))
    async def alive_callback(_, c_q: CallbackQuery):
        choice = c_q.matches[0].group(1)
        u_id = c_q.from_user.id
        if not (u_id == Config.OWNER_ID or u_id in Config.SUDO_USERS):
            return await c_q.answer("Given That It\'s A Stupid-Ass Decision, I\'ve Elected To Ignore It.", show_alert=True)
        await c_q.answer("I Have Had It With These Motherf*Cking Snakes On This Motherf*Cking Plane!", show_alert=True)
        if choice == "true":
            image="resources/samelljackson.jpg"
            img_text="Set <code>ALLOW_NSFW</code> = true in Heroku Vars"
        else:
            image="resources/go_away_kid.jpg"
            img_text="Samuel L. Jackson Says GO AWAY KID !"
        await c_q.edit_message_media(
            InputMedia(
                media=image,
                caption=img_text
            )
        )