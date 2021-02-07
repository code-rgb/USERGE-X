from pyrogram import filters
from pyrogram.errors import MessageNotModified
from pyrogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InputMediaPhoto,
)

from userge import Config, userge
from userge.utils import get_file_id


async def age_verification(msg):
    if Config.ALLOW_NSFW.lower() == "true":
        return False
    bot = await userge.bot.get_me()
    x = await userge.get_inline_bot_results(bot.username, "age_verification_alert")
    await msg.delete()
    await userge.send_inline_bot_result(
        chat_id=msg.chat.id, query_id=x.query_id, result_id=x.results[0].id
    )
    return True


if userge.has_bot:

    @userge.bot.on_callback_query(filters.regex(pattern=r"^age_verification_true"))
    async def age_verification_true(_, c_q: CallbackQuery):
        u_id = c_q.from_user.id
        if u_id not in Config.OWNER_ID and u_id not in Config.SUDO_USERS:
            return await c_q.answer(
                "Given That It's A Stupid-Ass Decision, I've Elected To Ignore It.",
                show_alert=True,
            )
        await c_q.answer("Yes I'm 18+", show_alert=False)
        msg = await userge.bot.get_messages("useless_x", 19)
        f_id = get_file_id(msg)
        buttons = [
            [
                InlineKeyboardButton(
                    text="Unsure / Change of Decision ❔",
                    callback_data="chg_of_decision_",
                )
            ]
        ]
        try:
            await c_q.edit_message_media(
                media=InputMediaPhoto(
                    media=f_id,
                    caption="Set <code>ALLOW_NSFW</code> = True in Heroku Vars to access this plugin",
                ),
                reply_markup=InlineKeyboardMarkup(buttons),
            )
        except MessageNotModified:
            pass

    @userge.bot.on_callback_query(filters.regex(pattern=r"^age_verification_false"))
    async def age_verification_false(_, c_q: CallbackQuery):
        u_id = c_q.from_user.id
        if u_id not in Config.OWNER_ID and u_id not in Config.SUDO_USERS:
            return await c_q.answer(
                "Given That It's A Stupid-Ass Decision, I've Elected To Ignore It.",
                show_alert=True,
            )
        await c_q.answer("No I'm Not", show_alert=False)
        msg = await userge.bot.get_messages("useless_x", 20)
        f_id = get_file_id(msg)
        img_text = "GO AWAY KID !"
        buttons = [
            [
                InlineKeyboardButton(
                    text="Unsure / Change of Decision ❔",
                    callback_data="chg_of_decision_",
                )
            ]
        ]
        try:
            await c_q.edit_message_media(
                media=InputMediaPhoto(media=f_id, caption=img_text),
                reply_markup=InlineKeyboardMarkup(buttons),
            )
        except MessageNotModified:
            return

    @userge.bot.on_callback_query(filters.regex(pattern=r"^chg_of_decision_"))
    async def chg_of_decision_(_, c_q: CallbackQuery):
        u_id = c_q.from_user.id
        if u_id not in Config.OWNER_ID and u_id not in Config.SUDO_USERS:
            return await c_q.answer(
                "Given That It's A Stupid-Ass Decision, I've Elected To Ignore It.",
                show_alert=True,
            )
        await c_q.answer("Unsure", show_alert=False)
        msg = await userge.bot.get_messages("useless_x", 21)
        f_id = get_file_id(msg)
        img_text = "<b>ARE YOU OLD ENOUGH FOR THIS ?</b>"
        buttons = [
            [
                InlineKeyboardButton(
                    text="Yes I'm 18+", callback_data="age_verification_true"
                ),
                InlineKeyboardButton(
                    text="No I'm Not", callback_data="age_verification_false"
                ),
            ]
        ]
        try:
            await c_q.edit_message_media(
                media=InputMediaPhoto(media=f_id, caption=img_text),
                reply_markup=InlineKeyboardMarkup(buttons),
            )
        except MessageNotModified:
            pass
