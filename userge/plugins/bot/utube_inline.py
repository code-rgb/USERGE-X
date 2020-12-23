import os
from urllib.parse import parse_qs, urlencode, urlparse

import ujson
from pyrogram.types import InlineKeyboardButton

from userge import Message, userge
from userge.utils import get_response, rand_key

LOGGER = userge.getLogger(__name__)
CHANNEL = userge.getCLogger(__name__)
BASE_YT_URL = "https://www.youtube.com/watch?v="
YT_SEARCH_API = "http://youtube-scrape.herokuapp.com/api/search?"
PATH = "./userge/xcache/ytsearch.json"


class YT_Search_X:
    def __init__(self):
        if not os.path.exists(PATH):
            d = {}
            ujson.dump(d, open(PATH, "w"))
        self.db = ujson.load(open(PATH))

    def store_(self, rnd_id: str, results: dict):
        self.db[rnd_id] = results
        self.save()

    def save(self):
        with open(PATH, "w") as outfile:
            ujson.dump(self.db, outfile, indent=4)


ytsearch_data = YT_Search_X()


async def get_ytthumb(videoid: str):
    thumb_quality = [
        "maxresdefault.jpg",  # Best quality
        "hqdefault.jpg",
        "sddefault.jpg",
        "mqdefault.jpg",
        "default.jpg",  # Worst quality
    ]
    thumb_link = "https://i.imgur.com/4LwPLai.png"
    for qualiy in thumb_quality:
        link = f"https://i.ytimg.com/vi/{videoid}/{qualiy}"
        r = await get_response.status(link)
        if r == 200:
            thumb_link = link
            break
    return thumb_link


def ytdl_btn_generator(array, code, i_q_id):
    btn = []
    b = []
    for i in array:
        name = f"{i.get('format_note', None)} ({i.get('ext', None)})"
        call_back = f"ytdl{code}|{i.get('format_id', '')}|{i_q_id}"
        b.append(InlineKeyboardButton(name, callback_data=call_back))
        if len(b) == 3:  # no. of columns
            btn.append(b)
            b = []
    if len(b) != 0:
        btn.append(b)  # buttons in the last row
    return btn


def ytsearch_url(query: str):
    return YT_SEARCH_API + urlencode({"q": query})


@userge.on_cmd(
    "iytdl",
    about={
        "header": "ytdl with inline buttons",
        "usage": "{tr}iytdl [URL] or [Reply to URL]",
    },
)
async def iytdl_inline(message: Message):
    reply = message.reply_to_message
    input_url = None
    if message.input_str:
        input_url = message.input_str
    elif reply:
        if reply.text:
            input_url = reply.text
        elif reply.caption:
            input_url = reply.caption

    resp = (await get_response.json(ytsearch_url(input_url)))["results"]
    if len(resp) == 0:
        return
    outdata = await result_formatter(resp[:10])
    ytsearch_data.store_(rand_key(), outdata)
    await message.reply(str(outdata[1]))

    if not input_url:
        return await message.err("Input or reply to a valid youtube URL", del_in=5)

    # bot = await userge.bot.get_me()
    # x = await userge.get_inline_bot_results(bot.username, f"ytdl {input_url.strip()}")
    # y = await userge.send_inline_bot_result(
    #     chat_id=message.chat.id, query_id=x.query_id, result_id=x.results[0].id
    # )


