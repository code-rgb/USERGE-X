

import datetime
import youtube_dl as ytdl
from pyrogram.types import InlineKeyboardButton, CallbackQuery
from pyrogram import filters
from userge import userge, Config

# LOGGER = userge.getLogger(__name__)

def get_ytthumb(thumb_array):
    thumb_link = (thumb_array.pop())['url']
    if "?" in thumb_link:
        thumb_link = thumb_link.split("?", 1)[0]
    return thumb_link
    

def ytdl_btn_generator(array, code):
        btn = []
        b = []
        for i in array:
            name = f"{i.get('format_note', None)} ({i.get('ext', None)})"
            call_back = f"ytdl{code}|{i.get('format_id', '')}"
            b.append(
               InlineKeyboardButton(name, callback_data=call_back)
            )
            if len(b) == 3:   # no. of columns
                btn.append(b)
                b = []
        if len(b) != 0: 
            btn.append(b)     # buttons in the last row
        return btn


def date_formatter(date_):
    if len(date_) != 8:
        return date_
    year, day, month = date_[:4], date_[4:6], date_[6:]
    x = datetime.datetime(int(year), int(month), int(day))
    return str(x.strftime('%d-%b-%Y'))


if Config.BOT_TOKEN and Config.OWNER_ID:
    if Config.HU_STRING_SESSION:
        ubot = userge.bot
    else:
        ubot = userge

       
    @ubot.on_callback_query(filters.regex(pattern=r"^ytdl(\S+)\|(\d+)$"))
    async def ytdl_callback(_, c_q: CallbackQuery):
        u_id = c_q.from_user.id
        if not (u_id == Config.OWNER_ID or u_id in Config.SUDO_USERS):
            return await c_q.answer("𝘿𝙚𝙥𝙡𝙤𝙮 𝙮𝙤𝙪𝙧 𝙤𝙬𝙣 𝙐𝙎𝙀𝙍𝙂𝙀-𝙓", show_alert=True)
        await c_q.answer("Message Will be Edited Shortly", show_alert=True)
        yt_code = c_q.matches[0].group(1)
        choice_id = c_q.matches[0].group(2)
        await c_q.edit_message_caption(
            caption=f"Youtube Link : https://www.youtube.com/watch?v={yt_code}\n\nFormat Code : {choice_id}",
            reply_markup=None
        )