"""
if userge.has_bot:

    @userge.bot.on_callback_query(filters.regex(pattern=r""))
    async def ytdl_callback(_, c_q: CallbackQuery):
        startTime = time()
        
        u_id = c_q.from_user.id
        if u_id not in Config.OWNER_ID and u_id not in Config.SUDO_USERS:
            return await c_q.answer("𝘿𝙚𝙥𝙡𝙤𝙮 𝙮𝙤𝙪𝙧 𝙤𝙬𝙣 𝙐𝙎𝙀𝙍𝙂𝙀-𝙓", show_alert=True)
        # choice_id = c_q.matches[0].group(2)
       
        callback_continue = "Downloading Video Please Wait..."
        callback_continue += f"\n\nFormat Code : {choice_id}"
        await c_q.answer(callback_continue, show_alert=True)
        upload_msg = await userge.send_message(Config.LOG_CHANNEL_ID, "Uploading...")
        yt_code = c_q.matches[0].group(1)
        yt_url = BASE_YT_URL + yt_code
        try:
            await c_q.edit_message_caption(
                caption=(
                    f"Video is now being ⬇️ Downloaded, for progress see:\nLog Channel:  [<b>click here</b>]({upload_msg.link})"
                    f"\n\n🔗  [<b>Link</b>]({yt_url})\n🆔  <b>Format Code</b> : {choice_id}"
                ),
                reply_markup=None,
            )

        retcode = await _tubeDl(yt_url, startTime, choice_id)
        if retcode != 0:
            return await upload_msg.edit(str(retcode))
        _fpath = ""
        for _path in glob.glob(os.path.join(Config.DOWN_PATH, str(startTime), "*")):
            if not _path.lower().endswith((".jpg", ".png", ".webp")):
                _fpath = _path
        if not _fpath:
            await upload_msg.err("nothing found !")
            return
        uploaded_vid = await upload(upload_msg, Path(_fpath), logvid=False)

        refresh_vid = await userge.bot.get_messages(
            Config.LOG_CHANNEL_ID, uploaded_vid.message_id
        )
        f_id, f_ref = get_file_id_and_ref(refresh_vid)
        video_thumb = None
        if refresh_vid.video.thumbs:
            video_thumb = await userge.bot.download_media(
                refresh_vid.video.thumbs[0].file_id
            )
        else:
            video_thumb = download(await get_ytthumb(yt_code))

        await c_q.edit_message_media(
            media=InputMediaVideo(
                media=f_id,
                file_ref=f_ref,
                thumb=video_thumb,
                caption=f"📹  <b>[{uploaded_vid.caption}]({yt_url})</b>",
                supports_streaming=True,
            ),
            reply_markup=None,
        )


@pool.run_in_thread
def _tubeDl(url: list, starttime, uid):
    ydl_opts = {
        "addmetadata": True,
        "geo_bypass": True,
        "nocheckcertificate": True,
        "outtmpl": os.path.join(
            Config.DOWN_PATH, str(starttime), "%(title)s-%(format)s.%(ext)s"
        ),
        "logger": LOGGER,
        "format": f"{uid}+bestaudio/best",
        "writethumbnail": True,
        "prefer_ffmpeg": True,
        "postprocessors": [{"key": "FFmpegMetadata"}],
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        try:
            x = ydl.download([url])
        except DownloadError as e:
            CHANNEL.log(str(e))
            x = None
    return x
"""

#  initial version: http://stackoverflow.com/a/7936523/617185 \
#  by Mikhail Kashkin (http://stackoverflow.com/users/85739/mikhail-kashkin)
#
# Returns Video_ID extracting from the given url of Youtube
# Examples of URLs:
#     Valid:
#     'http://youtu.be/_lOT2p_FCvA',
#     'www.youtube.com/watch?v=_lOT2p_FCvA&feature=feedu',
#     'http://www.youtube.com/embed/_lOT2p_FCvA',
#     'http://www.youtube.com/v/_lOT2p_FCvA?version=3&amp;hl=en_US',
#     'https://www.youtube.com/watch?v=rTHlyTphWP0&index=6&list=PLjeDyYvG6-40qawYNR4juzvSOg-ezZ2a6',
#     'youtube.com/watch?v=_lOT2p_FCvA',
#
#     Invalid:
#     'youtu.be/watch?v=_lOT2p_FCvA'


def get_yt_video_id(url: str):
    if url.startswith(("youtu", "www")):
        url = "http://" + url
    query = urlparse(url)
    if "youtube" in query.hostname:
        if query.path == "/watch":
            return parse_qs(query.query)["v"][0]
        if query.path.startswith(("/embed/", "/v/")):
            return query.path.split("/")[2]
    elif "youtu.be" in query.hostname:
        return query.path[1:]
    else:
        raise ValueError


async def result_formatter(results: list):
    output = {}
    for index, r in enumerate(results, start=1):
        rvid = r["video"]
        thumb = await get_ytthumb(rvid["id"])
        upld = r["uploader"]
        out = f'<a href={rvid["url"]}><b>{rvid["title"]}</b></a>\n'
        out += "<code>{}</code>\n\n".format(rvid["snippet"])
        out += f'<b>❯ Duration:</b> {rvid["duration"]}\n'
        out += f'<b>❯ Views:</b> {rvid["views"]}\n'
        out += f'<b>❯ Upload date:</b> {rvid["upload_date"]}\n'
        out += "<b>❯ Uploader:</b> "
        if upld["verified"]:
            out += "✅ "
        out += f'<a href={upld["url"]}>{upld["username"]}</a>'
        output[index] = {"message": out, "thumb": thumb}
    return output
